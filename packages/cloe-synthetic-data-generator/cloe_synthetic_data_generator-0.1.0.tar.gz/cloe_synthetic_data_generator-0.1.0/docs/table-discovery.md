# Table Discovery

The table discovery feature automatically discovers existing tables in your Databricks Unity Catalog and generates YAML configuration files with intelligent faker function mapping. This is especially useful for recreating data structures or generating test data that matches your production schemas.

## Overview

Table discovery works by:

1. **Connecting** to your Databricks workspace via Databricks Connect
2. **Scanning** tables in specified catalog and schema
3. **Analyzing** column names and data types
4. **Mapping** appropriate Faker functions based on column characteristics
5. **Generating** ready-to-use YAML configuration files

## Basic Usage

### Discover All Tables

Discover all tables in a catalog and schema:

```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data
```

### Discover Specific Tables

Use regex patterns to filter tables:

```bash
# Discover tables starting with "employee"
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data \
  --table-regex "^employee.*"

# Discover tables containing "fact" or "dim"
cloe-synthetic-data-generator discover \
  --catalog analytics \
  --schema warehouse \
  --table-regex "(fact|dim)_.*"
```

### Customize Output

Control where configurations are saved and how much data to generate:

```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema test_data \
  --output-dir ./custom_configs \
  --num-records 5000 \
  --write-mode append
```

## Intelligent Faker Mapping

The discovery process automatically maps appropriate Faker functions based on column names and data types:

### Name Recognition Patterns

| Column Pattern | Faker Function | Example Data |
|----------------|----------------|--------------|
| `first_name`, `fname` | `first_name` | "John", "Sarah" |
| `last_name`, `lname`, `surname` | `last_name` | "Smith", "Johnson" |
| `full_name`, `name` | `name` | "John Smith" |
| `email`, `mail` | `email` | "john@example.com" |
| `phone`, `tel`, `mobile` | `phone_number` | "+1-555-123-4567" |

### Address Recognition

| Column Pattern | Faker Function | Example Data |
|----------------|----------------|--------------|
| `address`, `street` | `address` | "123 Main St" |
| `city`, `town` | `city` | "New York" |
| `state`, `province` | `state` | "California" |
| `country`, `nation` | `country` | "United States" |
| `zip`, `postal`, `postcode` | `zipcode` | "12345" |

### Business Data Recognition

| Column Pattern | Faker Function | Example Data |
|----------------|----------------|--------------|
| `company`, `organization` | `company` | "Acme Corp" |
| `job`, `title`, `position` | `job` | "Software Engineer" |
| `department`, `dept` | `random_element` | "Engineering", "Sales" |
| `salary`, `wage` | `pyfloat` | 75000.00 |

### ID and Identifier Recognition

| Column Pattern | Faker Function | Example Data |
|----------------|----------------|--------------|
| `id`, `uuid`, `guid` | `uuid4` | "550e8400-e29b-41d4..." |
| `ssn`, `social_security` | `ssn` | "123-45-6789" |
| `*_id` (ending in _id) | `uuid4` | "550e8400-e29b-41d4..." |

### Date and Time Recognition

| Column Pattern | Faker Function | Example Data |
|----------------|----------------|--------------|
| `birth_date`, `birthday`, `dob` | `date_between` | "1985-05-15" |
| `created_at`, `created_date` | `date_time_between` | "2023-01-15 14:30:00" |
| `updated_at`, `modified_at` | `date_time_between` | "2023-12-01 09:15:22" |
| `start_date`, `end_date` | `date_between` | "2023-01-01" |

### Numeric Data Recognition

| Data Type | Default Faker Function | Example Options |
|-----------|------------------------|-----------------|
| `integer` | `random_int` | `min: 1, max: 100` |
| `long` | `random_int` | `min: 1000, max: 999999` |
| `double`, `float` | `pyfloat` | `left_digits: 3, right_digits: 2` |
| `decimal` | `pydecimal` | `left_digits: 4, right_digits: 2` |
| `boolean` | `boolean` | `chance_of_getting_true: 50` |

## Discovery Output

### Generated Files

The discovery process creates files using this naming convention:
```
{catalog}_{schema}_{table_name}_config.yaml
```

For example, discovering `main.hr_data.employees` creates:
```
main_hr_data_employees_config.yaml
```

### Sample Generated Configuration

Here's an example of what the discovery process might generate for an employee table:

