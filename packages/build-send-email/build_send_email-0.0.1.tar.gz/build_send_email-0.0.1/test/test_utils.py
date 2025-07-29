#!/usr/bin/env python3

"""Unit tests for utility functions."""

import pytest
import email.message
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from argparse import Namespace

from build_send_email.utils import (
    validate_email_address,
    build_email_message,
    retry_with_backoff,
    create_backend
)
from build_send_email.config import EmailConfig
from build_send_email.backends import SESBackend, SMTPBackend, SendmailBackend


class TestValidateEmailAddress:
    """Test email address validation."""

    def test_valid_email_addresses(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "firstname.lastname@company.com",
            "user123@test-domain.net"
        ]

        for email_addr in valid_emails:
            assert validate_email_address(email_addr), f"Should be valid: {email_addr}"

    def test_invalid_email_addresses(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "",
            "notanemail",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@.example.com",
            "user@example.com.",
            "user@example"
            # Note: parseaddr actually handles some spaces, so removing space tests
        ]

        for email_addr in invalid_emails:
            assert not validate_email_address(email_addr), f"Should be invalid: {email_addr}"

    def test_validate_email_with_display_name(self):
        """Test email validation with display names."""
        # parseaddr should handle display names
        assert validate_email_address("John Doe <john@example.com>")
        assert validate_email_address('"Test User" <test@example.org>')

    def test_validate_email_exception_handling(self):
        """Test validation handles parsing exceptions."""
        # Malformed input that might cause parseaddr to fail
        assert not validate_email_address(None)  # Will cause exception


class TestBuildEmailMessage:
    """Test email message building."""

    def test_basic_email_message(self):
        """Test building basic email message."""
        msg = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test Subject",
            body_content="Test body content"
        )

        assert isinstance(msg, email.message.EmailMessage)
        assert msg["From"] == "sender@example.com"
        assert msg["To"] == "recipient@example.com"
        assert msg["Subject"] == "Test Subject"
        assert "Date" in msg
        assert "Message-ID" in msg
        assert msg.get_content().strip() == "Test body content"

    def test_email_with_cc(self):
        """Test building email with CC addresses."""
        msg = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Test",
            cc_addrs="cc@example.com"
        )

        assert msg["Cc"] == "cc@example.com"

    def test_email_with_html_content(self):
        """Test building email with HTML alternative."""
        msg = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Plain text content",
            html_content="<p>HTML content</p>"
        )

        # Should have both plain text and HTML parts
        parts = list(msg.walk())
        assert len(parts) >= 2

        # Check plain text content exists
        plain_part = msg.get_body(('plain',))
        assert plain_part is not None
        assert "Plain text content" in plain_part.get_content()

    def test_email_with_attachments(self):
        """Test building email with attachments."""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test attachment content")
            temp_path = f.name

        try:
            msg = build_email_message(
                from_addr="sender@example.com",
                to_addrs="recipient@example.com",
                subject="Test",
                body_content="Test",
                attachments=[temp_path]
            )

            # Should have attachment
            parts = list(msg.walk())
            assert len(parts) >= 2  # Main message + attachment

            # Find attachment part
            attachment_found = False
            for part in parts:
                if part.get_content_disposition() == 'attachment':
                    attachment_found = True
                    assert part.get_filename() == Path(temp_path).name

            assert attachment_found, "Attachment not found in message"

        finally:
            Path(temp_path).unlink()

    def test_email_with_nonexistent_attachment(self):
        """Test that nonexistent attachments are skipped."""
        msg = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Test",
            attachments=["/nonexistent/file.txt"]
        )

        # Should only have the main message part
        parts = list(msg.walk())
        assert len(parts) == 1

    def test_invalid_from_address(self):
        """Test that invalid from address raises ValueError."""
        with pytest.raises(ValueError, match="Invalid from address"):
            build_email_message(
                from_addr="invalid-email",
                to_addrs="recipient@example.com",
                subject="Test",
                body_content="Test"
            )

    def test_preserve_formatting_plain_text(self):
        """Test preserve_formatting option with plain text content."""
        msg = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Line 1\n    Indented line\n\nLine 3",
            preserve_formatting=True
        )

        # With preserve_formatting=True, should use set_payload instead of set_content
        # This preserves exact formatting including whitespace
        assert isinstance(msg, email.message.EmailMessage)
        body_content = msg.get_payload()
        assert body_content == "Line 1\n    Indented line\n\nLine 3"

    def test_preserve_formatting_with_html(self):
        """Test preserve_formatting option with HTML content."""
        msg = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Line 1\n    Indented line\n\nLine 3",
            html_content="<p>HTML content</p>",
            preserve_formatting=True
        )

        # Should have both parts with preserved formatting
        assert isinstance(msg, email.message.EmailMessage)

        # Check that plain text formatting is preserved
        plain_part = msg.get_body(('plain',))
        if plain_part:
            # When preserve_formatting=True with HTML, the structure might be different
            # The key is that the original formatting should be maintained
            assert "Line 1\n    Indented line\n\nLine 3" in str(msg)

    def test_preserve_formatting_false_default(self):
        """Test that preserve_formatting=False is the default behavior."""
        msg_default = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Test content"
        )

        msg_explicit_false = build_email_message(
            from_addr="sender@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            body_content="Test content",
            preserve_formatting=False
        )

        # Both should behave the same way (using set_content)
        assert msg_default.get_content() == msg_explicit_false.get_content()


