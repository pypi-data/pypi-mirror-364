"""Tests for configuration models."""

import pytest
from pydantic import ValidationError

from cloe_synthetic_data_generator.config import (
    ColumnConfig,
    DataGenConfig,
    SparkDataType,
    TableTarget,
)


class TestSparkDataType:
    """Test SparkDataType enum."""

    def test_valid_types(self):
        """Test all valid data types."""
        assert SparkDataType.STRING == "string"
        assert SparkDataType.INTEGER == "integer"
        assert SparkDataType.LONG == "long"
        assert SparkDataType.DOUBLE == "double"
        assert SparkDataType.FLOAT == "float"
        assert SparkDataType.BOOLEAN == "boolean"
        assert SparkDataType.DATE == "date"
        assert SparkDataType.TIMESTAMP == "timestamp"
        assert SparkDataType.DECIMAL == "decimal"


class TestColumnConfig:
    """Test ColumnConfig model."""

    def test_valid_column_config(self):
        """Test creating a valid column configuration."""
        config = ColumnConfig(
            name="test_column", data_type=SparkDataType.STRING, nullable=False, faker_function="first_name"
        )

        assert config.name == "test_column"
        assert config.data_type == SparkDataType.STRING
        assert config.nullable is False
        assert config.faker_function == "first_name"
        assert config.faker_options == {}

    def test_column_with_faker_options(self):
        """Test column configuration with faker options."""
        config = ColumnConfig(
            name="age",
            data_type=SparkDataType.INTEGER,
            nullable=True,
            faker_function="random_int",
            faker_options={"min": 18, "max": 65},
        )

        assert config.faker_options == {"min": 18, "max": 65}

    def test_nullable_default_true(self):
        """Test that nullable defaults to True."""
        config = ColumnConfig(name="test_column", data_type=SparkDataType.STRING, faker_function="first_name")

        assert config.nullable is True

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            ColumnConfig()

        errors = exc_info.value.errors()
        required_fields = {"name", "data_type", "faker_function"}
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        assert required_fields.issubset(missing_fields)

    def test_invalid_data_type(self):
        """Test validation error with invalid data type."""
        with pytest.raises(ValidationError) as exc_info:
            ColumnConfig(
                name="test_column",
                data_type="invalid_type",  # type: ignore
                faker_function="first_name",
            )

        assert "Input should be" in str(exc_info.value)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            ColumnConfig(
                name="test_column",
                data_type=SparkDataType.STRING,
                faker_function="first_name",
                extra_field="not_allowed",  # type: ignore
            )

        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestTableTarget:
    """Test TableTarget model."""

    def test_valid_target_config(self):
        """Test creating a valid target configuration."""
        config = TableTarget(catalog="test_catalog", schema="test_schema", table="test_table", write_mode="overwrite")

        assert config.catalog == "test_catalog"
        assert config.schema_name == "test_schema"
        assert config.table == "test_table"
        assert config.write_mode == "overwrite"

    def test_write_mode_default_overwrite(self):
        """Test that write_mode defaults to overwrite."""
        config = TableTarget(catalog="test_catalog", schema="test_schema", table="test_table")

        assert config.write_mode == "overwrite"

    def test_all_write_modes(self):
        """Test all valid write modes."""
        write_modes = ["overwrite", "append", "error", "ignore"]
        for mode in write_modes:
            config = TableTarget(catalog="test_catalog", schema="test_schema", table="test_table", write_mode=mode)
            assert config.write_mode == mode

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            TableTarget()

        errors = exc_info.value.errors()
        required_fields = {"catalog", "schema", "table"}
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        assert required_fields.issubset(missing_fields)


class TestDataGenConfig:
    """Test DataGenConfig model."""

    def test_valid_config(self, sample_target_config, sample_column_config):
        """Test creating a valid data generation configuration."""
        config = DataGenConfig(
            name="Test Configuration",
            target=sample_target_config,
            num_records=100,
            batch_size=50,
            columns=[sample_column_config],
        )

        assert config.name == "Test Configuration"
        assert config.target == sample_target_config
        assert config.num_records == 100
        assert config.batch_size == 50
        assert len(config.columns) == 1
        assert config.columns[0] == sample_column_config

    def test_default_batch_size(self, sample_target_config, sample_column_config):
        """Test that batch_size defaults to 1000."""
        config = DataGenConfig(
            name="Test Configuration", target=sample_target_config, num_records=100, columns=[sample_column_config]
        )

        assert config.batch_size == 1000

    def test_get_table_path(self, sample_target_config, sample_column_config):
        """Test getting the table path from target config."""
        config = DataGenConfig(
            name="Test Configuration", target=sample_target_config, num_records=100, columns=[sample_column_config]
        )

        expected_path = (
            f"{sample_target_config.catalog}.{sample_target_config.schema_name}.{sample_target_config.table}"
        )
        assert config.get_table_path() == expected_path

    def test_multiple_columns(self, sample_target_config):
        """Test configuration with multiple columns."""
        columns = [
            ColumnConfig(name="id", data_type=SparkDataType.STRING, nullable=False, faker_function="uuid4"),
            ColumnConfig(name="name", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
            ColumnConfig(
                name="age",
                data_type=SparkDataType.INTEGER,
                nullable=True,
                faker_function="random_int",
                faker_options={"min": 18, "max": 65},
            ),
        ]

        config = DataGenConfig(name="Multi-column Test", target=sample_target_config, num_records=100, columns=columns)

        assert len(config.columns) == 3
        assert all(isinstance(col, ColumnConfig) for col in config.columns)

    def test_empty_columns_list(self, sample_target_config):
        """Test that empty columns list is allowed."""
        config = DataGenConfig(name="Empty Columns Test", target=sample_target_config, num_records=100, columns=[])

        assert len(config.columns) == 0

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            DataGenConfig()

        errors = exc_info.value.errors()
        required_fields = {"name", "target", "columns"}
        missing_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        assert required_fields.issubset(missing_fields)

    def test_nested_validation_error(self, sample_column_config):
        """Test that nested validation errors are properly reported."""
        with pytest.raises(ValidationError) as exc_info:
            DataGenConfig(
                name="Test Configuration",
                target={  # Invalid target config
                    "catalog": "test_catalog",
                    # Missing required fields
                },
                num_records=100,
                columns=[sample_column_config],
            )

        # Should have validation errors for the nested target config
        errors = exc_info.value.errors()
        target_errors = [error for error in errors if error["loc"][0] == "target"]
        assert len(target_errors) > 0
