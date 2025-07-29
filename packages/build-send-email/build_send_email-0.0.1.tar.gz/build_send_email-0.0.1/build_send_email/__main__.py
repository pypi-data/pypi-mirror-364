#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

"""Main CLI entry point for build-send-email tool."""

import argparse
import email.parser
import email.policy
import logging
import sys
from pathlib import Path

# Import from focused modules
from .config import EmailConfig
from .utils import build_email_message, create_backend, retry_with_backoff
from . import __version__


def cmd_build(args, config: EmailConfig):
    """Build email message command."""
    # Read body content
    if args.body == '-':
        body_content = sys.stdin.read()
    elif Path(args.body).exists():
        with open(args.body) as f:
            body_content = f.read()
    else:
        body_content = args.body

    # Read and add pre/post content
    if args.body_pre:
        if Path(args.body_pre).exists():
            with open(args.body_pre) as f:
                body_pre_content = f.read()
        else:
            body_pre_content = args.body_pre
        body_content = body_pre_content + "\n\n" + body_content
    
    if args.body_post:
        if Path(args.body_post).exists():
            with open(args.body_post) as f:
                body_post_content = f.read()
        else:
            body_post_content = args.body_post
        body_content = body_content + "\n\n" + body_post_content

    # Read HTML content if provided
    html_content = None
    if args.html:
        if Path(args.html).exists():
            with open(args.html) as f:
                html_content = f.read()
        else:
            html_content = args.html

    # Use config defaults
    from_addr = args.from_addr or config.get('from_addr')
    to_addrs = args.to_addrs or config.get('to_addrs')

    if not from_addr or not to_addrs:
        print("Error: --from and --to are required", file=sys.stderr)
        return 1

    try:
        msg = build_email_message(
            from_addr=from_addr,
            to_addrs=to_addrs,
            subject=args.subject,
            body_content=body_content,
            cc_addrs=args.cc_addrs,
            html_content=html_content,
            attachments=args.attachments,
            preserve_formatting=args.preserve_formatting,
        )

        # Output message
        if args.output:
            with open(args.output, 'w') as f:
                f.write(msg.as_string())
            print(f"Email message saved to {args.output}")
        else:
            print(msg.as_string())

        return 0

    except Exception as e:
        print(f"Error building email: {e}", file=sys.stderr)
        return 1


def cmd_send(args, config: EmailConfig):
    """Send email message command."""
    # Read email message
    if args.message == '-':
        msg_content = sys.stdin.read()
    else:
        try:
            with open(args.message) as f:
                msg_content = f.read()
        except FileNotFoundError:
            print(f"Error: Email file not found: {args.message}", file=sys.stderr)
            return 1

    # Parse message
    try:
        parser = email.parser.Parser(policy=email.policy.default)
        msg = parser.parsestr(msg_content)
    except Exception as e:
        print(f"Error parsing email message: {e}", file=sys.stderr)
        return 1

    # Create backend
    backend_type = args.backend or config.get('backend', 'sendmail')

    try:
        backend = create_backend(backend_type, config, args)
    except Exception as e:
        print(f"Error creating {backend_type} backend: {e}", file=sys.stderr)
        return 1

    # Send with retry
    if args.dry_run:
        print("DRY RUN - Would send email:")
        print(f"Backend: {backend_type}")
        print(f"From: {msg['From']}")
        print(f"To: {msg['To']}")
        print(f"Subject: {msg['Subject']}")
        return 0

    def send_func():
        return backend.send(msg)

    max_retries = args.retries or config.get('retries', 3)
    result = retry_with_backoff(send_func, max_retries=max_retries)

    if result["success"]:
        print(f"Email sent successfully via {result['backend']}")
        if "message_id" in result:
            print(f"Message ID: {result['message_id']}")
        return 0
    else:
        print(f"Failed to send email: {result['error']}", file=sys.stderr)
        return 1


def cmd_preview(args, config: EmailConfig):
    """Preview email message command."""
    if args.message == '-':
        msg_content = sys.stdin.read()
    else:
        try:
            with open(args.message) as f:
                msg_content = f.read()
        except FileNotFoundError:
            print(f"Error: Email file not found: {args.message}", file=sys.stderr)
            return 1

    # Parse and display
    try:
        parser = email.parser.Parser(policy=email.policy.default)
        msg = parser.parsestr(msg_content)

        print("=" * 50)
        print("EMAIL PREVIEW")
        print("=" * 50)
        print(f"From: {msg['From']}")
        print(f"To: {msg['To']}")
        if msg['Cc']:
            print(f"Cc: {msg['Cc']}")
        print(f"Subject: {msg['Subject']}")
        print("-" * 50)

        body = msg.get_body(("plain",))
        if body:
            print(body.get_content())
        else:
            print("(No plain text body)")

        print("=" * 50)
        return 0

    except Exception as e:
        print(f"Error previewing email: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="Enhanced email CLI tool")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build email message")
    build_parser.add_argument("--from", dest="from_addr", help="From address")
    build_parser.add_argument("--to", dest="to_addrs", help="To addresses")
    build_parser.add_argument("--cc", dest="cc_addrs", help="CC addresses")
    build_parser.add_argument("--subject", required=True, help="Email subject")
    build_parser.add_argument("--body", required=True, help="Body content (file path or '-' for stdin)")
    build_parser.add_argument("--body-pre", help="Text before body (file path or literal text)")
    build_parser.add_argument("--body-post", help="Text after body (file path or literal text)")
    build_parser.add_argument("--html", help="HTML content (file path or content)")
    build_parser.add_argument("--attachment", dest="attachments", action="append", help="Attachment file paths")
    build_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    build_parser.add_argument("--preserve-formatting", "-p", action="store_true", default=False, help="Preserves the formatting of the body (default: False)")

    # Send command
    send_parser = subparsers.add_parser("send", help="Send email message")
    send_parser.add_argument("message", help="Email message file ('-' for stdin)")
    send_parser.add_argument("--backend", choices=["ses", "smtp", "sendmail"], help="Email backend")
    send_parser.add_argument("--dry-run", action="store_true", help="Show what would be sent")
    send_parser.add_argument("--retries", type=int, help="Number of retry attempts")

    # SES options
    send_parser.add_argument("--aws-region", help="AWS region for SES")
    send_parser.add_argument("--aws-profile", help="AWS profile to use")

    # SMTP options
    send_parser.add_argument("--smtp-server", help="SMTP server")
    send_parser.add_argument("--smtp-port", type=int, help="SMTP port")
    send_parser.add_argument("--smtp-username", help="SMTP username")
    send_parser.add_argument("--smtp-password", help="SMTP password")
    send_parser.add_argument("--smtp-tls", action="store_true", help="Use TLS")

    # Sendmail options
    send_parser.add_argument("--sendmail-path", help="Path to sendmail binary")

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview email message")
    preview_parser.add_argument("message", help="Email message file ('-' for stdin)")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    config = EmailConfig(args.config)

    if args.command == "build":
        return cmd_build(args, config)
    elif args.command == "send":
        return cmd_send(args, config)
    elif args.command == "preview":
        return cmd_preview(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
