# Getting Started

This guide will help you set up and run your first synthetic data generation with CLOE Synthetic Data Generator.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.12+**: The library requires Python 3.12 or later
- **Databricks Access**: Valid Databricks workspace with Unity Catalog enabled
- **Databricks Connect**: Configured connection to your Databricks workspace

!!! tip "Databricks Connect Setup"
    If you haven't set up Databricks Connect yet, follow the [official Databricks Connect documentation](https://docs.databricks.com/dev-tools/databricks-connect/index.html) to configure your environment.

## Installation

CLOE Synthetic Data Generator is available on PyPI and can be installed using your preferred Python package manager:

=== "pip"

    ```bash
    # Install the latest version
    pip install cloe-synthetic-data-generator
    ```

=== "uv (Recommended)"

    ```bash
    # Install using uv (faster and more reliable)
    uv add cloe-synthetic-data-generator
    ```

=== "pipx (Isolated Installation)"

    ```bash
    # Install as an isolated CLI tool
    pipx install cloe-synthetic-data-generator
    ```

## Verify Installation

Test your installation by checking the available commands:

```bash
# Check if the CLI is available
cloe-synthetic-data-generator --help

# Test Databricks connection
test-connection
```

!!! success "Expected Output"
    If everything is set up correctly, you should see:

    - The help message for the CLI tool
    - A successful connection message from the test-connection command

## Your First Data Generation

The easiest way to get started is to use the discovery feature to automatically generate configurations from existing tables in your Databricks workspace.

### Step 1: Discover Existing Tables

First, let's discover tables in your workspace and generate configurations automatically:

```bash
# Discover all tables in a catalog and schema
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema default \
  --num-records 100 \
  --output-dir ./my_configs
```

!!! tip "Choosing Catalog and Schema"
    Replace `main` and `default` with your actual catalog and schema names. If you're unsure what's available, check your Databricks workspace or ask your administrator.

This command will:

1. 🔍 **Connect** to your Databricks workspace
2. 📊 **Scan** all tables in the specified catalog and schema
3. 🧠 **Analyze** column names and types to suggest appropriate Faker functions
4. 📄 **Generate** YAML configuration files in the `./my_configs` directory

### Step 2: Review Generated Configurations

After discovery completes, you'll see output like:

```
Discovered Tables in main.default
┌─────────────┬─────────┬──────────────────────┐
│ Table Name  │ Columns │ Full Path            │
├─────────────┼─────────┼──────────────────────┤
│ users       │       6 │ main.default.users   │
│ orders      │       8 │ main.default.orders  │
└─────────────┴─────────┴──────────────────────┘

🎉 Successfully discovered 2 tables and generated 2 YAML configuration files
```

List the generated configurations:

```bash
# See what configurations were created
cloe-synthetic-data-generator list-configs ./my_configs --verbose
```

### Step 3: Examine and Customize a Configuration

Let's look at one of the generated configurations:

```bash
# View the contents of a generated config
cat ./my_configs/main_default_users_config.yaml
```

You'll see something like:

```yaml title="Generated Configuration Example"
name: Users Data Generation
num_records: 100
columns:
- name: user_id
  data_type: string
  nullable: false
  faker_function: uuid4          # Auto-detected as ID field
- name: first_name
  data_type: string
  nullable: false
  faker_function: first_name     # Auto-detected from column name
- name: email
  data_type: string
  nullable: true
  faker_function: email          # Auto-detected from column name
- name: created_at
  data_type: timestamp
  nullable: false
  faker_function: date_time_between
  faker_options:
    start_date: -1y
    end_date: now
target:
  catalog: main
  schema: default
  table: users
  write_mode: overwrite
```

!!! success "Smart Detection"
    Notice how the discovery process automatically:

    - Detected `user_id` as an ID field and suggested `uuid4`
    - Recognized `first_name` and suggested the appropriate Faker function
    - Identified `email` columns and suggested `email` generation
    - Set realistic date ranges for timestamp fields

### Step 4: Validate Your Configuration

Before generating data, validate the discovered configuration:

```bash
cloe-synthetic-data-generator validate-config ./my_configs/main_default_users_config.yaml
```

!!! success "Validation Success"
    You should see a green checkmark and details about your configuration including column definitions.

### Step 5: Generate the Data

Now generate synthetic data using the discovered configuration:

```bash
cloe-synthetic-data-generator generate --config ./my_configs/main_default_users_config.yaml
```

