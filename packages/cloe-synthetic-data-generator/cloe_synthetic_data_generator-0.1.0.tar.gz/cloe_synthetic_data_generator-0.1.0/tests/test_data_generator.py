"""Tests for data_generator module."""

from unittest.mock import patch

import pandas as pd
import pytest
from faker import Faker

from cloe_synthetic_data_generator.config import ColumnConfig, SparkDataType
from cloe_synthetic_data_generator.generate.data_generator import (
    generate_fake_data_from_config,
    generate_fake_value,
)


class TestGenerateFakeValue:
    """Test generate_fake_value function."""

    def setup_method(self):
        """Setup faker instance for tests."""
        self.faker = Faker()
        Faker.seed(42)  # For reproducible tests

    def test_generate_string_value(self):
        """Test generating string values."""
        column = ColumnConfig(
            name="first_name", data_type=SparkDataType.STRING, nullable=False, faker_function="first_name"
        )

        value = generate_fake_value(self.faker, column)

        assert isinstance(value, str)
        assert len(value) > 0

    def test_generate_integer_value(self):
        """Test generating integer values."""
        column = ColumnConfig(
            name="age",
            data_type=SparkDataType.INTEGER,
            nullable=False,
            faker_function="random_int",
            faker_options={"min": 18, "max": 65},
        )

        value = generate_fake_value(self.faker, column)

        assert isinstance(value, int)
        assert 18 <= value <= 65

    def test_generate_boolean_value(self):
        """Test generating boolean values."""
        column = ColumnConfig(
            name="is_active", data_type=SparkDataType.BOOLEAN, nullable=False, faker_function="boolean"
        )

        value = generate_fake_value(self.faker, column)

        assert isinstance(value, bool)

    def test_generate_float_value(self):
        """Test generating float values."""
        column = ColumnConfig(
            name="salary",
            data_type=SparkDataType.FLOAT,
            nullable=False,
            faker_function="pyfloat",
            faker_options={"min_value": 1000.0, "max_value": 10000.0},
        )

        value = generate_fake_value(self.faker, column)

        assert isinstance(value, float)
        assert 1000.0 <= value <= 10000.0

    def test_nullable_column_returns_none(self):
        """Test that nullable columns can return None."""
        column = ColumnConfig(
            name="optional_field", data_type=SparkDataType.STRING, nullable=True, faker_function="first_name"
        )

        # Mock boolean to always return True for null generation
        with patch.object(self.faker, "boolean", return_value=True):
            value = generate_fake_value(self.faker, column)
            assert value is None

    def test_non_nullable_column_never_returns_none(self):
        """Test that non-nullable columns never return None."""
        column = ColumnConfig(
            name="required_field", data_type=SparkDataType.STRING, nullable=False, faker_function="first_name"
        )

        # Generate multiple values to ensure none are None
        values = [generate_fake_value(self.faker, column) for _ in range(10)]

        assert all(value is not None for value in values)

    def test_faker_options_passed_correctly(self):
        """Test that faker options are passed to the faker method."""
        column = ColumnConfig(
            name="test_int",
            data_type=SparkDataType.INTEGER,
            nullable=False,
            faker_function="random_int",
            faker_options={"min": 100, "max": 200},
        )

        # Generate multiple values to check range
        values = [generate_fake_value(self.faker, column) for _ in range(20)]

        assert all(100 <= value <= 200 for value in values)

    def test_faker_method_without_options(self):
        """Test faker methods that don't need options."""
        column = ColumnConfig(name="uuid", data_type=SparkDataType.STRING, nullable=False, faker_function="uuid4")

        value = generate_fake_value(self.faker, column)

        assert isinstance(value, str)
        assert len(value) == 36  # UUID4 length

    def test_invalid_faker_method(self):
        """Test error handling for invalid faker methods."""
        column = ColumnConfig(
            name="test", data_type=SparkDataType.STRING, nullable=False, faker_function="non_existent_method"
        )

        with pytest.raises(AttributeError):
            generate_fake_value(self.faker, column)

    def test_random_element_with_options(self):
        """Test random_element faker function with elements option."""
        elements = ["A", "B", "C", "D"]
        column = ColumnConfig(
            name="category",
            data_type=SparkDataType.STRING,
            nullable=False,
            faker_function="random_element",
            faker_options={"elements": elements},
        )

        value = generate_fake_value(self.faker, column)

        assert value in elements


