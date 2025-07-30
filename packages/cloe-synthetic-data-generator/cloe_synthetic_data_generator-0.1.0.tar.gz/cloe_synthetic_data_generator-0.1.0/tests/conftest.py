"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

from cloe_synthetic_data_generator.config import (
    ColumnConfig,
    DataGenConfig,
    SparkDataType,
    TableTarget,
)


@pytest.fixture
def sample_column_config():
    """Sample column configuration for testing."""
    return ColumnConfig(name="test_column", data_type=SparkDataType.STRING, nullable=False, faker_function="first_name")


@pytest.fixture
def sample_target_config():
    """Sample target configuration for testing."""
    return TableTarget(catalog="test_catalog", schema="test_schema", table="test_table", write_mode="overwrite")


@pytest.fixture
def sample_config(sample_target_config, sample_column_config):
    """Sample complete configuration for testing."""
    return DataGenConfig(
        name="Test Configuration",
        target=sample_target_config,
        num_records=100,
        batch_size=50,
        columns=[sample_column_config],
    )


@pytest.fixture
def mock_spark_session():
    """Mock Spark session for testing."""
    mock_spark = MagicMock(spec=SparkSession)
    mock_spark.sql.return_value = MagicMock()
    mock_spark.createDataFrame.return_value = MagicMock()
    return mock_spark


@pytest.fixture
def sample_yaml_config():
    """Sample YAML configuration content."""
    return """
name: "Test Users Configuration"
target:
  catalog: "test_catalog"
  schema: "test_schema"
  table: "users"
  write_mode: "overwrite"
num_records: 100
batch_size: 50
columns:
  - name: "user_id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"
  - name: "first_name"
    data_type: "string"
    nullable: false
    faker_function: "first_name"
  - name: "age"
    data_type: "integer"
    nullable: true
    faker_function: "random_int"
    faker_options:
      min: 18
      max: 65
"""


@pytest.fixture
def temp_config_file(sample_yaml_config):
    """Create a temporary YAML config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(sample_yaml_config)
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    temp_file = Path(temp_path)
    if temp_file.exists():
        temp_file.unlink()


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_table_info():
    """Mock table info for discovery tests."""
    from cloe_synthetic_data_generator.discovery.table_discovery import TableInfo

    return TableInfo(
        catalog="test_catalog",
        schema="test_schema",
        table="test_table",
        columns=[
            {"name": "id", "type": "string", "nullable": False},
            {"name": "name", "type": "string", "nullable": True},
            {"name": "age", "type": "integer", "nullable": True},
        ],
    )


@pytest.fixture
def mock_spark_schema():
    """Mock Spark schema for testing."""
    return StructType(
        [
            StructField("id", StringType(), False),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ]
    )