```yaml title="main_hr_data_employees_config.yaml"
name: Employees Data Generation
num_records: 1000
columns:
- name: employee_id
  data_type: string
  nullable: false
  faker_function: uuid4
  faker_options: {}

- name: first_name
  data_type: string
  nullable: false
  faker_function: first_name
  faker_options: {}

- name: last_name
  data_type: string
  nullable: false
  faker_function: last_name
  faker_options: {}

- name: email
  data_type: string
  nullable: true
  faker_function: email
  faker_options:
    domain: company.com

- name: department
  data_type: string
  nullable: true
  faker_function: random_element
  faker_options:
    elements: ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']

- name: salary
  data_type: double
  nullable: true
  faker_function: pyfloat
  faker_options:
    left_digits: 5
    right_digits: 2
    positive: true
    min_value: 30000
    max_value: 200000

- name: hire_date
  data_type: date
  nullable: true
  faker_function: date_between
  faker_options:
    start_date: -10y
    end_date: today

target:
  catalog: main
  schema: hr_data
  table: employees
  write_mode: overwrite
```

## Advanced Discovery Options

### Custom Output Directory Structure

Organize discovered configurations by catalog or schema:

```bash
# Create subdirectories by catalog
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data \
  --output-dir "./configs/main/"

# Create subdirectories by schema
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data \
  --output-dir "./configs/hr_data/"
```

### Batch Discovery Across Multiple Schemas

Use shell scripting to discover across multiple schemas:

```bash
#!/bin/bash
CATALOG="main"
SCHEMAS=("hr_data" "finance_data" "marketing_data")

for schema in "${SCHEMAS[@]}"; do
    echo "Discovering tables in $CATALOG.$schema..."
    cloe-synthetic-data-generator discover \
        --catalog "$CATALOG" \
        --schema "$schema" \
        --output-dir "./configs/$schema/" \
        --num-records 1000
done
```

### Discovery with Custom Record Counts by Table Pattern

```bash
# High-volume tables get more records
cloe-synthetic-data-generator discover \
  --catalog analytics \
  --schema warehouse \
  --table-regex "fact_.*" \
  --num-records 100000

# Dimension tables get fewer records
cloe-synthetic-data-generator discover \
  --catalog analytics \
  --schema warehouse \
  --table-regex "dim_.*" \
  --num-records 1000
```

## Discovery Best Practices

### 1. Start Small

Begin with a single schema to understand the discovery output:

```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema test_schema \
  --num-records 100
```

### 2. Use Descriptive Output Directories

Organize configurations logically:

```bash
# By environment
--output-dir "./configs/dev/"
--output-dir "./configs/staging/"

# By domain
--output-dir "./configs/hr/"
--output-dir "./configs/finance/"
```

### 3. Filter Tables Strategically

Use regex patterns to focus on relevant tables:

```bash
# Skip temporary or system tables
--table-regex "^(?!temp_|sys_|_tmp).*"

# Focus on specific table types
--table-regex "(employee|customer|product)_.*"
```

### 4. Set Appropriate Record Counts

Consider table purpose when setting record counts:

- **Large fact tables**: 10,000+ records for performance testing
- **Dimension tables**: 100-1,000 records for referential integrity
- **Configuration tables**: 10-50 records for basic functionality

### 5. Review Faker Mappings

Always review and customize the auto-generated faker functions:

```yaml
# Auto-generated might be too generic
- name: status
  faker_function: word

# Customize for domain-specific values
- name: status
  faker_function: random_element
  faker_options:
    elements: ["active", "inactive", "pending", "suspended"]
```

## Troubleshooting Discovery

### Permission Issues

!!! warning "Catalog Access"
    **Error**: `Permission denied to access catalog.schema`

    **Solution**:

    - Verify Unity Catalog permissions
    - Check if catalog and schema exist
    - Ensure your user/service principal has `SELECT` permissions

### No Tables Found

!!! info "Empty Results"
    **Error**: `No tables found matching the criteria`

    **Troubleshooting**:

    1. Verify catalog and schema names
    2. Check if tables exist: `SHOW TABLES IN catalog.schema`
    3. Adjust regex pattern to be less restrictive
    4. Remove `--table-regex` to see all tables

### Connection Issues

!!! failure "Databricks Connection"
    **Error**: `Failed to connect to Databricks`

    **Solution**:

    1. Test connection: `test-connection`
    2. Verify Databricks Connect setup
    3. Check network connectivity
    4. Validate workspace URL and authentication

### Large Schema Discovery

For schemas with many tables, use verbose logging to monitor progress:

```bash
cloe-synthetic-data-generator discover \
  --catalog large_catalog \
  --schema large_schema \
  --verbose
```

## Next Steps

After successful table discovery:

- 📝 [Customize Configurations](configuration.md) - Fine-tune the generated YAML files
- ⚡ [Generate Data](cli-reference.md#generate) - Create synthetic data from discovered configurations
- 🎭 [Advanced Faker Usage](faker-integration.md) - Enhance faker function mappings
- 📊 [Real-world Examples](examples.md) - See discovery in action with complex schemas
