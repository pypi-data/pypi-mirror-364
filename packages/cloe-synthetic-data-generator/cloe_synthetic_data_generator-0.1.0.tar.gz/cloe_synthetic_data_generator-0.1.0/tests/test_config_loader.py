"""Tests for config_loader module."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from cloe_synthetic_data_generator.config import DataGenConfig
from cloe_synthetic_data_generator.config_loader import (
    load_config,
    load_configs_from_directory,
)


class TestLoadConfig:
    """Test load_config function."""

    def test_load_valid_config(self, temp_config_file):
        """Test loading a valid configuration file."""
        config = load_config(temp_config_file)

        assert isinstance(config, DataGenConfig)
        assert config.name == "Test Users Configuration"
        assert config.target.catalog == "test_catalog"
        assert config.target.schema_name == "test_schema"
        assert config.target.table == "users"
        assert config.num_records == 100
        assert config.batch_size == 50
        assert len(config.columns) == 3

    def test_load_config_string_path(self, temp_config_file):
        """Test loading config with string path."""
        config = load_config(str(temp_config_file))

        assert isinstance(config, DataGenConfig)
        assert config.name == "Test Users Configuration"

    def test_file_not_found(self):
        """Test error when configuration file doesn't exist."""
        non_existent_path = Path("/non/existent/path.yaml")

        with pytest.raises(FileNotFoundError) as exc_info:
            load_config(non_existent_path)

        assert "Configuration file not found" in str(exc_info.value)

    def test_invalid_yaml_syntax(self, temp_directory):
        """Test error when YAML has syntax errors."""
        invalid_yaml = "name: 'Test\n  invalid: yaml: syntax"
        config_file = temp_directory / "invalid.yaml"
        config_file.write_text(invalid_yaml)

        with pytest.raises(yaml.scanner.ScannerError) as exc_info:
            load_config(config_file)

        assert "while scanning a quoted scalar" in str(exc_info.value)

    def test_invalid_config_data(self, temp_directory):
        """Test error when YAML is valid but config data is invalid."""
        invalid_config = """
        name: "Test Config"
        # Missing required fields like target, num_records, columns
        """
        config_file = temp_directory / "invalid_config.yaml"
        config_file.write_text(invalid_config)

        with pytest.raises(Exception) as exc_info:
            load_config(config_file)

        assert "validation error" in str(exc_info.value)

    def test_empty_file(self, temp_directory):
        """Test error when configuration file is empty."""
        empty_file = temp_directory / "empty.yaml"
        empty_file.write_text("")

        with pytest.raises(TypeError) as exc_info:
            load_config(empty_file)

        assert "must be a mapping" in str(exc_info.value)

    def test_logging_info_message(self, temp_config_file, caplog):
        """Test that loading logs an info message."""
        with caplog.at_level("INFO"):
            load_config(temp_config_file)

        assert "Loading configuration from" in caplog.text
        assert str(temp_config_file) in caplog.text


