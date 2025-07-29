#!/usr/bin/env python3

"""Unit tests for CLI main module."""

import pytest
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from argparse import Namespace

from build_send_email.__main__ import cmd_build, cmd_send, cmd_preview, main
from build_send_email.config import EmailConfig


class TestCmdBuild:
    """Test the build command."""

    def test_build_basic_email(self):
        """Test building basic email message."""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            'from_addr': 'config@example.com',
            'to_addrs': 'config-to@example.com'
        }.get(key, default)

        args = Namespace(
            body="Test body content",
            body_pre=None,
            body_post=None,
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test Subject",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('build_send_email.__main__.build_email_message') as mock_build:
            with patch('builtins.print') as mock_print:
                mock_msg = Mock()
                mock_msg.as_string.return_value = "Email content"
                mock_build.return_value = mock_msg

                result = cmd_build(args, config)

                assert result == 0
                mock_build.assert_called_once()
                mock_print.assert_called_with("Email content")

    def test_build_with_stdin_body(self):
        """Test building email with body from stdin."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="-",
            body_pre=None,
            body_post=None,
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('sys.stdin.read', return_value="Body from stdin"):
            with patch('build_send_email.__main__.build_email_message') as mock_build:
                with patch('builtins.print'):
                    mock_build.return_value = Mock()
                    mock_build.return_value.as_string.return_value = "Email"

                    result = cmd_build(args, config)

                    assert result == 0
                    # Check that stdin content was used
                    call_args = mock_build.call_args[1]
                    assert call_args['body_content'] == "Body from stdin"

    def test_build_with_file_body(self):
        """Test building email with body from file."""
        config = Mock()
        config.get.return_value = None

        # Create temp file with body content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Body from file")
            temp_path = f.name

        try:
            args = Namespace(
                body=temp_path,
                body_pre=None,
                body_post=None,
                html=None,
                from_addr="test@example.com",
                to_addrs="recipient@example.com",
                subject="Test",
                cc_addrs=None,
                attachments=None,
                output=None,
                preserve_formatting=False
            )

            with patch('build_send_email.__main__.build_email_message') as mock_build:
                with patch('builtins.print'):
                    mock_build.return_value = Mock()
                    mock_build.return_value.as_string.return_value = "Email"

                    result = cmd_build(args, config)

                    assert result == 0
                    call_args = mock_build.call_args[1]
                    assert call_args['body_content'] == "Body from file"

        finally:
            Path(temp_path).unlink()

    def test_build_with_pre_post_content(self):
        """Test building email with pre/post body content."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="Main body",
            body_pre="Pre content",
            body_post="Post content",
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('build_send_email.__main__.build_email_message') as mock_build:
            with patch('builtins.print'):
                mock_build.return_value = Mock()
                mock_build.return_value.as_string.return_value = "Email"

                result = cmd_build(args, config)

                assert result == 0
                call_args = mock_build.call_args[1]
                expected_body = "Pre content\n\nMain body\n\nPost content"
                assert call_args['body_content'] == expected_body

    def test_build_missing_required_fields(self):
        """Test build command fails with missing from/to addresses."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="Test body",
            body_pre=None,
            body_post=None,
            html=None,
            from_addr=None,
            to_addrs=None,
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('builtins.print') as mock_print:
            result = cmd_build(args, config)

            assert result == 1
            mock_print.assert_called_with("Error: --from and --to are required", file=sys.stderr)

    def test_build_with_output_file(self):
        """Test building email with output to file."""
        config = Mock()
        config.get.return_value = None

        with tempfile.NamedTemporaryFile(delete=False) as f:
            output_path = f.name

        try:
            args = Namespace(
                body="Test body",
                body_pre=None,
                body_post=None,
                html=None,
                from_addr="test@example.com",
                to_addrs="recipient@example.com",
                subject="Test",
                cc_addrs=None,
                attachments=None,
                output=output_path,
                preserve_formatting=False
            )

            with patch('build_send_email.__main__.build_email_message') as mock_build:
                with patch('builtins.print') as mock_print:
                    mock_msg = Mock()
                    mock_msg.as_string.return_value = "Email content"
                    mock_build.return_value = mock_msg

                    result = cmd_build(args, config)

                    assert result == 0
                    mock_print.assert_called_with(f"Email message saved to {output_path}")

                    # Check file was written
                    with open(output_path) as f:
                        content = f.read()
                        assert content == "Email content"

        finally:
            Path(output_path).unlink()

    def test_build_with_preserve_formatting(self):
        """Test building email with preserve_formatting option."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="Line 1\n    Indented line\n\nLine 3",
            body_pre=None,
            body_post=None,
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=True
        )

        with patch('build_send_email.__main__.build_email_message') as mock_build:
            with patch('builtins.print'):
                mock_build.return_value = Mock()
                mock_build.return_value.as_string.return_value = "Email"

                result = cmd_build(args, config)

                assert result == 0
                # Verify preserve_formatting was passed to build_email_message
                call_args = mock_build.call_args[1]
                assert call_args['preserve_formatting'] is True

    def test_build_without_preserve_formatting(self):
        """Test building email without preserve_formatting (default behavior)."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="Test body",
            body_pre=None,
            body_post=None,
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('build_send_email.__main__.build_email_message') as mock_build:
            with patch('builtins.print'):
                mock_build.return_value = Mock()
                mock_build.return_value.as_string.return_value = "Email"

                result = cmd_build(args, config)

                assert result == 0
                # Verify preserve_formatting was passed as False
                call_args = mock_build.call_args[1]
                assert call_args['preserve_formatting'] is False

    def test_build_with_body_pre_file(self):
        """Test building email with body-pre from file."""
        config = Mock()
        config.get.return_value = None

        # Create temp file with pre content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Header from file")
            temp_path = f.name

        try:
            args = Namespace(
                body="Main body",
                body_pre=temp_path,
                body_post=None,
                html=None,
                from_addr="test@example.com",
                to_addrs="recipient@example.com",
                subject="Test",
                cc_addrs=None,
                attachments=None,
                output=None,
                preserve_formatting=False
            )

            with patch('build_send_email.__main__.build_email_message') as mock_build:
                with patch('builtins.print'):
                    mock_build.return_value = Mock()
                    mock_build.return_value.as_string.return_value = "Email"

                    result = cmd_build(args, config)

                    assert result == 0
                    call_args = mock_build.call_args[1]
                    expected_body = "Header from file\n\nMain body"
                    assert call_args['body_content'] == expected_body

        finally:
            Path(temp_path).unlink()

    def test_build_with_body_post_file(self):
        """Test building email with body-post from file."""
        config = Mock()
        config.get.return_value = None

        # Create temp file with post content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Footer from file")
            temp_path = f.name

        try:
            args = Namespace(
                body="Main body",
                body_pre=None,
                body_post=temp_path,
                html=None,
                from_addr="test@example.com",
                to_addrs="recipient@example.com",
                subject="Test",
                cc_addrs=None,
                attachments=None,
                output=None,
                preserve_formatting=False
            )

            with patch('build_send_email.__main__.build_email_message') as mock_build:
                with patch('builtins.print'):
                    mock_build.return_value = Mock()
                    mock_build.return_value.as_string.return_value = "Email"

                    result = cmd_build(args, config)

                    assert result == 0
                    call_args = mock_build.call_args[1]
                    expected_body = "Main body\n\nFooter from file"
                    assert call_args['body_content'] == expected_body

        finally:
            Path(temp_path).unlink()

    def test_build_with_body_pre_post_files(self):
        """Test building email with both body-pre and body-post from files."""
        config = Mock()
        config.get.return_value = None

        # Create temp files
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as pre_file:
            pre_file.write("Header from file")
            pre_path = pre_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as post_file:
            post_file.write("Footer from file")
            post_path = post_file.name

        try:
            args = Namespace(
                body="Main body",
                body_pre=pre_path,
                body_post=post_path,
                html=None,
                from_addr="test@example.com",
                to_addrs="recipient@example.com",
                subject="Test",
                cc_addrs=None,
                attachments=None,
                output=None,
                preserve_formatting=False
            )

            with patch('build_send_email.__main__.build_email_message') as mock_build:
                with patch('builtins.print'):
                    mock_build.return_value = Mock()
                    mock_build.return_value.as_string.return_value = "Email"

                    result = cmd_build(args, config)

                    assert result == 0
                    call_args = mock_build.call_args[1]
                    expected_body = "Header from file\n\nMain body\n\nFooter from file"
                    assert call_args['body_content'] == expected_body

        finally:
            Path(pre_path).unlink()
            Path(post_path).unlink()

    def test_build_with_body_pre_literal_text(self):
        """Test building email with body-pre as literal text (non-existent file)."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="Main body",
            body_pre="Non-existent-file-literal-text",
            body_post=None,
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('build_send_email.__main__.build_email_message') as mock_build:
            with patch('builtins.print'):
                mock_build.return_value = Mock()
                mock_build.return_value.as_string.return_value = "Email"

                result = cmd_build(args, config)

                assert result == 0
                call_args = mock_build.call_args[1]
                expected_body = "Non-existent-file-literal-text\n\nMain body"
                assert call_args['body_content'] == expected_body

    def test_build_with_body_post_literal_text(self):
        """Test building email with body-post as literal text (non-existent file)."""
        config = Mock()
        config.get.return_value = None

        args = Namespace(
            body="Main body",
            body_pre=None,
            body_post="Non-existent-file-literal-text",
            html=None,
            from_addr="test@example.com",
            to_addrs="recipient@example.com",
            subject="Test",
            cc_addrs=None,
            attachments=None,
            output=None,
            preserve_formatting=False
        )

        with patch('build_send_email.__main__.build_email_message') as mock_build:
            with patch('builtins.print'):
                mock_build.return_value = Mock()
                mock_build.return_value.as_string.return_value = "Email"

                result = cmd_build(args, config)

                assert result == 0
                call_args = mock_build.call_args[1]
                expected_body = "Main body\n\nNon-existent-file-literal-text"
                assert call_args['body_content'] == expected_body


