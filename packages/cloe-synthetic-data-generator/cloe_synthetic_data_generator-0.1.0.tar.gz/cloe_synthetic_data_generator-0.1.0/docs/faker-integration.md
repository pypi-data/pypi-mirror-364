# Faker Integration

CLOE Synthetic Data Generator leverages the powerful [Faker library](https://faker.readthedocs.io/) to generate realistic synthetic data. This guide covers the essential concepts and patterns for using Faker effectively.

## What is Faker?

Faker is a Python library that generates fake data for you. It provides over 100 data providers covering everything from personal information to business data, addresses, and more.

!!! tip "Complete Faker Documentation"
    For the full list of available providers and methods, visit the [official Faker documentation](https://faker.readthedocs.io/en/master/providers.html). This guide covers the core concepts - refer to the official docs for specific provider details.

## Basic Usage

### Simple Functions

Most Faker functions work without any options:

```yaml
columns:
  - name: "first_name"
    data_type: "string"
    faker_function: "first_name"    # Generates: "John", "Sarah", "Michael"

  - name: "email"
    data_type: "string"
    faker_function: "email"         # Generates: "john@example.com"

  - name: "company"
    data_type: "string"
    faker_function: "company"       # Generates: "Smith Inc", "Johnson LLC"
```

### Functions with Options

Customize output using `faker_options`:

```yaml
columns:
  - name: "age"
    data_type: "integer"
    faker_function: "random_int"
    faker_options:
      min: 18
      max: 80

  - name: "description"
    data_type: "string"
    faker_function: "text"
    faker_options:
      max_nb_chars: 200

  - name: "salary"
    data_type: "double"
    faker_function: "pyfloat"
    faker_options:
      left_digits: 5
      right_digits: 2
      positive: true
      min_value: 30000
      max_value: 150000
```

## Core Faker Patterns

### Custom Choices

Create domain-specific data using `random_element`:

```yaml
columns:
  - name: "status"
    data_type: "string"
    faker_function: "random_element"
    faker_options:
      elements: ["active", "inactive", "pending", "suspended"]

  - name: "priority"
    data_type: "string"
    faker_function: "random_element"
    faker_options:
      elements: ["low", "medium", "high", "critical"]
```

### Pattern-Based Generation

Use `bothify` and `hexify` for specific patterns:

```yaml
columns:
  # Product SKUs: "PRD-1234-ABC"
  - name: "sku"
    data_type: "string"
    faker_function: "bothify"
    faker_options:
      text: "PRD-####-???"

  # License keys: "XXXX-XXXX-XXXX-XXXX"
  - name: "license_key"
    data_type: "string"
    faker_function: "hexify"
    faker_options:
      text: "^^^^-^^^^-^^^^-^^^^"
      upper: true
```

### Date and Time Patterns

Generate dates within specific ranges:

```yaml
columns:
  - name: "created_at"
    data_type: "timestamp"
    faker_function: "date_time_between"
    faker_options:
      start_date: "-1y"    # 1 year ago
      end_date: "now"      # Current time

  - name: "birth_date"
    data_type: "date"
    faker_function: "date_between"
    faker_options:
      start_date: "-65y"   # 65 years ago
      end_date: "-18y"     # 18 years ago
```

### Boolean with Probability

Control boolean distribution:

```yaml
columns:
  # 80% chance of being true
  - name: "is_active"
    data_type: "boolean"
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 80

  # 20% chance of being true  
  - name: "is_premium"
    data_type: "boolean"
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 20
```

## Common Providers by Category

!!! info "Provider Categories"
    Faker organizes providers into categories. Here are the most commonly used ones:

    **Personal Data**: `first_name`, `last_name`, `name`, `email`, `phone_number`, `ssn`
    
    **Address**: `address`, `city`, `state`, `country`, `zipcode`, `latitude`, `longitude`
    
    **Business**: `company`, `job`, `catch_phrase`, `bs`
    
    **Finance**: `credit_card_number`, `iban`, `currency_code`
    
    **Internet**: `user_name`, `domain_name`, `url`, `ipv4`, `mac_address`
    
    **Text**: `sentence`, `paragraph`, `text`, `words`
    
    **Identifiers**: `uuid4`, `ean13`, `isbn13`
    
    **Dates**: `date`, `date_between`, `date_time`, `date_time_between`

For detailed documentation of each provider and their options, see the [Faker Providers Documentation](https://faker.readthedocs.io/en/master/providers.html).

## Localization

Faker supports multiple locales for region-specific data:

```yaml
columns:
  # US-specific phone numbers
  - name: "us_phone"
    data_type: "string"
    faker_function: "phone_number"
    faker_options:
      locale: "en_US"

  # German addresses  
  - name: "de_address"
    data_type: "string"
    faker_function: "address"
    faker_options:
      locale: "de_DE"
```

Available locales include `en_US`, `de_DE`, `fr_FR`, `es_ES`, `ja_JP`, and many more. See the [Faker Localization Documentation](https://faker.readthedocs.io/en/master/locales.html) for the complete list.

## Advanced Patterns

### Weighted Random Choices

Use different probabilities for choices:

```yaml
columns:
  - name: "plan_type"
    data_type: "string"
    faker_function: "random_choices"
    faker_options:
      elements: ["free", "basic", "premium", "enterprise"]
      weights: [50, 30, 15, 5]    # 50% free, 30% basic, etc.
      length: 1
```

### Complex Numeric Patterns

Generate numbers with specific characteristics:

```yaml
columns:
  # Prices with 2 decimal places ($1.00 to $999.99)
  - name: "price"
    data_type: "double"
    faker_function: "pyfloat"
    faker_options:
      left_digits: 3
      right_digits: 2
      positive: true
      min_value: 1.00
      max_value: 999.99

  # Percentages (0.0 to 1.0)
  - name: "completion_rate"
    data_type: "double"
    faker_function: "pyfloat"
    faker_options:
      left_digits: 1
      right_digits: 3
      positive: true
      min_value: 0.0
      max_value: 1.0
```

## Performance Tips

### Function Performance

Some Faker functions are faster than others:

- **Fast**: `uuid4`, `random_int`, `boolean`, `random_element`
- **Medium**: `first_name`, `email`, `company`, `address`  
- **Slower**: `paragraph`, `text` (with large content), complex pattern matching

For very large datasets (millions of records), prefer faster functions when possible.

### Best Practices

1. **Use simple functions** for high-volume generation
2. **Increase `batch_size`** in your configuration for better performance
3. **Cache repeated patterns** by using `random_element` with predefined lists
4. **Monitor memory usage** when generating large text content

## Complete Example

Here's a realistic configuration combining multiple patterns:

```yaml
name: "User Management System"
target:
  catalog: "main"
  schema: "user_data"
  table: "users"
  write_mode: "overwrite"

num_records: 10000
batch_size: 1000

columns:
  # Unique identifier
  - name: "user_id"
    data_type: "string"
    nullable: false
    faker_function: "uuid4"

  # Personal information
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

  # Demographics
  - name: "age"
    data_type: "integer"
    nullable: true
    faker_function: "random_int"
    faker_options:
      min: 18
      max: 80

  - name: "country"
    data_type: "string"
    nullable: false
    faker_function: "country_code"

  # Account details
  - name: "account_type"
    data_type: "string"
    nullable: false
    faker_function: "random_element"
    faker_options:
      elements: ["free", "premium", "enterprise"]

  - name: "is_active"
    data_type: "boolean"
    nullable: false
    faker_function: "boolean"
    faker_options:
      chance_of_getting_true: 85

  # Timestamps
  - name: "created_at"
    data_type: "timestamp"
    nullable: false
    faker_function: "date_time_between"
    faker_options:
      start_date: "-2y"
      end_date: "now"

  - name: "last_login"
    data_type: "timestamp"
    nullable: true
    faker_function: "date_time_between"
    faker_options:
      start_date: "-30d"
      end_date: "now"
```

## Next Steps

- 📚 [Configuration Guide](configuration.md) - Learn about complete YAML structure
- 🔍 [Table Discovery](table-discovery.md) - Auto-discover and generate configs
- 📊 [Examples](examples.md) - See domain-specific examples
- 🌐 [Faker Documentation](https://faker.readthedocs.io/) - Complete provider reference
