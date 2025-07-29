#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

"""Utility functions for email handling."""

import email.message
import email.utils
import logging
import time
from pathlib import Path
from typing import Optional

from .backends import EmailBackend, SESBackend, SMTPBackend, SendmailBackend
from .config import EmailConfig


def validate_email_address(email_addr: str) -> bool:
    """Basic email address validation."""
    try:
        parsed = email.utils.parseaddr(email_addr)
        addr = parsed[1]

        # Must have @ and at least one dot
        if "@" not in addr or "." not in addr:
            return False

        # Split on @ - should have exactly 2 parts
        parts = addr.split("@")
        if len(parts) != 2:
            return False

        local, domain = parts

        # Local part (before @) must not be empty
        if not local:
            return False

        # Domain part must have at least one dot and not start/end with dot
        if not domain or domain.startswith(".") or domain.endswith("."):
            return False

        return True
    except:
        return False


def build_email_message(from_addr: str, to_addrs: str, subject: str, body_content: str,
                       cc_addrs: Optional[str] = None, html_content: Optional[str] = None,
                       attachments: Optional[list] = None, preserve_formatting: bool = False) -> email.message.EmailMessage:
    """Build an email message with enhanced features."""
    msg = email.message.EmailMessage()

    # Validate addresses
    if not validate_email_address(from_addr):
        raise ValueError(f"Invalid from address: {from_addr}")

    msg["From"] = from_addr
    msg["To"] = to_addrs
    if cc_addrs:
        msg["Cc"] = cc_addrs
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid()

    # Set content
    if html_content:
        if preserve_formatting:
            msg.set_payload(body_content)
        else:
            msg.set_content(body_content)
        msg.add_alternative(html_content, subtype='html')
    else:
        if preserve_formatting:
            msg.set_payload(body_content)
        else:
            msg.set_content(body_content)

    # Add attachments (basic implementation)
    if attachments:
        for attachment_path in attachments:
            path = Path(attachment_path)
            if path.exists():
                with open(path, 'rb') as f:
                    msg.add_attachment(f.read(),
                                     maintype='application',
                                     subtype='octet-stream',
                                     filename=path.name)

    return msg


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            result = func()
            if result.get("success", False):
                return result
            elif attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {result.get('error')}")
                time.sleep(delay)
            else:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed with exception, retrying in {delay}s: {e}")
                time.sleep(delay)
            else:
                return {"success": False, "error": str(e)}

    return {"success": False, "error": "Max retries exceeded"}


def create_backend(backend_type: str, config: EmailConfig, args) -> EmailBackend:
    """Create email backend based on type and configuration."""
    if backend_type == "ses":
        region = getattr(args, 'aws_region', None) or config.get('aws_region', 'us-east-1')
        profile = getattr(args, 'aws_profile', None) or config.get('aws_profile')
        return SESBackend(region=region, profile=profile)

    elif backend_type == "smtp":
        server = getattr(args, 'smtp_server', None) or config.get('smtp_server', 'localhost')
        port = getattr(args, 'smtp_port', None) or config.get('smtp_port', 587)
        username = getattr(args, 'smtp_username', None) or config.get('smtp_username')
        password = getattr(args, 'smtp_password', None) or config.get('smtp_password')
        use_tls = getattr(args, 'smtp_tls', None)
        if use_tls is None:
            use_tls = config.get('smtp_tls', True)

        return SMTPBackend(server=server, port=port, username=username,
                          password=password, use_tls=use_tls)

    elif backend_type == "sendmail":
        sendmail_path = getattr(args, 'sendmail_path', None) or config.get('sendmail_path', '/usr/sbin/sendmail')
        return SendmailBackend(sendmail_path=sendmail_path)

    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