class TestCmdSend:
    """Test the send command."""

    def test_send_basic_email(self):
        """Test sending basic email message."""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            'backend': 'smtp',
            'retries': 3
        }.get(key, default)

        args = Namespace(
            message="test.eml",
            backend="smtp",
            dry_run=False,
            retries=None
        )

        mock_msg = Mock()
        mock_msg.__getitem__ = Mock(side_effect=lambda key: {
            'From': 'sender@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test'
        }.get(key))

        mock_backend = Mock()
        mock_backend.send.return_value = {
            "success": True,
            "backend": "smtp",
            "message_id": "test-id"
        }

        with patch('builtins.open', mock_open(read_data="Email content")):
            with patch('build_send_email.__main__.email.parser.Parser') as mock_parser:
                with patch('build_send_email.__main__.create_backend', return_value=mock_backend):
                    with patch('build_send_email.__main__.retry_with_backoff') as mock_retry:
                        with patch('builtins.print') as mock_print:
                            mock_parser_inst = Mock()
                            mock_parser.return_value = mock_parser_inst
                            mock_parser_inst.parsestr.return_value = mock_msg
                            mock_retry.return_value = {"success": True, "backend": "smtp", "message_id": "test-id"}

                            result = cmd_send(args, config)

                            assert result == 0
                            mock_print.assert_any_call("Email sent successfully via smtp")
                            mock_print.assert_any_call("Message ID: test-id")

    def test_send_dry_run(self):
        """Test send command in dry run mode."""
        config = Mock()
        config.get.return_value = "smtp"

        args = Namespace(
            message="test.eml",
            backend="smtp",
            dry_run=True,
            retries=None
        )

        mock_msg = Mock()
        mock_msg.__getitem__ = Mock(side_effect=lambda key: {
            'From': 'sender@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test Subject'
        }.get(key))

        with patch('builtins.open', mock_open(read_data="Email content")):
            with patch('build_send_email.__main__.email.parser.Parser') as mock_parser:
                with patch('build_send_email.__main__.create_backend') as mock_create:
                    with patch('builtins.print') as mock_print:
                        mock_parser_inst = Mock()
                        mock_parser.return_value = mock_parser_inst
                        mock_parser_inst.parsestr.return_value = mock_msg

                        result = cmd_send(args, config)

                        assert result == 0
                        mock_print.assert_any_call("DRY RUN - Would send email:")
                        mock_print.assert_any_call("Backend: smtp")
                        mock_print.assert_any_call("From: sender@example.com")
                        mock_print.assert_any_call("To: recipient@example.com")
                        mock_print.assert_any_call("Subject: Test Subject")
                        mock_create.assert_called_once()  # Backend still created for validation

    def test_send_file_not_found(self):
        """Test send command with missing email file."""
        config = Mock()

        args = Namespace(
            message="nonexistent.eml",
            backend=None,
            dry_run=False,
            retries=None
        )

        with patch('builtins.print') as mock_print:
            result = cmd_send(args, config)

            assert result == 1
            mock_print.assert_called_with(
                "Error: Email file not found: nonexistent.eml",
                file=sys.stderr
            )

    def test_send_backend_creation_error(self):
        """Test send command with backend creation error."""
        config = Mock()
        config.get.return_value = "smtp"

        args = Namespace(
            message="test.eml",
            backend="invalid",
            dry_run=False,
            retries=None
        )

        mock_msg = Mock()

        with patch('builtins.open', mock_open(read_data="Email content")):
            with patch('build_send_email.__main__.email.parser.Parser') as mock_parser:
                with patch('build_send_email.__main__.create_backend') as mock_create:
                    with patch('builtins.print') as mock_print:
                        mock_parser_inst = Mock()
                        mock_parser.return_value = mock_parser_inst
                        mock_parser_inst.parsestr.return_value = mock_msg
                        mock_create.side_effect = ValueError("Unknown backend")

                        result = cmd_send(args, config)

                        assert result == 1
                        mock_print.assert_called_with(
                            "Error creating invalid backend: Unknown backend",
                            file=sys.stderr
                        )

    def test_send_failure(self):
        """Test send command when email sending fails."""
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            'backend': 'smtp',
            'retries': 3
        }.get(key, default)

        args = Namespace(
            message="test.eml",
            backend=None,
            dry_run=False,
            retries=None
        )

        mock_msg = Mock()
        mock_backend = Mock()

        with patch('builtins.open', mock_open(read_data="Email content")):
            with patch('build_send_email.__main__.email.parser.Parser') as mock_parser:
                with patch('build_send_email.__main__.create_backend', return_value=mock_backend):
                    with patch('build_send_email.__main__.retry_with_backoff') as mock_retry:
                        with patch('builtins.print') as mock_print:
                            mock_parser_inst = Mock()
                            mock_parser.return_value = mock_parser_inst
                            mock_parser_inst.parsestr.return_value = mock_msg
                            mock_retry.return_value = {"success": False, "error": "Connection failed"}

                            result = cmd_send(args, config)

                            assert result == 1
                            mock_print.assert_called_with(
                                "Failed to send email: Connection failed",
                                file=sys.stderr
                            )


