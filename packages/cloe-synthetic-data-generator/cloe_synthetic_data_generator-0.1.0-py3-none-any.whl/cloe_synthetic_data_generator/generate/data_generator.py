"""Data generation module using Faker and configuration."""

import logging
from typing import Any

import pandas as pd
from faker import Faker

from cloe_synthetic_data_generator.config import ColumnConfig, DataGenConfig

logger = logging.getLogger(__name__)


def generate_fake_value(faker: Faker, column: ColumnConfig) -> Any:
    """Generate a fake value for a column based on its configuration.

    Args:
        faker: Faker instance
        column: Column configuration

    Returns:
        Generated fake value
    """
    # Handle nullable columns
    if column.nullable and faker.boolean(chance_of_getting_true=10):  # 10% chance of null
        return None

    # Get the faker method
    faker_method = getattr(faker, column.faker_function)

    # Call the method with options
    if column.faker_options:
        return faker_method(**column.faker_options)
    return faker_method()


def generate_fake_data_from_config(config: DataGenConfig) -> pd.DataFrame:
    """Generate fake data based on configuration.

    Args:
        config: Data generation configuration

    Returns:
        pandas DataFrame with fake data
    """
    faker = Faker()
    data = []

    logger.info("Generating %d fake records...", config.num_records)

    for i in range(config.num_records):
        if i % 100 == 0:
            logger.debug("Generated %d records...", i)

        record = {}
        for column in config.columns:
            try:
                record[column.name] = generate_fake_value(faker, column)
            except Exception as e:
                logger.error("Error generating value for column %s: %s", column.name, e)
                raise

        data.append(record)

    logger.info("Successfully generated %d records", config.num_records)
    return pd.DataFrame(data)
