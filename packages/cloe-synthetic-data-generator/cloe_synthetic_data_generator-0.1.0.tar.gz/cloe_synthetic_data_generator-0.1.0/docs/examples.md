# Examples

This section provides practical examples of CLOE Synthetic Data Generator configurations for common use cases. Each example demonstrates specific patterns and best practices.

## Quick Examples by Domain

### User Management System

A simple user table with essential fields:

```yaml title="user_data.yaml"
name: "User Management Data"
target:
  catalog: "main"
  schema: "app_data"
  table: "users"
  write_mode: "overwrite"

num_records: 1000
batch_size: 500

columns:
  - name: "user_id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"

  - name: "username"
    data_type: "string"
    nullable: false
    faker_function: "user_name"

  - name: "email"
    data_type: "string"
    nullable: false
    faker_function: "email"

  - name: "first_name"
    data_type: "string"
    nullable: false
    faker_function: "first_name"

  - name: "last_name"
    data_type: "string"
    nullable: false
    faker_function: "last_name"

  - name: "age"
    data_type: "integer"
    nullable: true
    faker_function: "random_int"
    faker_options:
      min: 18
      max: 80

  - name: "is_active"
    data_type: "boolean"
    nullable: false
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 85

  - name: "created_at"
    data_type: "timestamp"
    nullable: false
    faker_function: "date_time_between"
    faker_options:
      start_date: "-2y"
      end_date: "now"
```

### E-commerce Product Catalog

Product data with SKUs, pricing, and categories:

```yaml title="product_catalog.yaml"
name: "Product Catalog Data"
target:
  catalog: "ecommerce"
  schema: "inventory"
  table: "products"
  write_mode: "overwrite"

num_records: 5000
batch_size: 1000

columns:
  - name: "product_id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"

  - name: "sku"
    data_type: "string"
    nullable: false
    faker_function: "bothify"
    faker_options:
      text: "PRD-####-???"

  - name: "product_name"
    data_type: "string"
    nullable: false
    faker_function: "catch_phrase"

  - name: "category"
    data_type: "string"
    nullable: false
    faker_function: "random_element"
    faker_options:
      elements: ["Electronics", "Clothing", "Home & Garden", "Books", "Sports"]

  - name: "price"
    data_type: "double"
    nullable: false
    faker_function: "pyfloat"
    faker_options:
      left_digits: 3
      right_digits: 2
      positive: true
      min_value: 5.00
      max_value: 999.99

  - name: "in_stock"
    data_type: "boolean"
    nullable: false
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 90

  - name: "rating"
    data_type: "double"
    nullable: true
    faker_function: "pyfloat"
    faker_options:
      left_digits: 1
      right_digits: 1
      positive: true
      min_value: 1.0
      max_value: 5.0

  - name: "created_at"
    data_type: "timestamp"
    nullable: false
    faker_function: "date_time_between"
    faker_options:
      start_date: "-1y"
      end_date: "now"
```

### Employee HR Data

Human resources data with departments and roles:

```yaml title="employee_data.yaml"
name: "Employee HR Data"
target:
  catalog: "main"
  schema: "hr"
  table: "employees"
  write_mode: "overwrite"

num_records: 2000
batch_size: 500

columns:
  - name: "employee_id"
    data_type: "string"
    nullable: false
    faker_function: "bothify"
    faker_options:
      text: "EMP-######"

  - name: "first_name"
    data_type: "string"
    nullable: false
    faker_function: "first_name"

  - name: "last_name"
    data_type: "string"
    nullable: false
    faker_function: "last_name"

  - name: "email"
    data_type: "string"
    nullable: false
    faker_function: "email"

  - name: "department"
    data_type: "string"
    nullable: false
    faker_function: "random_element"
    faker_options:
      elements: ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]

  - name: "job_title"
    data_type: "string"
    nullable: false
    faker_function: "job"

  - name: "salary"
    data_type: "double"
    nullable: false
    faker_function: "pyfloat"
    faker_options:
      left_digits: 6
      right_digits: 2
      positive: true
      min_value: 35000.00
      max_value: 200000.00

  - name: "hire_date"
    data_type: "date"
    nullable: false
    faker_function: "date_between"
    faker_options:
      start_date: "-10y"
      end_date: "today"

  - name: "is_manager"
    data_type: "boolean"
    nullable: false
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 15
```

### Financial Transactions

Banking transaction data with account information:

```yaml title="transactions.yaml"
name: "Financial Transactions"
target:
  catalog: "finance"
  schema: "banking"
  table: "transactions"
  write_mode: "overwrite"

num_records: 10000
batch_size: 2000

columns:
  - name: "transaction_id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"

  - name: "account_number"
    data_type: "string"
    nullable: false
    faker_function: "bothify"
    faker_options:
      text: "####-####-####"

  - name: "transaction_type"
    data_type: "string"
    nullable: false
    faker_function: "random_element"
    faker_options:
      elements: ["deposit", "withdrawal", "transfer", "payment"]

  - name: "amount"
    data_type: "double"
    nullable: false
    faker_function: "pyfloat"
    faker_options:
      left_digits: 6
      right_digits: 2
      positive: false  # Allow negative values for withdrawals
      min_value: -5000.00
      max_value: 10000.00

  - name: "currency"
    data_type: "string"
    nullable: false
    faker_function: "currency_code"

  - name: "description"
    data_type: "string"
    nullable: true
    faker_function: "sentence"
    faker_options:
      nb_words: 6

  - name: "transaction_date"
    data_type: "timestamp"
    nullable: false
    faker_function: "date_time_between"
    faker_options:
      start_date: "-90d"
      end_date: "now"

  - name: "is_approved"
    data_type: "boolean"
    nullable: false
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 95
```

## Common Patterns

### Weighted Distributions

Create realistic data distributions using weighted choices:

```yaml
columns:
  - name: "subscription_tier"
    data_type: "string"
    faker_function: "random_choices"
    faker_options:
      elements: ["free", "basic", "premium", "enterprise"]
      weights: [60, 25, 12, 3]  # 60% free, 25% basic, 12% premium, 3% enterprise
      length: 1
```

### Custom Identifier Patterns

Generate domain-specific identifiers:

```yaml
columns:
  # Order numbers: ORD-2024-001234
  - name: "order_number"
    data_type: "string"
    faker_function: "bothify"
    faker_options:
      text: "ORD-####-######"

  # License plates: ABC-1234
  - name: "license_plate"
    data_type: "string"
    faker_function: "bothify"
    faker_options:
      text: "???-####"

  # Product codes: PROD-A1B2C3
  - name: "product_code"
    data_type: "string"
    faker_function: "hexify"
    faker_options:
      text: "PROD-^^^^^^"
      upper: true
```

### Realistic Date Ranges

Generate dates that make business sense:

```yaml
columns:
  # Account creation (past 3 years)
  - name: "account_created"
    data_type: "timestamp"
    faker_function: "date_time_between"
    faker_options:
      start_date: "-3y"
      end_date: "now"

  # Last login (within last 30 days for active users)
  - name: "last_login"
    data_type: "timestamp"
    faker_function: "date_time_between"
    faker_options:
      start_date: "-30d"
      end_date: "now"

  # Birth dates (18-65 years old)
  - name: "birth_date"
    data_type: "date"
    faker_function: "date_between"
    faker_options:
      start_date: "-65y"
      end_date: "-18y"
```

### Correlated Boolean Fields

Create logical relationships between boolean fields:

```yaml
columns:
  # 90% of accounts are active
  - name: "is_active"
    data_type: "boolean"
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 90

  # Only 20% of accounts are premium (subset of active)
  - name: "is_premium"
    data_type: "boolean"
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 20

  # Most accounts are email verified (85%)
  - name: "email_verified"
    data_type: "boolean"
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 85
```

## Testing and Development Workflows

### Small Test Dataset

For development and testing:

```yaml
name: "Test Dataset"
target:
  catalog: "dev"
  schema: "testing"
  table: "sample_data"
  write_mode: "overwrite"

num_records: 100      # Small dataset for quick testing
batch_size: 50        # Small batches for fast iteration

columns:
  - name: "id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"

  - name: "name"
    data_type: "string"
    nullable: false
    faker_function: "name"

  - name: "status"
    data_type: "string"
    nullable: false
    faker_function: "random_element"
    faker_options:
      elements: ["active", "inactive"]
```

### Large Production Dataset

For production-like data volumes:

```yaml
name: "Production Scale Dataset"
target:
  catalog: "main"
  schema: "analytics"
  table: "large_dataset"
  write_mode: "overwrite"

num_records: 1000000   # 1 million records
batch_size: 10000      # Large batches for efficiency

columns:
  - name: "id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"          # Fast function for large datasets

  - name: "category"
    data_type: "string"
    nullable: false
    faker_function: "random_element"  # Fast categorical data
    faker_options:
      elements: ["A", "B", "C", "D"]

  - name: "value"
    data_type: "integer"
    nullable: false
    faker_function: "random_int"     # Fast numeric generation
    faker_options:
      min: 1
      max: 1000
```

## Next Steps

For more complex scenarios:

- 📚 [Configuration Guide](configuration.md) - Complete YAML reference
- �� [Faker Integration](faker-integration.md) - Advanced Faker patterns
- 🔍 [Table Discovery](table-discovery.md) - Auto-generate configurations
- 🌐 [Faker Documentation](https://faker.readthedocs.io/) - Full provider library

## Tips for Creating Examples

1. **Start Simple**: Begin with basic data types and add complexity gradually
2. **Use Realistic Patterns**: Match real-world data distributions and formats
3. **Consider Performance**: For large datasets, prefer faster Faker functions
4. **Test Incrementally**: Start with small `num_records` and increase gradually
5. **Document Business Logic**: Add comments explaining domain-specific choices
