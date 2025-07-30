# CLI Reference

The CLOE Synthetic Data Generator provides a powerful command-line interface with several commands for data generation, configuration validation, and table discovery.

## Command Overview

| Command | Description |
|---------|-------------|
| [`generate`](#generate) | Generate synthetic data from YAML configuration |
| [`test-connection`](#test-connection) | Test Databricks Connect connectivity |
| [`list-configs`](#list-configs) | List all configurations in a directory |
| [`validate-config`](#validate-config) | Validate a YAML configuration file |
| [`discover`](#discover) | Discover existing tables and generate configs |

## Global Options

All commands support these global options:

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--verbose` | `-v` | Enable verbose (debug) logging |

## Commands

### `generate`

Generate synthetic data from YAML configuration files and write to Unity Catalog.

#### Usage

=== "Single Configuration"
    ```bash
    cloe-synthetic-data-generator generate --config CONFIG_FILE
    ```

=== "Multiple Configurations"
    ```bash
    cloe-synthetic-data-generator generate --config-dir CONFIG_DIRECTORY
    ```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--config` | `-c` | Path | Path to YAML configuration file | None |
| `--config-dir` | `-d` | Path | Directory containing YAML files | None |
| `--num-records` | `-n` | Integer | Override number of records from config | None |
| `--verbose` | `-v` | Flag | Enable verbose logging | False |

!!! warning "Mutual Exclusivity"
    You must specify either `--config` OR `--config-dir`, but not both.

#### Examples

**Generate from single configuration:**
```bash
cloe-synthetic-data-generator generate --config user_data.yaml
```

**Generate from single configuration with record override:**
```bash
cloe-synthetic-data-generator generate \
  --config user_data.yaml \
  --num-records 5000
```

**Generate from all configurations in directory:**
```bash
cloe-synthetic-data-generator generate --config-dir ./configs/
```

**Generate with verbose logging:**
```bash
cloe-synthetic-data-generator generate \
  --config user_data.yaml \
  --verbose
```

#### Sample Output

```
Configuration: User Data Generation
┌─────────────┬────────────────────────────────┐
│ Property    │ Value                          │
├─────────────┼────────────────────────────────┤
│ Target Table│ main.test_data.users           │
│ Columns     │ 6                              │
│ Records     │ 1000                           │
│ Write Mode  │ overwrite                      │
└─────────────┴────────────────────────────────┘

⠋ Connecting to Databricks...
✅ Connected to Databricks!

Sample generated data:
+--------------------+----------+---------+--------------------+----+--------------------+
|             user_id|first_name|last_name|               email| age|          created_at|
+--------------------+----------+---------+--------------------+----+--------------------+
|550e8400-e29b-41d4-...|      John|      Doe|john.doe@email.com|  34|2023-05-15 14:30:22|
+--------------------+----------+---------+--------------------+----+--------------------+

⠋ Writing to Unity Catalog...
⠋ Verifying write...
✅ Completed successfully!

🎉 Successfully generated 1000 records and wrote to main.test_data.users
```

### `test-connection`

Test the connection to your Databricks workspace using Databricks Connect.

#### Usage

```bash
test-connection
```

#### Examples

```bash
test-connection
```

#### Sample Output

```
⠋ Testing Databricks Connect connection...
✅ Connected! Reading sample data...
✅ Connection test completed!

✅ Successfully connected to Databricks!
Sample table 'samples.nyctaxi.trips' contains 1,547,741 rows

Sample data:
+--------+--------------------+-----+---+-----+
|vendor_id|pickup_datetime     |...|
+--------+--------------------+-----+---+-----+
|       2|2016-12-31 15:15:00 |...|
+--------+--------------------+-----+---+-----+
```

!!! tip "Troubleshooting Connection Issues"
    If the connection fails, check:

    - Databricks Connect configuration
    - Workspace URL and access token
    - Network connectivity
    - Unity Catalog access permissions

### `list-configs`

List all YAML configuration files in a directory with summary information.

#### Usage

```bash
cloe-synthetic-data-generator list-configs DIRECTORY [OPTIONS]
```

#### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `DIRECTORY` | Path | Directory containing YAML configuration files |

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Show detailed configuration information | False |

#### Examples

**Basic listing:**
```bash
cloe-synthetic-data-generator list-configs ./configs/
```

**Detailed listing:**
```bash
cloe-synthetic-data-generator list-configs ./configs/ --verbose
```

#### Sample Output

=== "Basic Output"
    ```
    Configurations in ./configs/
    ┌──────────────────┬─────────────────────────────┬─────────┬─────────┐
    │ Name             │ Target Table                │ Records │ Columns │
    ├──────────────────┼─────────────────────────────┼─────────┼─────────┤
    │ User Data Gen    │ main.test_data.users        │    1000 │       6 │
    │ Employee Data    │ main.hr_data.employees      │    5000 │      12 │
    │ Product Catalog  │ main.inventory.products     │   10000 │       8 │
    └──────────────────┴─────────────────────────────┴─────────┴─────────┘

    Found 3 configuration(s)
    ```

=== "Verbose Output"
    ```
    Detailed Configurations in ./configs/
    ┌────────────┬─────────────────────┬─────────┬─────────┬────────────┬─────────────────────┐
    │ Name       │ Target              │ Records │ Columns │ Write Mode │ Column Names        │
    ├────────────┼─────────────────────┼─────────┼─────────┼────────────┼─────────────────────┤
    │ User Data  │ main.test_data.users│    1000 │       6 │ overwrite  │ user_id, first_name,│
    │            │                     │         │         │            │ last_name, email... │
    └────────────┴─────────────────────┴─────────┴─────────┴────────────┴─────────────────────┘
    ```

### `validate-config`

Validate a YAML configuration file for syntax errors and configuration completeness.

#### Usage

```bash
cloe-synthetic-data-generator validate-config CONFIG_FILE
```

#### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `CONFIG_FILE` | Path | Path to YAML configuration file to validate |

#### Examples

```bash
cloe-synthetic-data-generator validate-config user_data.yaml
```

#### Sample Output

=== "Valid Configuration"
    ```
    ✅ Configuration 'user_data.yaml' is valid!

    Configuration Details
    ┌─────────────┬─────────────────────────────┐
    │ Property    │ Value                       │
    ├─────────────┼─────────────────────────────┤
    │ Name        │ User Data Generation        │
    │ Target Table│ main.test_data.users        │
    │ Write Mode  │ overwrite                   │
    │ Records     │ 1000                        │
    │ Batch Size  │ 1000                        │
    │ Columns     │ 6                           │
    └─────────────┴─────────────────────────────┘

    Column Definitions
    ┌─────────────┬───────────┬──────────┬─────────────────┐
    │ Name        │ Type      │ Nullable │ Faker Function  │
    ├─────────────┼───────────┼──────────┼─────────────────┤
    │ user_id     │ string    │ No       │ uuid4           │
    │ first_name  │ string    │ No       │ first_name      │
    │ last_name   │ string    │ No       │ last_name       │
    │ email       │ string    │ No       │ email           │
    │ age         │ integer   │ Yes      │ random_int      │
    │ created_at  │ timestamp │ No       │ date_time_between│
    └─────────────┴───────────┴──────────┴─────────────────┘
    ```

=== "Invalid Configuration"
    ```
    ❌ Configuration validation failed: 1 validation error for DataGenConfig
    target
      Field required [type=missing, input_value={'name': 'Test Config', 'columns': [...]}, input_loc=('target',)]
    ```

### `discover`

Discover existing tables in a Databricks catalog/schema and automatically generate YAML configuration files.

#### Usage

```bash
cloe-synthetic-data-generator discover [OPTIONS]
```

#### Required Options

| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--catalog` | `-c` | String | Target catalog name in Unity Catalog |
| `--schema` | `-s` | String | Target schema name within the catalog |

#### Optional Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--table-regex` | `-t` | String | Regex pattern to filter table names | None (all tables) |
| `--output-dir` | `-o` | Path | Directory to write generated YAML files | `./discovered_configs` |
| `--num-records` | `-n` | Integer | Records to generate per table | 1000 |
| `--write-mode` | `-w` | String | Write mode for tables | "overwrite" |
| `--verbose` | `-v` | Flag | Enable verbose logging | False |

#### Examples

**Discover all tables in a schema:**
```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data
```

**Discover with custom output directory:**
```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data \
  --output-dir ./my_configs/
```

**Discover tables matching a pattern:**
```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data \
  --table-regex "employee.*"
```

**Discover with custom record count:**
```bash
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema hr_data \
  --num-records 5000 \
  --write-mode append
```

#### Sample Output

```
⠋ Connecting to Databricks...
✅ Connected to Databricks!
⠋ Found 3 tables...

Discovered Tables in main.hr_data
┌─────────────┬─────────┬────────────────────────┐
│ Table Name  │ Columns │ Full Path              │
├─────────────┼─────────┼────────────────────────┤
│ employees   │      12 │ main.hr_data.employees │
│ departments │       4 │ main.hr_data.departments│
│ salaries    │       6 │ main.hr_data.salaries  │
└─────────────┴─────────┴────────────────────────┘

⠋ Generating YAML configurations...
⠋ Writing YAML files...
✅ Discovery completed!

Discovery Results
┌─────────────────────┬─────────────────────────────┐
│ Property            │ Value                       │
├─────────────────────┼─────────────────────────────┤
│ Tables Discovered   │ 3                           │
│ Configs Generated   │ 3                           │
│ Output Directory    │ ./discovered_configs        │
│ Records per Table   │ 1000                        │
│ Write Mode          │ overwrite                   │
└─────────────────────┴─────────────────────────────┘

Generated Configuration Files
┌──────────────────────────────────────┬────────────────────────┐
│ File                                 │ Table                  │
├──────────────────────────────────────┼────────────────────────┤
│ main_hr_data_employees_config.yaml   │ main.hr_data.employees │
│ main_hr_data_departments_config.yaml │ main.hr_data.departments│
│ main_hr_data_salaries_config.yaml    │ main.hr_data.salaries  │
└──────────────────────────────────────┴────────────────────────┘

🎉 Successfully discovered 3 tables and generated 3 YAML configuration files in ./discovered_configs
```

#### Generated File Names

The discover command generates files using this naming pattern:
```
{catalog}_{schema}_{table_name}_config.yaml
```

Examples:
- `main_hr_data_employees_config.yaml`
- `dev_test_users_config.yaml`
- `prod_analytics_events_config.yaml`

## Command Combinations

You can combine commands in workflows:

### Development Workflow

```bash
# 1. Discover existing tables
cloe-synthetic-data-generator discover --catalog main --schema test_data

# 2. Validate generated configurations
cloe-synthetic-data-generator list-configs ./discovered_configs --verbose

# 3. Validate specific configuration
cloe-synthetic-data-generator validate-config ./discovered_configs/main_test_data_users_config.yaml

# 4. Generate small test dataset
cloe-synthetic-data-generator generate \
  --config ./discovered_configs/main_test_data_users_config.yaml \
  --num-records 10

# 5. Generate full dataset
cloe-synthetic-data-generator generate \
  --config-dir ./discovered_configs
```

### Production Workflow

```bash
# 1. Test connection
test-connection

# 2. Validate all configurations
for config in configs/*.yaml; do
  cloe-synthetic-data-generator validate-config "$config"
done

# 3. Generate data with verbose logging
cloe-synthetic-data-generator generate \
  --config-dir ./configs \
  --verbose
```

## Error Handling

The CLI provides detailed error messages and appropriate exit codes:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error (configuration, connection, etc.) |

### Common Error Messages

!!! failure "Configuration Errors"
    ```
    ❌ Configuration validation failed: Field required [type=missing, input_value=...]
    ```
    **Solution**: Check YAML syntax and ensure all required fields are present.

!!! failure "Connection Errors"
    ```
    ❌ Failed to connect to Databricks: [CONNECTION_ERROR]
    ```
    **Solution**: Verify Databricks Connect setup and credentials.

!!! failure "Permission Errors"
    ```
    ❌ Permission denied to write to catalog/schema
    ```
    **Solution**: Check Unity Catalog permissions for the target location.

!!! failure "File Not Found"
    ```
    ❌ Configuration file not found: path/to/config.yaml
    ```
    **Solution**: Verify file path and ensure file exists.

## Performance Tips

### Large Datasets

For generating large datasets:

```bash
# Use larger batch sizes (reduce memory pressure)
# Edit your config file to set: batch_size: 10000

# Monitor progress with verbose logging
cloe-synthetic-data-generator generate \
  --config large_dataset.yaml \
  --verbose
```

### Multiple Configurations

For processing many configurations:

```bash
# Place all configs in a directory
cloe-synthetic-data-generator generate --config-dir ./configs/

# This is more efficient than running generate multiple times
```

### Resource Management

Monitor resource usage:

```bash
# Check table sizes after generation
# In Databricks SQL:
SELECT
    table_catalog,
    table_schema,
    table_name,
    table_rows
FROM system.information_schema.tables
WHERE table_catalog = 'main'
    AND table_schema = 'your_schema';
```

## Next Steps

- 📚 [Configuration Guide](configuration.md) - Learn about YAML configuration options
- 🔍 [Table Discovery](table-discovery.md) - Deep dive into auto-discovery features
- 🎭 [Faker Integration](faker-integration.md) - Explore advanced Faker capabilities
- 📊 [Examples](examples.md) - See real-world usage examples