class TestLoadConfigsFromDirectory:
    """Test load_configs_from_directory function."""

    def test_load_multiple_configs(self, temp_directory, sample_yaml_config):
        """Test loading multiple configuration files from directory."""
        # Create multiple config files
        config1 = temp_directory / "config1.yaml"
        config2 = temp_directory / "config2.yaml"
        config3 = temp_directory / "config3.yml"  # Different extension

        config1.write_text(sample_yaml_config)
        config2.write_text(sample_yaml_config.replace("users", "orders"))
        config3.write_text(sample_yaml_config.replace("users", "products"))

        configs = load_configs_from_directory(temp_directory)

        assert len(configs) == 3
        assert all(isinstance(config, DataGenConfig) for config in configs)

        # Check that different tables were loaded
        table_names = [config.target.table for config in configs]
        assert "users" in table_names
        assert "orders" in table_names
        assert "products" in table_names

    def test_load_configs_string_path(self, temp_directory, sample_yaml_config):
        """Test loading configs with string directory path."""
        config_file = temp_directory / "config.yaml"
        config_file.write_text(sample_yaml_config)

        configs = load_configs_from_directory(str(temp_directory))

        assert len(configs) == 1
        assert isinstance(configs[0], DataGenConfig)

    def test_empty_directory(self, temp_directory):
        """Test loading from empty directory."""
        with pytest.raises(ValueError) as exc_info:
            load_configs_from_directory(temp_directory)

        assert "No YAML files found" in str(exc_info.value)

    def test_directory_not_found(self):
        """Test error when directory doesn't exist."""
        non_existent_dir = Path("/non/existent/directory")

        with pytest.raises(FileNotFoundError) as exc_info:
            load_configs_from_directory(non_existent_dir)

        assert "Directory not found" in str(exc_info.value)

    def test_not_a_directory(self, temp_config_file):
        """Test error when path is not a directory."""
        with pytest.raises(ValueError) as exc_info:
            load_configs_from_directory(temp_config_file)

        assert "Path is not a directory" in str(exc_info.value)

    def test_skip_non_yaml_files(self, temp_directory, sample_yaml_config):
        """Test that non-YAML files are skipped."""
        # Create YAML files
        yaml_file = temp_directory / "config.yaml"
        yaml_file.write_text(sample_yaml_config)

        # Create non-YAML files
        txt_file = temp_directory / "readme.txt"
        txt_file.write_text("This is not a YAML file")

        json_file = temp_directory / "data.json"
        json_file.write_text('{"key": "value"}')

        configs = load_configs_from_directory(temp_directory)

        # Only the YAML file should be loaded
        assert len(configs) == 1
        assert configs[0].name == "Test Users Configuration"

    def test_skip_invalid_config_files(self, temp_directory, sample_yaml_config, caplog):
        """Test that invalid config files are skipped with warning."""
        # Create valid config
        valid_file = temp_directory / "valid.yaml"
        valid_file.write_text(sample_yaml_config)

        # Create invalid config
        invalid_file = temp_directory / "invalid.yaml"
        invalid_file.write_text("name: 'Invalid'\n# Missing required fields")

        with caplog.at_level("WARNING"):
            configs = load_configs_from_directory(temp_directory)

        # Only valid config should be loaded
        assert len(configs) == 1
        assert configs[0].name == "Test Users Configuration"

        # Should have warning about invalid file
        assert "Failed to load configuration" in caplog.text
        assert "invalid.yaml" in caplog.text

    def test_skip_corrupted_yaml_files(self, temp_directory, sample_yaml_config, caplog):
        """Test that corrupted YAML files are skipped with warning."""
        # Create valid config
        valid_file = temp_directory / "valid.yaml"
        valid_file.write_text(sample_yaml_config)

        # Create corrupted YAML
        corrupted_file = temp_directory / "corrupted.yaml"
        corrupted_file.write_text("name: 'Test\n  invalid: yaml: syntax")

        with caplog.at_level("WARNING"):
            configs = load_configs_from_directory(temp_directory)

        # Only valid config should be loaded
        assert len(configs) == 1
        assert configs[0].name == "Test Users Configuration"

        # Should have warning about corrupted file
        assert "Failed to load configuration" in caplog.text
        assert "corrupted.yaml" in caplog.text

    def test_logging_info_message(self, temp_directory, sample_yaml_config, caplog):
        """Test that loading logs info messages."""
        config_file = temp_directory / "config.yaml"
        config_file.write_text(sample_yaml_config)

        with caplog.at_level("INFO"):
            load_configs_from_directory(temp_directory)

        assert "Loading configurations from directory" in caplog.text
        assert "Successfully loaded 1 configuration" in caplog.text

    def test_permission_error_on_directory(self):
        """Test error when directory cannot be accessed due to permissions."""
        # This test is complex to mock properly due to Path object limitations
        # For now we'll test the basic case - function exists and can handle errors
        with patch("cloe_synthetic_data_generator.config_loader.Path") as mock_path:
            mock_dir = mock_path.return_value
            mock_dir.exists.return_value = True
            mock_dir.is_dir.return_value = True
            mock_dir.glob.side_effect = PermissionError("Permission denied")

            with pytest.raises(PermissionError):
                load_configs_from_directory("/some/path")