!!! info "What Happens Next"
    The tool will:

    1. 🔗 Connect to your Databricks workspace
    2. 📊 Generate 100 rows of fake data using the auto-detected Faker functions
    3. 🔄 Convert the data to a Spark DataFrame
    4. 📝 Write the data to your Unity Catalog table
    5. ✅ Verify the write was successful

### Step 6: Verify Your Data

### Step 6: Verify Your Data

You can verify the data was created by querying it in Databricks:

```sql
-- In your Databricks notebook or SQL editor
SELECT * FROM main.default.users LIMIT 10;
```

### Step 7: Customize for Your Needs (Optional)

The auto-generated configuration provides a great starting point, but you can customize it:

```yaml
# Edit the generated file to customize Faker options
- name: "email"
  data_type: "string"
  nullable: false
  faker_function: "email"
  faker_options:
    domain: "yourcompany.com"     # Use your company domain

- name: "age"
  data_type: "integer"
  nullable: true
  faker_function: "random_int"
  faker_options:
    min: 25                       # Adjust age range
    max: 65                       # for your use case
```

!!! tip "Discovery for New Tables"
    If you don't have existing tables to discover from, you can:

    1. Create a simple table with just column names and types in Databricks
    2. Use the discovery feature to generate the initial configuration
    3. Drop the empty table and use the generated config to create realistic data

## Alternative: Manual Configuration

If you prefer to create configurations manually or don't have existing tables to discover from, you can still create YAML files manually. See the [Configuration Guide](configuration.md) for detailed instructions.

## Understanding the Output

When you run the generate command, you'll see rich console output showing:

- **Configuration Details**: Summary of your target table and settings
- **Progress Indicators**: Real-time progress of each step
- **Sample Data**: Preview of the generated data
- **Success Confirmation**: Final confirmation with record counts

Example output:
```
Configuration: Users Data Generation
┌─────────────┬────────────────────────────────┐
│ Property    │ Value                          │
├─────────────┼────────────────────────────────┤
│ Target Table│ main.default.users             │
│ Columns     │ 6                              │
│ Records     │ 100                            │
│ Write Mode  │ overwrite                      │
└─────────────┴────────────────────────────────┘

✅ Connected to Databricks!
✅ Completed successfully!

🎉 Successfully generated 100 records and wrote to main.default.users
```

## Common CLI Options

Here are some useful command-line options to get you started:

### Override Record Count

```bash
# Generate 500 records instead of the configured 100
cloe-synthetic-data-generator generate --config ./my_configs/main_default_users_config.yaml --num-records 500
```

### Verbose Logging

```bash
# Enable detailed logging for troubleshooting
cloe-synthetic-data-generator generate --config ./my_configs/main_default_users_config.yaml --verbose
```

### Process Multiple Configurations

```bash
# Generate data for all discovered configurations at once
cloe-synthetic-data-generator generate --config-dir ./my_configs/
```

### Discover Specific Tables

```bash
# Use regex to discover only specific tables
cloe-synthetic-data-generator discover \
  --catalog main \
  --schema default \
  --table-regex "user.*|customer.*" \
  --output-dir ./my_configs
```

## Next Steps

Now that you've successfully generated your first synthetic dataset:

- 📚 [Learn about Configuration Options](configuration.md) - Explore all available configuration options
- 🔍 [Discover Existing Tables](table-discovery.md) - Auto-generate configs from existing tables
- ⚡ [CLI Reference](cli-reference.md) - Explore all CLI commands and options
- 🎭 [Faker Integration](faker-integration.md) - Learn about advanced Faker usage

## Troubleshooting

### Common Issues

!!! warning "Connection Issues"
    **Problem**: `Failed to connect to Databricks`

    **Solution**:

    1. Verify your Databricks Connect configuration
    2. Check your workspace URL and access token
    3. Ensure you have Unity Catalog access
    4. Run `test-connection` to diagnose connection issues

!!! warning "Permission Issues"
    **Problem**: `Permission denied to write to catalog/schema`

    **Solution**:

    1. Verify you have CREATE TABLE permissions in the target catalog/schema
    2. Check with your Databricks administrator about Unity Catalog permissions
    3. Try using a different catalog/schema you have access to

!!! warning "Configuration Errors"
    **Problem**: `Configuration validation failed`

    **Solution**:

    1. Use `validate-config` command to check your YAML syntax
    2. Ensure all required fields are present
    3. Check data types match supported Spark SQL types
    4. Verify faker function names are correct

### Getting Help

If you encounter issues:

1. **Check the logs**: Use `--verbose` flag for detailed error information
2. **Validate configuration**: Use `validate-config` command
3. **Test connection**: Use `test-connection` command
4. **Review examples**: Check the sample configurations in the repository
