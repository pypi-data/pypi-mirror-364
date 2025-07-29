#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

"""Enhanced email CLI tool with multiple backend support."""

# Import from focused modules
from .backends import EmailBackend, SESBackend, SMTPBackend, SendmailBackend
from .config import EmailConfig
from .utils import validate_email_address, build_email_message, retry_with_backoff, create_backend


def main():
    """Main function placeholder - CLI logic is in __main__.py"""
    from . import __main__
    return __main__.main()


__all__ = [
    "EmailConfig",
    "EmailBackend",
    "SESBackend",
    "SMTPBackend",
    "SendmailBackend",
    "build_email_message",
    "validate_email_address",
    "retry_with_backoff",
    "create_backend",
    "main"
]

__version__ = "0.0.1"