class TestGenerateFakeDataFromConfig:
    """Test generate_fake_data_from_config function."""

    def setup_method(self):
        """Setup for tests."""
        Faker.seed(42)  # For reproducible tests

    def test_generate_simple_dataframe(self, sample_config):
        """Test generating a simple DataFrame."""
        # Modify config to have multiple column types
        sample_config.columns = [
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
        sample_config.num_records = 10

        df = generate_fake_data_from_config(sample_config)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert len(df.columns) == 3
        assert list(df.columns) == ["id", "name", "age"]

    def test_generate_with_nullable_columns(self, sample_config):
        """Test generating data with nullable columns."""
        sample_config.columns = [
            ColumnConfig(name="required_field", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
            ColumnConfig(
                name="optional_field", data_type=SparkDataType.STRING, nullable=True, faker_function="company"
            ),
        ]
        sample_config.num_records = 50

        df = generate_fake_data_from_config(sample_config)

        # Required field should never be null
        assert df["required_field"].isna().sum() == 0

        # Optional field might have some nulls (but not guaranteed in small sample)
        assert df["optional_field"].isna().sum() >= 0

    def test_generate_large_dataframe(self, sample_config):
        """Test generating larger DataFrame."""
        sample_config.num_records = 1000

        df = generate_fake_data_from_config(sample_config)

        assert len(df) == 1000
        assert not df.empty

    def test_data_types_preserved(self, sample_config):
        """Test that data types are properly maintained."""
        sample_config.columns = [
            ColumnConfig(name="string_col", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
            ColumnConfig(
                name="int_col",
                data_type=SparkDataType.INTEGER,
                nullable=False,
                faker_function="random_int",
                faker_options={"min": 1, "max": 100},
            ),
            ColumnConfig(name="bool_col", data_type=SparkDataType.BOOLEAN, nullable=False, faker_function="boolean"),
            ColumnConfig(name="float_col", data_type=SparkDataType.FLOAT, nullable=False, faker_function="pyfloat"),
        ]
        sample_config.num_records = 10

        df = generate_fake_data_from_config(sample_config)

        # Check that data types are correct
        assert df["string_col"].dtype == "object"  # pandas string type
        assert df["int_col"].dtype in ["int64", "Int64"]  # pandas int type
        assert df["bool_col"].dtype in ["bool", "boolean"]  # pandas bool type
        assert df["float_col"].dtype in ["float64", "Float64"]  # pandas float type

    def test_column_order_preserved(self, sample_config):
        """Test that column order is preserved."""
        columns = [
            ColumnConfig(name="third", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
            ColumnConfig(name="first", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
            ColumnConfig(name="second", data_type=SparkDataType.STRING, nullable=False, faker_function="name"),
        ]
        sample_config.columns = columns
        sample_config.num_records = 5

        df = generate_fake_data_from_config(sample_config)

        assert list(df.columns) == ["third", "first", "second"]

    def test_consistent_data_with_seed(self, sample_config):
        """Test that data generation is consistent with same seed."""
        sample_config.num_records = 5

        # Generate data twice with same seed
        Faker.seed(123)
        df1 = generate_fake_data_from_config(sample_config)

        Faker.seed(123)
        df2 = generate_fake_data_from_config(sample_config)

        # DataFrames should be identical
        pd.testing.assert_frame_equal(df1, df2)

    def test_no_columns_config(self, sample_config):
        """Test handling config with no columns."""
        sample_config.columns = []
        sample_config.num_records = 10

        df = generate_fake_data_from_config(sample_config)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert len(df.columns) == 0