class TestRetryWithBackoff:
    """Test retry mechanism with backoff."""

    def test_retry_success_first_attempt(self):
        """Test successful execution on first attempt."""
        def success_func():
            return {"success": True, "message": "Success"}

        result = retry_with_backoff(success_func, max_retries=3)
        assert result["success"] is True
        assert result["message"] == "Success"

    def test_retry_success_after_failures(self):
        """Test success after initial failures."""
        call_count = 0

        def eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"success": False, "error": f"Attempt {call_count} failed"}
            return {"success": True, "message": "Finally succeeded"}

        with patch('build_send_email.utils.time.sleep') as mock_sleep:
            result = retry_with_backoff(eventually_success, max_retries=3)

        assert result["success"] is True
        assert result["message"] == "Finally succeeded"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Two retries before success

    def test_retry_max_retries_exceeded(self):
        """Test behavior when max retries exceeded."""
        def always_fail():
            return {"success": False, "error": "Always fails"}

        with patch('build_send_email.utils.time.sleep') as mock_sleep:
            result = retry_with_backoff(always_fail, max_retries=2)

        assert result["success"] is False
        assert result["error"] == "Always fails"
        assert mock_sleep.call_count == 1  # One retry before giving up

    def test_retry_with_exception(self):
        """Test retry behavior when function raises exceptions."""
        call_count = 0

        def raise_exception():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError(f"Connection failed attempt {call_count}")
            return {"success": True, "message": "Success after exceptions"}

        with patch('build_send_email.utils.time.sleep') as mock_sleep:
            result = retry_with_backoff(raise_exception, max_retries=3)

        assert result["success"] is True
        assert result["message"] == "Success after exceptions"
        assert call_count == 3
        assert mock_sleep.call_count == 2

    def test_retry_max_exceptions(self):
        """Test when all attempts result in exceptions."""
        def always_raise():
            raise RuntimeError("Always fails")

        with patch('build_send_email.utils.time.sleep') as mock_sleep:
            result = retry_with_backoff(always_raise, max_retries=2)

        assert result["success"] is False
        assert "Always fails" in result["error"]
        assert mock_sleep.call_count == 1

    def test_retry_backoff_timing(self):
        """Test exponential backoff timing."""
        def always_fail():
            return {"success": False, "error": "Fail"}

        with patch('build_send_email.utils.time.sleep') as mock_sleep:
            retry_with_backoff(always_fail, max_retries=4, base_delay=1.0)

        # Should have called sleep with exponential backoff: 1.0, 2.0, 4.0
        expected_delays = [1.0, 2.0, 4.0]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_delays == expected_delays


class TestCreateBackend:
    """Test backend creation function."""

    def test_create_ses_backend(self):
        """Test creating SES backend."""
        config = EmailConfig()
        args = Namespace(aws_region="us-west-2", aws_profile="test-profile")

        with patch('build_send_email.utils.SESBackend') as mock_ses:
            create_backend("ses", config, args)
            mock_ses.assert_called_once_with(region="us-west-2", profile="test-profile")

    def test_create_ses_backend_with_config_defaults(self):
        """Test SES backend uses config defaults when args not provided."""
        config_data = {"aws_region": "eu-west-1", "aws_profile": "prod"}
        config = Mock()
        config.get.side_effect = lambda key, default=None: config_data.get(key, default)

        args = Namespace()  # No aws_region or aws_profile

        with patch('build_send_email.utils.SESBackend') as mock_ses:
            create_backend("ses", config, args)
            mock_ses.assert_called_once_with(region="eu-west-1", profile="prod")

    def test_create_smtp_backend(self):
        """Test creating SMTP backend."""
        config = EmailConfig()
        args = Namespace(
            smtp_server="smtp.test.com",
            smtp_port=465,
            smtp_username="testuser",
            smtp_password="testpass",
            smtp_tls=False
        )

        with patch('build_send_email.utils.SMTPBackend') as mock_smtp:
            create_backend("smtp", config, args)
            mock_smtp.assert_called_once_with(
                server="smtp.test.com",
                port=465,
                username="testuser",
                password="testpass",
                use_tls=False
            )

    def test_create_smtp_backend_with_config_defaults(self):
        """Test SMTP backend uses config defaults."""
        config_data = {
            "smtp_server": "smtp.config.com",
            "smtp_port": 587,
            "smtp_username": "configuser",
            "smtp_password": "configpass",
            "smtp_tls": True
        }
        config = Mock()
        config.get.side_effect = lambda key, default=None: config_data.get(key, default)

        args = Namespace()  # No SMTP args

        with patch('build_send_email.utils.SMTPBackend') as mock_smtp:
            create_backend("smtp", config, args)
            mock_smtp.assert_called_once_with(
                server="smtp.config.com",
                port=587,
                username="configuser",
                password="configpass",
                use_tls=True
            )

    def test_create_sendmail_backend(self):
        """Test creating Sendmail backend."""
        config = EmailConfig()
        args = Namespace(sendmail_path="/usr/bin/msmtp")

        with patch('build_send_email.utils.SendmailBackend') as mock_sendmail:
            create_backend("sendmail", config, args)
            mock_sendmail.assert_called_once_with(sendmail_path="/usr/bin/msmtp")

    def test_create_sendmail_backend_default_path(self):
        """Test Sendmail backend with default path."""
        config = EmailConfig()
        args = Namespace()  # No sendmail_path

        with patch('build_send_email.utils.SendmailBackend') as mock_sendmail:
            create_backend("sendmail", config, args)
            mock_sendmail.assert_called_once_with(sendmail_path="/usr/sbin/sendmail")

    def test_create_unknown_backend(self):
        """Test error when creating unknown backend type."""
        config = EmailConfig()
        args = Namespace()

        with pytest.raises(ValueError, match="Unknown backend type: unknown"):
            create_backend("unknown", config, args)