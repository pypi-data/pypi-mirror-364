"""Tests for spark_utils module."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from cloe_synthetic_data_generator.config import SparkDataType
from cloe_synthetic_data_generator.spark_utils import (
    create_spark_dataframe_from_config,
    get_spark_data_type,
    verify_table_write,
    write_to_unity_catalog,
)


class TestGetSparkDataType:
    """Test get_spark_data_type function."""

    def test_string_type(self):
        """Test string data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.STRING)
        from pyspark.sql.types import StringType

        assert spark_type == StringType

    def test_integer_type(self):
        """Test integer data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.INTEGER)
        from pyspark.sql.types import IntegerType

        assert spark_type == IntegerType

    def test_long_type(self):
        """Test long data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.LONG)
        from pyspark.sql.types import LongType

        assert spark_type == LongType

    def test_double_type(self):
        """Test double data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.DOUBLE)
        from pyspark.sql.types import DoubleType

        assert spark_type == DoubleType

    def test_float_type(self):
        """Test float data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.FLOAT)
        from pyspark.sql.types import FloatType

        assert spark_type == FloatType

    def test_boolean_type(self):
        """Test boolean data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.BOOLEAN)
        from pyspark.sql.types import BooleanType

        assert spark_type == BooleanType

    def test_date_type(self):
        """Test date data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.DATE)
        from pyspark.sql.types import DateType

        assert spark_type == DateType

    def test_timestamp_type(self):
        """Test timestamp data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.TIMESTAMP)
        from pyspark.sql.types import TimestampType

        assert spark_type == TimestampType

    def test_decimal_type(self):
        """Test decimal data type conversion."""
        spark_type = get_spark_data_type(SparkDataType.DECIMAL)
        from pyspark.sql.types import DecimalType

        assert spark_type == DecimalType


class TestCreateSparkDataframeFromConfig:
    """Test create_spark_dataframe_from_config function."""

    def test_create_simple_dataframe(self, mock_spark_session, sample_config):
        """Test creating a simple Spark DataFrame."""
        # Create sample pandas DataFrame
        pandas_df = pd.DataFrame({"test_column": ["value1", "value2", "value3"]})

        # Mock Spark session createDataFrame method
        mock_spark_df = MagicMock()
        mock_spark_session.createDataFrame.return_value = mock_spark_df

        result_df = create_spark_dataframe_from_config(pandas_df, sample_config, mock_spark_session)

        assert result_df == mock_spark_df
        mock_spark_session.createDataFrame.assert_called_once()

    def test_create_dataframe_with_multiple_columns(self, mock_spark_session, sample_config):
        """Test creating DataFrame with multiple columns and types."""
        # Modify config to have multiple column types
        from cloe_synthetic_data_generator.config import ColumnConfig

        sample_config.columns = [
            ColumnConfig(name="id", data_type=SparkDataType.INTEGER, nullable=False, faker_function="random_int"),
            ColumnConfig(name="name", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
            ColumnConfig(name="is_active", data_type=SparkDataType.BOOLEAN, nullable=True, faker_function="boolean"),
        ]

        pandas_df = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "is_active": [True, False, None]}
        )

        mock_spark_df = MagicMock()
        mock_spark_session.createDataFrame.return_value = mock_spark_df

        result_df = create_spark_dataframe_from_config(pandas_df, sample_config, mock_spark_session)

        assert result_df == mock_spark_df
        mock_spark_session.createDataFrame.assert_called_once()

    def test_create_dataframe_empty(self, mock_spark_session, sample_config):
        """Test creating DataFrame from empty pandas DataFrame."""
        pandas_df = pd.DataFrame({"test_column": []})

        mock_spark_df = MagicMock()
        mock_spark_session.createDataFrame.return_value = mock_spark_df

        result_df = create_spark_dataframe_from_config(pandas_df, sample_config, mock_spark_session)

        assert result_df == mock_spark_df
        mock_spark_session.createDataFrame.assert_called_once()

    def test_spark_creation_error(self, mock_spark_session, sample_config):
        """Test error handling when Spark DataFrame creation fails."""
        pandas_df = pd.DataFrame({"test_column": ["value1"]})
        mock_spark_session.createDataFrame.side_effect = Exception("Spark error")

        with pytest.raises(Exception) as exc_info:
            create_spark_dataframe_from_config(pandas_df, sample_config, mock_spark_session)

        assert "Spark error" in str(exc_info.value)


class TestWriteToUnityCatalog:
    """Test write_to_unity_catalog function."""

    def test_write_overwrite_mode(self, sample_config):
        """Test writing DataFrame in overwrite mode."""
        mock_spark_df = MagicMock()

        write_to_unity_catalog(
            mock_spark_df, sample_config.target.catalog, sample_config.target.schema_name, sample_config.target.table
        )

        # Verify write method was called with correct parameters
        mock_spark_df.write.mode.assert_called_once_with("overwrite")
        mock_spark_df.write.mode.return_value.option.assert_called_once_with("mergeSchema", "true")
        mock_spark_df.write.mode.return_value.option.return_value.saveAsTable.assert_called_once_with(
            sample_config.get_table_path()
        )

    def test_write_append_mode(self, sample_config):
        """Test writing DataFrame in append mode."""
        mock_spark_df = MagicMock()

        write_to_unity_catalog(
            mock_spark_df,
            sample_config.target.catalog,
            sample_config.target.schema_name,
            sample_config.target.table,
            "append",
        )

        mock_spark_df.write.mode.assert_called_once_with("append")

    def test_write_with_different_table_path(self):
        """Test writing to different table path."""
        mock_spark_df = MagicMock()

        write_to_unity_catalog(mock_spark_df, "production", "analytics", "user_events")

        expected_table_path = "production.analytics.user_events"
        mock_spark_df.write.mode.return_value.option.return_value.saveAsTable.assert_called_once_with(
            expected_table_path
        )

    def test_write_error_handling(self, sample_config):
        """Test error handling during write operation."""
        mock_spark_df = MagicMock()
        mock_spark_df.write.mode.return_value.option.return_value.saveAsTable.side_effect = Exception("Write failed")

        with pytest.raises(Exception) as exc_info:
            write_to_unity_catalog(
                mock_spark_df,
                sample_config.target.catalog,
                sample_config.target.schema_name,
                sample_config.target.table,
            )

        assert "Write failed" in str(exc_info.value)

    @patch("cloe_synthetic_data_generator.spark_utils.logger")
    def test_logging_messages(self, mock_logger, sample_config):
        """Test that appropriate log messages are generated."""
        mock_spark_df = MagicMock()

        write_to_unity_catalog(
            mock_spark_df, sample_config.target.catalog, sample_config.target.schema_name, sample_config.target.table
        )

        # Check that info messages were logged
        mock_logger.info.assert_called()

        # Check specific log messages
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Writing data to Unity Catalog table" in call for call in calls)


class TestVerifyTableWrite:
    """Test verify_table_write function."""

    def test_verify_successful_write(self, mock_spark_session, sample_config):
        """Test verifying a successful table write."""
        # Mock read.table to return a DataFrame
        mock_df = MagicMock()
        mock_df.count.return_value = 100
        mock_spark_session.read.table.return_value = mock_df

        # Should not raise an exception
        verify_table_write(
            mock_spark_session,
            sample_config.target.catalog,
            sample_config.target.schema_name,
            sample_config.target.table,
        )

        # Verify correct table path was used
        expected_table_path = sample_config.get_table_path()
        mock_spark_session.read.table.assert_called_once_with(expected_table_path)
        mock_df.count.assert_called_once()
        mock_df.show.assert_called_once_with(3, truncate=False)
        mock_df.printSchema.assert_called_once()

    def test_verify_table_not_found(self, mock_spark_session, sample_config):
        """Test verification when table doesn't exist."""
        mock_spark_session.read.table.side_effect = Exception("Table not found")

        with pytest.raises(Exception) as exc_info:
            verify_table_write(
                mock_spark_session,
                sample_config.target.catalog,
                sample_config.target.schema_name,
                sample_config.target.table,
            )

        assert "Table not found" in str(exc_info.value)

    @patch("cloe_synthetic_data_generator.spark_utils.logger")
    def test_verify_logging_messages(self, mock_logger, mock_spark_session, sample_config):
        """Test that verification logs appropriate messages."""
        mock_df = MagicMock()
        mock_df.count.return_value = 100
        mock_spark_session.read.table.return_value = mock_df

        verify_table_write(
            mock_spark_session,
            sample_config.target.catalog,
            sample_config.target.schema_name,
            sample_config.target.table,
        )

        # Check that info messages were logged
        mock_logger.info.assert_called()

        # Check specific log messages
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Verifying data was written" in call for call in calls)
        assert any("contains" in call and "rows" in call for call in calls)
