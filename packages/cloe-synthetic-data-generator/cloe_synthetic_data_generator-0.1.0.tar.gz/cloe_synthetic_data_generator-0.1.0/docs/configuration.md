# Configuration Guide

This guide covers everything you need to know about creating and configuring YAML files for synthetic data generation.

## Configuration File Structure

Every configuration file follows this basic structure:

```yaml
name: "Descriptive name for your configuration"
target:
  catalog: "catalog_name"
  schema: "schema_name"
  table: "table_name"
  write_mode: "overwrite"
num_records: 1000
batch_size: 1000
columns:
  - name: "column_name"
    data_type: "string"
    nullable: true
    faker_function: "faker_method"
    faker_options: {}
```

## Configuration Sections

### Target Table Configuration

The `target` section defines where your generated data will be written:

```yaml
target:
  catalog: "main"              # Unity Catalog name
  schema: "hr_data"            # Schema within the catalog
  table: "employees"           # Table name
  write_mode: "overwrite"      # How to handle existing data
```

#### Write Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `overwrite` | Replace all existing data | Development, testing, complete refresh |
| `append` | Add new data to existing table | Incremental data generation |
| `error` | Fail if table already exists | Safety check for new tables |
| `ignore` | Skip if table already exists | Safe re-runs |

!!! tip "Choosing Write Mode"
    - Use `overwrite` for development and testing environments
    - Use `append` when you want to add more data incrementally
    - Use `error` for production safety when creating new tables

### Generation Settings

Control how much data is generated and processed:

```yaml
num_records: 10000           # Total number of records to generate
batch_size: 1000             # Process in batches of this size
```

!!! info "Batch Size Considerations"
    - Larger batch sizes are more memory efficient
    - Smaller batch sizes provide better progress feedback
    - Default batch size of 1000 works well for most use cases

### Column Definitions

Each column is defined with these properties:

#### Required Properties

```yaml
- name: "column_name"        # Column name in the target table
  data_type: "string"        # Spark SQL data type
  faker_function: "email"    # Faker method to use
```

#### Optional Properties

```yaml
- name: "column_name"
  data_type: "string"
  nullable: true             # Allow NULL values (default: true)
  faker_function: "email"
  faker_options:             # Options passed to Faker method
    domain: "company.com"
  description: "User email"  # Column description (optional)
```

## Supported Data Types

CLOE supports all common Spark SQL data types:

### Basic Types

| Type | Description | Example Values |
|------|-------------|----------------|
| `string` | Text data | "John Doe", "example@email.com" |
| `integer` | 32-bit integers | 42, -123 |
| `long` | 64-bit integers | 1234567890123 |
| `double` | Double precision floats | 3.14159, 123.456 |
| `float` | Single precision floats | 3.14, 123.45 |
| `boolean` | True/false values | true, false |

### Date and Time Types

| Type | Description | Example Values |
|------|-------------|----------------|
| `date` | Date only | "2024-01-15" |
| `timestamp` | Date and time | "2024-01-15 14:30:00" |

### Decimal Type

| Type | Description | Example Values |
|------|-------------|----------------|
| `decimal` | Precise decimal numbers | 123.45, 999.99 |

!!! note "Type Conversion"
    CLOE automatically converts Python data types from Faker to appropriate Spark SQL types. For example, Faker's `date_time()` is automatically converted to Spark's `timestamp` type.

## Faker Integration

CLOE uses the [Faker library](https://faker.readthedocs.io/) to generate realistic data. You can use any Faker provider method.

### Basic Faker Functions

Common faker functions for different types of data:

#### Personal Information

```yaml
# Names
- name: "first_name"
  data_type: "string"
  faker_function: "first_name"

- name: "last_name"
  data_type: "string"
  faker_function: "last_name"

- name: "full_name"
  data_type: "string"
  faker_function: "name"

# Contact Information
- name: "email"
  data_type: "string"
  faker_function: "email"

- name: "phone"
  data_type: "string"
  faker_function: "phone_number"
```

#### Business Data

```yaml
- name: "company_name"
  data_type: "string"
  faker_function: "company"

- name: "job_title"
  data_type: "string"
  faker_function: "job"

- name: "department"
  data_type: "string"
  faker_function: "random_element"
  faker_options:
    elements: ["Engineering", "Sales", "Marketing", "HR"]
```

#### Numbers and IDs

```yaml
- name: "user_id"
  data_type: "string"
  faker_function: "uuid4"

- name: "age"
  data_type: "integer"
  faker_function: "random_int"
  faker_options:
    min: 18
    max: 80

- name: "salary"
  data_type: "double"
  faker_function: "random_number"
  faker_options:
    digits: 5
```

#### Dates and Times

```yaml
- name: "birth_date"
  data_type: "date"
  faker_function: "date_between"
  faker_options:
    start_date: "-65y"    # 65 years ago
    end_date: "-18y"      # 18 years ago

- name: "created_at"
  data_type: "timestamp"
  faker_function: "date_time_between"
  faker_options:
    start_date: "-1y"     # 1 year ago
    end_date: "now"       # Current time
```

### Advanced Faker Options

Most Faker methods accept options to customize the generated data:

#### String Length Control

```yaml
- name: "description"
  data_type: "string"
  faker_function: "text"
  faker_options:
    max_nb_chars: 200     # Maximum 200 characters
```

#### Localization

```yaml
- name: "local_phone"
  data_type: "string"
  faker_function: "phone_number"
  faker_options:
    locale: "en_US"       # US phone format
```

#### Custom Choices

```yaml
- name: "status"
  data_type: "string"
  faker_function: "random_element"
  faker_options:
    elements: ["active", "inactive", "pending", "suspended"]

- name: "priority"
  data_type: "string"
  faker_function: "random_choices"
  faker_options:
    elements: ["low", "medium", "high", "critical"]
    length: 1             # Return single choice
```

#### Numeric Ranges

```yaml
- name: "score"
  data_type: "integer"
  faker_function: "random_int"
  faker_options:
    min: 0
    max: 100

- name: "price"
  data_type: "double"
  faker_function: "pyfloat"
  faker_options:
    left_digits: 3        # 3 digits before decimal
    right_digits: 2       # 2 digits after decimal
    positive: true        # Only positive numbers
```

### Working with NULL Values

Control null value generation:

```yaml
- name: "optional_field"
  data_type: "string"
  nullable: true          # Allow nulls (default: true)
  faker_function: "word"
```

!!! info "NULL Generation"
    When `nullable: true`, CLOE automatically generates NULL values for approximately 10% of records. This percentage is not currently configurable but provides realistic null distributions.

## Validation and Testing

Always validate your configuration before generating large datasets:

```bash
# Validate configuration syntax and structure
cloe-synthetic-data-generator validate-config my_config.yaml

# Generate a small sample first
cloe-synthetic-data-generator generate --config my_config.yaml --num-records 10
```

!!! tip "Configuration Testing"
    1. Start with small record counts (10-100) to verify your configuration works
    2. Use the validation command to catch errors early
    3. Check generated data samples to ensure they meet your expectations
    4. Gradually increase record counts for performance testing

## Next Steps

- 🔍 [Explore Table Discovery](table-discovery.md) - Auto-generate configurations from existing tables
- ⚡ [CLI Reference](cli-reference.md) - Learn about all CLI commands and options
- 🎭 [Faker Integration](faker-integration.md) - Deep dive into Faker capabilities
- 📊 [Advanced Examples](examples.md) - See complex real-world configuration examples
