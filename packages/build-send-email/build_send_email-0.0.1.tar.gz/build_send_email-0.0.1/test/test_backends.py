#!/usr/bin/env python3

"""Unit tests for email backends."""

import pytest
import email.message
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from build_send_email.backends import EmailBackend, SESBackend, SMTPBackend, SendmailBackend


class TestEmailBackend:
    """Test the base EmailBackend class."""

    def test_base_backend_send_not_implemented(self):
        """Test that base backend raises NotImplementedError."""
        backend = EmailBackend()
        msg = email.message.EmailMessage()

        with pytest.raises(NotImplementedError):
            backend.send(msg)


class TestSESBackend:
    """Test the SES backend."""

    def test_ses_backend_requires_boto3(self):
        """Test SES backend fails without boto3."""
        with patch('build_send_email.backends.HAS_BOTO3', False):
            with pytest.raises(ImportError, match="boto3 is required"):
                SESBackend()

    @patch('build_send_email.backends.HAS_BOTO3', True)
    @patch('build_send_email.backends.boto3')
    def test_ses_backend_initialization(self, mock_boto3):
        """Test SES backend initialization."""
        mock_session = Mock()
        mock_client = Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        backend = SESBackend(region="us-west-2", profile="test-profile")

        assert backend.region == "us-west-2"
        assert backend.profile == "test-profile"
        assert backend.client == mock_client
        mock_boto3.Session.assert_called_once_with(profile_name="test-profile")
        mock_session.client.assert_called_once_with("ses", region_name="us-west-2")

    @patch('build_send_email.backends.HAS_BOTO3', True)
    @patch('build_send_email.backends.boto3')
    def test_ses_backend_send_success(self, mock_boto3):
        """Test successful SES email sending."""
        mock_session = Mock()
        mock_client = Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        # Mock successful SES response
        mock_client.build_send_email.return_value = {"MessageId": "test-message-id"}

        backend = SESBackend()

        # Create test email
        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Test Subject"
        msg.set_content("Test body")

        result = backend.send(msg)

        assert result["success"] is True
        assert result["message_id"] == "test-message-id"
        assert result["backend"] == "ses"

        # Verify SES API call
        mock_client.build_send_email.assert_called_once()
        call_args = mock_client.build_send_email.call_args[1]
        assert call_args["Source"] == "sender@example.com"
        assert "recipient@example.com" in call_args["Destination"]["ToAddresses"]

    @patch('build_send_email.backends.HAS_BOTO3', True)
    @patch('build_send_email.backends.boto3')
    def test_ses_backend_send_failure(self, mock_boto3):
        """Test SES backend handles errors properly."""
        mock_session = Mock()
        mock_client = Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        # Mock SES error - use a botocore ClientError
        from botocore.exceptions import ClientError
        error = ClientError(
            error_response={'Error': {'Code': 'SendingQuotaExceeded', 'Message': 'SES API Error'}},
            operation_name='SendEmail'
        )
        mock_client.build_send_email.side_effect = error

        backend = SESBackend()
        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is False
        assert "SES API Error" in result["error"]
        assert result["backend"] == "ses"


class TestSMTPBackend:
    """Test the SMTP backend."""

    def test_smtp_backend_initialization(self):
        """Test SMTP backend initialization with default values."""
        backend = SMTPBackend("smtp.example.com")

        assert backend.server == "smtp.example.com"
        assert backend.port == 587
        assert backend.username is None
        assert backend.password is None
        assert backend.use_tls is True

    def test_smtp_backend_initialization_custom(self):
        """Test SMTP backend initialization with custom values."""
        backend = SMTPBackend(
            server="smtp.gmail.com",
            port=465,
            username="user@gmail.com",
            password="secret",
            use_tls=False
        )

        assert backend.server == "smtp.gmail.com"
        assert backend.port == 465
        assert backend.username == "user@gmail.com"
        assert backend.password == "secret"
        assert backend.use_tls is False

    @patch('build_send_email.backends.smtplib.SMTP')
    def test_smtp_backend_send_success(self, mock_smtp):
        """Test successful SMTP email sending."""
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        backend = SMTPBackend("smtp.example.com", 587, "user", "pass")

        # Create test email
        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is True
        assert result["backend"] == "smtp"
        assert result["server"] == "smtp.example.com"

        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("user", "pass")
        mock_smtp_instance.send_message.assert_called_once()

    @patch('build_send_email.backends.smtplib.SMTP')
    def test_smtp_backend_send_no_auth(self, mock_smtp):
        """Test SMTP sending without authentication."""
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        backend = SMTPBackend("smtp.example.com")  # No username/password

        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is True
        mock_smtp_instance.login.assert_not_called()

    @patch('build_send_email.backends.smtplib.SMTP')
    def test_smtp_backend_send_failure(self, mock_smtp):
        """Test SMTP backend handles errors properly."""
        mock_smtp.side_effect = OSError("Connection refused")

        backend = SMTPBackend("smtp.example.com")
        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is False
        assert "Connection refused" in result["error"]
        assert result["backend"] == "smtp"


class TestSendmailBackend:
    """Test the Sendmail backend."""

    def test_sendmail_backend_initialization(self):
        """Test Sendmail backend initialization."""
        backend = SendmailBackend()
        assert backend.sendmail_path == "/usr/sbin/sendmail"

        backend = SendmailBackend("/usr/bin/msmtp")
        assert backend.sendmail_path == "/usr/bin/msmtp"

    def test_sendmail_not_found(self):
        """Test behavior when sendmail binary is not found."""
        backend = SendmailBackend(sendmail_path="/nonexistent/sendmail")

        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is False
        assert "not found" in result["error"]
        assert result["backend"] == "sendmail"

    @patch('build_send_email.backends.Path.exists')
    @patch('build_send_email.backends.subprocess.run')
    def test_sendmail_send_success(self, mock_run, mock_exists):
        """Test successful sendmail sending."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0, stderr="")

        backend = SendmailBackend()

        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is True
        assert result["backend"] == "sendmail"

        # Verify subprocess call
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "/usr/sbin/sendmail"
        assert "recipient@example.com" in args

    @patch('build_send_email.backends.Path.exists')
    @patch('build_send_email.backends.subprocess.run')
    def test_sendmail_send_failure(self, mock_run, mock_exists):
        """Test sendmail handles process errors."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=1, stderr="Sendmail error")

        backend = SendmailBackend()

        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg.set_content("Test")

        result = backend.send(msg)

        assert result["success"] is False
        assert "Sendmail error" in result["error"]
        assert result["backend"] == "sendmail"

    @patch('build_send_email.backends.Path.exists')
    def test_sendmail_no_recipients(self, mock_exists):
        """Test sendmail handles emails with no recipients."""
        mock_exists.return_value = True

        backend = SendmailBackend()

        msg = email.message.EmailMessage()
        msg["From"] = "sender@example.com"
        msg.set_content("Test")
        # No To, CC, or BCC headers

        result = backend.send(msg)

        assert result["success"] is False
        assert "No recipients found" in result["error"]
        assert result["backend"] == "sendmail"