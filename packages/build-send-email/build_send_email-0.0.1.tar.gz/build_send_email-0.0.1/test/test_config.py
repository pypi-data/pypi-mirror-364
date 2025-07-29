#!/usr/bin/env python3

"""Unit tests for configuration management."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from build_send_email.config import EmailConfig


class TestEmailConfig:
    """Test the EmailConfig class."""

    def test_config_no_files(self):
        """Test config initialization with no config files."""
        config = EmailConfig()
        assert config.config == {}
        assert config.get('from_addr') is None
        assert config.get('backend', 'default') == 'default'

    def test_config_explicit_file_json(self):
        """Test config with explicit JSON file."""
        config_data = {
            "from_addr": "test@example.com",
            "backend": "smtp",
            "retries": 5
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = EmailConfig(temp_path)
            assert config.get('from_addr') == "test@example.com"
            assert config.get('backend') == "smtp"
            assert config.get('retries') == 5
        finally:
            Path(temp_path).unlink()

    @patch('build_send_email.config.HAS_YAML', True)
    @patch('build_send_email.config.yaml')
    def test_config_yaml_file(self, mock_yaml):
        """Test config with YAML file."""
        config_data = {
            "from_addr": "yaml@example.com",
            "backend": "ses",
            "aws_region": "us-west-2"
        }
        mock_yaml.safe_load.return_value = config_data

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("test config")
            temp_path = f.name

        try:
            with patch('builtins.open', mock_open(read_data="test")):
                config = EmailConfig(temp_path)
                assert config.get('from_addr') == "yaml@example.com"
                assert config.get('backend') == "ses"
                assert config.get('aws_region') == "us-west-2"
        finally:
            Path(temp_path).unlink()

    @patch('build_send_email.config.HAS_YAML', False)
    def test_config_yaml_file_no_yaml_library(self):
        """Test config falls back to JSON when YAML library unavailable."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            json.dump({"from_addr": "fallback@example.com"}, f)
            temp_path = f.name

        try:
            config = EmailConfig(temp_path)
            assert config.get('from_addr') == "fallback@example.com"
        finally:
            Path(temp_path).unlink()

    def test_config_default_search_paths(self):
        """Test config searches default paths."""
        # Create a temporary config in one of the search paths
        config_data = {"from_addr": "default@example.com"}

        with patch.object(Path, 'exists') as mock_exists:
            with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
                # Mock the first path to not exist, second to exist
                mock_exists.side_effect = [False, True]

                config = EmailConfig()
                assert config.get('from_addr') == "default@example.com"

    def test_config_invalid_json(self):
        """Test config handles invalid JSON gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            with patch('build_send_email.config.logging.warning') as mock_warning:
                config = EmailConfig(temp_path)
                assert config.config == {}
                mock_warning.assert_called_once()
                assert "Failed to load config" in str(mock_warning.call_args)
        finally:
            Path(temp_path).unlink()

    @patch('build_send_email.config.HAS_YAML', True)
    @patch('build_send_email.config.yaml')
    def test_config_invalid_yaml(self, mock_yaml):
        """Test config handles invalid YAML gracefully."""
        mock_yaml.YAMLError = Exception  # Set exception class
        mock_yaml.safe_load.side_effect = mock_yaml.YAMLError("Invalid YAML")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:")
            temp_path = f.name

        try:
            with patch('build_send_email.config.logging.warning') as mock_warning:
                config = EmailConfig(temp_path)
                assert config.config == {}
                mock_warning.assert_called_once()
                assert "Failed to load config" in str(mock_warning.call_args)
        finally:
            Path(temp_path).unlink()

    def test_config_file_not_found(self):
        """Test config handles missing file gracefully."""
        config = EmailConfig("/nonexistent/config.json")
        assert config.config == {}

    def test_config_empty_yaml_file(self):
        """Test config handles empty YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            with patch('build_send_email.config.HAS_YAML', True):
                with patch('build_send_email.config.yaml') as mock_yaml:
                    mock_yaml.safe_load.return_value = None
                    config = EmailConfig(temp_path)
                    assert config.config == {}
        finally:
            Path(temp_path).unlink()

    def test_get_method_with_defaults(self):
        """Test get method returns defaults for missing keys."""
        config = EmailConfig()
        assert config.get('nonexistent') is None
        assert config.get('nonexistent', 'default_value') == 'default_value'
        assert config.get('nonexistent', 42) == 42

    def test_get_method_with_existing_values(self):
        """Test get method returns actual values when they exist."""
        config_data = {"test_key": "test_value", "number": 123}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = EmailConfig(temp_path)
            assert config.get('test_key') == "test_value"
            assert config.get('test_key', 'default') == "test_value"
            assert config.get('number') == 123
            assert config.get('number', 0) == 123
        finally:
            Path(temp_path).unlink()

    def test_default_config_paths_format(self):
        """Test that default config paths are correctly formatted."""
        expected_paths = [
            "~/.config/build-send-email/config.yaml",
            "~/.build-send-email.yaml",
            ".build-send-email.yaml",
        ]
        assert EmailConfig.DEFAULT_CONFIG_PATHS == expected_paths