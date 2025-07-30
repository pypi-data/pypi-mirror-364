"""Configuration models for fake data generation using Pydantic v2."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SparkDataType(str, Enum):
    """Supported Spark SQL data types."""

    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    DOUBLE = "double"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    DECIMAL = "decimal"


class ColumnConfig(BaseModel):
    """Configuration for a single column."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Column name")
    data_type: SparkDataType = Field(..., description="Spark SQL data type")
    nullable: bool = Field(default=True, description="Whether column can be null")
    faker_function: str = Field(..., description="Faker method to use (e.g., 'first_name', 'random_int')")
    faker_options: dict[str, Any] = Field(default_factory=dict, description="Options to pass to the Faker method")
    description: str | None = Field(default=None, description="Column description")


class TableTarget(BaseModel):
    """Target table configuration."""

    model_config = ConfigDict(extra="forbid")

    catalog: str = Field(..., description="Unity Catalog catalog name")
    schema_name: str = Field(..., alias="schema", description="Schema name within the catalog")
    table: str = Field(..., description="Table name within the schema")
    write_mode: str = Field(default="overwrite", description="Write mode: overwrite, append, error, ignore")


class DataGenConfig(BaseModel):
    """Complete configuration for fake data generation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Configuration name/description")
    target: TableTarget = Field(..., description="Target table configuration")
    columns: list[ColumnConfig] = Field(..., description="Column definitions")
    num_records: int = Field(default=1000, description="Number of records to generate")
    batch_size: int = Field(default=1000, description="Batch size for processing")

    def get_table_path(self) -> str:
        """Get the full table path."""
        return f"{self.target.catalog}.{self.target.schema_name}.{self.target.table}"
