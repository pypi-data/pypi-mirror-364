#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

"""Configuration management for email CLI."""

import json
import logging
from pathlib import Path
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class EmailConfig:
    """Configuration management for email CLI."""

    DEFAULT_CONFIG_PATHS = [
        "~/.config/build-send-email/config.yaml",
        "~/.build-send-email.yaml",
        ".build-send-email.yaml",
    ]

    def __init__(self, config_file: Optional[str] = None):
        self.config = {}
        self._load_config(config_file)

    def _load_config(self, config_file: Optional[str] = None):
        """Load configuration from file."""
        config_paths = [config_file] if config_file else self.DEFAULT_CONFIG_PATHS

        for path_str in config_paths:
            if not path_str:
                continue

            path = Path(path_str).expanduser()
            if path.exists():
                try:
                    if HAS_YAML and path.suffix in ['.yaml', '.yml']:
                        with open(path) as f:
                            self.config = yaml.safe_load(f) or {}
                    else:
                        with open(path) as f:
                            self.config = json.load(f)
                    break
                except (yaml.YAMLError, json.JSONDecodeError, OSError) as e:
                    logging.warning(f"Failed to load config from {path}: {e}")

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