class TestCmdPreview:
    """Test the preview command."""

    def test_preview_basic_email(self):
        """Test previewing basic email message."""
        config = Mock()

        args = Namespace(message="test.eml")

        mock_msg = Mock()
        mock_msg.__getitem__ = Mock(side_effect=lambda key: {
            'From': 'sender@example.com',
            'To': 'recipient@example.com',
            'Subject': 'Test Subject',
            'Cc': None
        }.get(key))

        mock_body = Mock()
        mock_body.get_content.return_value = "Test email body"
        mock_msg.get_body.return_value = mock_body

        with patch('builtins.open', mock_open(read_data="Email content")):
            with patch('build_send_email.__main__.email.parser.Parser') as mock_parser:
                with patch('builtins.print') as mock_print:
                    mock_parser_inst = Mock()
                    mock_parser.return_value = mock_parser_inst
                    mock_parser_inst.parsestr.return_value = mock_msg

                    result = cmd_preview(args, config)

                    assert result == 0
                    # Check expected output calls
                    expected_calls = [
                        ("=" * 50,),
                        ("EMAIL PREVIEW",),
                        ("=" * 50,),
                        ("From: sender@example.com",),
                        ("To: recipient@example.com",),
                        ("Subject: Test Subject",),
                        ("-" * 50,),
                        ("Test email body",),
                        ("=" * 50,)
                    ]
                    for expected_call in expected_calls:
                        mock_print.assert_any_call(*expected_call)

    def test_preview_file_not_found(self):
        """Test preview command with missing file."""
        config = Mock()
        args = Namespace(message="nonexistent.eml")

        with patch('builtins.print') as mock_print:
            result = cmd_preview(args, config)

            assert result == 1
            mock_print.assert_called_with(
                "Error: Email file not found: nonexistent.eml",
                file=sys.stderr
            )


