#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

"""Email backend implementations."""

import email.message
import email.utils
import smtplib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import boto3
    import botocore.exceptions
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class EmailBackend:
    """Base class for email backends."""

    def send(self, message: email.message.EmailMessage) -> Dict[str, Any]:
        """Send an email message and return response info."""
        raise NotImplementedError


class SESBackend(EmailBackend):
    """AWS SES email backend."""

    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        if not HAS_BOTO3:
            raise ImportError("boto3 is required for SES backend. Install with: pip install boto3")

        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client("ses", region_name=region)
        self.region = region
        self.profile = profile

    def send(self, message: email.message.EmailMessage) -> Dict[str, Any]:
        source = message["From"]

        to_addresses = email.utils.getaddresses(message.get_all("to", []))
        cc_addresses = email.utils.getaddresses(message.get_all("cc", []))

        destination = {
            "ToAddresses": [addr for name, addr in to_addresses],
            "CcAddresses": [addr for name, addr in cc_addresses],
        }

        subject = message["Subject"] or ""
        body = message.get_body(("plain",)).get_content() if message.get_body(("plain",)) else ""

        ses_message = {
            "Subject": {"Charset": "UTF-8", "Data": subject},
            "Body": {"Text": {"Charset": "UTF-8", "Data": body}},
        }

        try:
            response = self.client.build_send_email(
                Source=source,
                Destination=destination,
                Message=ses_message,
            )
            return {"success": True, "message_id": response["MessageId"], "backend": "ses"}
        except (botocore.exceptions.NoCredentialsError,
                botocore.exceptions.ParamValidationError,
                botocore.exceptions.ClientError) as e:
            return {"success": False, "error": str(e), "backend": "ses"}


class SMTPBackend(EmailBackend):
    """SMTP email backend."""

    def __init__(self, server: str, port: int = 587, username: Optional[str] = None,
                 password: Optional[str] = None, use_tls: bool = True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, message: email.message.EmailMessage) -> Dict[str, Any]:
        try:
            with smtplib.SMTP(self.server, self.port) as smtp:
                if self.use_tls:
                    smtp.starttls()

                if self.username and self.password:
                    smtp.login(self.username, self.password)

                to_addresses = []
                for header in ["to", "cc", "bcc"]:
                    addresses = email.utils.getaddresses(message.get_all(header, []))
                    to_addresses.extend([addr for name, addr in addresses])

                smtp.send_message(message, to_addrs=to_addresses)

                return {"success": True, "backend": "smtp", "server": self.server}
        except (smtplib.SMTPException, OSError) as e:
            return {"success": False, "error": str(e), "backend": "smtp"}


class SendmailBackend(EmailBackend):
    """Local sendmail backend."""

    def __init__(self, sendmail_path: str = "/usr/sbin/sendmail"):
        self.sendmail_path = sendmail_path

    def send(self, message: email.message.EmailMessage) -> Dict[str, Any]:
        try:
            # Check if sendmail exists
            if not Path(self.sendmail_path).exists():
                return {"success": False, "error": f"Sendmail not found at {self.sendmail_path}", "backend": "sendmail"}

            to_addresses = []
            for header in ["to", "cc", "bcc"]:
                addresses = email.utils.getaddresses(message.get_all(header, []))
                to_addresses.extend([addr for name, addr in addresses])

            if not to_addresses:
                return {"success": False, "error": "No recipients found", "backend": "sendmail"}

            cmd = [self.sendmail_path] + to_addresses
            proc = subprocess.run(cmd, input=message.as_string(), text=True,
                                capture_output=True, timeout=30)

            if proc.returncode == 0:
                return {"success": True, "backend": "sendmail"}
            else:
                return {"success": False, "error": proc.stderr, "backend": "sendmail"}

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            return {"success": False, "error": str(e), "backend": "sendmail"}