class TestMain:
    """Test main function and argument parsing."""

    def test_main_no_command(self):
        """Test main function with no command shows help."""
        with patch('sys.argv', ['build-send-email']):
            with patch('build_send_email.__main__.argparse.ArgumentParser.print_help') as mock_help:
                result = main()

                assert result == 1
                mock_help.assert_called_once()

    def test_main_build_command(self):
        """Test main function routes to build command."""
        test_args = [
            'build-send-email', 'build',
            '--from', 'test@example.com',
            '--to', 'recipient@example.com',
            '--subject', 'Test',
            '--body', 'Test body'
        ]

        with patch('sys.argv', test_args):
            with patch('build_send_email.__main__.cmd_build') as mock_build:
                mock_build.return_value = 0
                result = main()

                assert result == 0
                mock_build.assert_called_once()

    def test_main_send_command(self):
        """Test main function routes to send command."""
        test_args = ['build-send-email', 'send', 'test.eml']

        with patch('sys.argv', test_args):
            with patch('build_send_email.__main__.cmd_send') as mock_send:
                mock_send.return_value = 0
                result = main()

                assert result == 0
                mock_send.assert_called_once()

    def test_main_preview_command(self):
        """Test main function routes to preview command."""
        test_args = ['build-send-email', 'preview', 'test.eml']

        with patch('sys.argv', test_args):
            with patch('build_send_email.__main__.cmd_preview') as mock_preview:
                mock_preview.return_value = 0
                result = main()

                assert result == 0
                mock_preview.assert_called_once()

    def test_main_verbose_mode(self):
        """Test main function enables verbose logging."""
        test_args = ['build-send-email', '--verbose', 'preview', 'test.eml']

        with patch('sys.argv', test_args):
            with patch('build_send_email.__main__.logging.basicConfig') as mock_logging:
                with patch('build_send_email.__main__.cmd_preview', return_value=0):
                    main()

                    mock_logging.assert_called_once_with(level=20)  # logging.INFO = 20

    def test_main_version_flag(self):
        """Test main function shows version with --version flag."""
        test_args = ['build-send-email', '--version']

        with patch('sys.argv', test_args):
            # Capture stdout where argparse prints version info
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with pytest.raises(SystemExit) as exc_info:
                    main()

                # argparse exits with code 0 for --version
                assert exc_info.value.code == 0

                # Check that version was printed to stdout
                output = mock_stdout.getvalue()
                assert "build-send-email" in output
                assert "0.0.1" in output
