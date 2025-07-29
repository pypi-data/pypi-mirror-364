# LLM Wrapper

A comprehensive Python wrapper for Large Language Models with database integration and usage tracking. Supports multiple database backends (PostgreSQL, MySQL, MongoDB) and provides detailed analytics for LLM usage.

## Features

- 🚀 **Easy Integration**: Simple API for interacting with various LLM services
- 📊 **Usage Tracking**: Comprehensive logging and analytics for all LLM requests
- 💾 **Multi-Database Support**: PostgreSQL, MySQL, and MongoDB backends
- ⚡ **High Performance**: Optimized for concurrent requests and high throughput
- 🔒 **Secure**: Built-in security features and API key management
- 📈 **Analytics**: Detailed usage statistics and reporting
- 🐳 **Production Ready**: Robust error handling and logging

## Installation

### Basic Installation

```bash
pip install llm-wrapper
```

### Development Installation

```bash
pip install llm-wrapper[dev]
```

### With All Optional Dependencies

```bash
pip install llm-wrapper[dev,test,docs]
```

## Quick Start

### Basic Usage

```python
from llm_wrapper import LLMWrapper

# Configure your database
db_config = {
    'type': 'postgresql',
    'dbname': 'llm_wrapper_db',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}

# Initialize the wrapper
wrapper = LLMWrapper(
    service_url="https://your-llm-service.com",
    api_key="your-api-key",
    db_config=db_config,
    deployment_name="gpt-4",
    api_version="2024-12-01-preview",
    default_model='gpt-4'
)

# Send a request
response = wrapper.send_request(
    input_text="What are the benefits of renewable energy?",
    customer_id=1,
    organization_id=1,
    temperature=0.7,
    max_tokens=2000
)

print(f"Response: {response['output_text']}")
print(f"Tokens used: {response['total_tokens']}")

# Get usage statistics
stats = wrapper.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")

# Clean up
wrapper.close()
```

### Environment Variables

Create a `.env` file for easier configuration:

```bash
# Database Configuration
DATABASE_TYPE=postgresql
DB_NAME=llm_wrapper_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# LLM Service Configuration
LLM_SERVICE_URL=https://your-llm-service.com
LLM_API_KEY=your-api-key
LLM_DEPLOYMENT_NAME=gpt-4
LLM_API_VERSION=2024-12-01-preview
```

## Database Configurations

### PostgreSQL

```python
db_config = {
    'type': 'postgresql',
    'dbname': 'llm_wrapper_db',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
```

### MySQL

```python
db_config = {
    'type': 'mysql',
    'dbname': 'llm_wrapper_db',
    'user': 'root',
    'password': 'your_password',
    'host': 'localhost',
    'port': '3306'
}
```

### MongoDB

```python
db_config = {
    'type': 'mongodb',
    'dbname': 'llm_wrapper_db',
    'host': 'localhost',
    'port': 27017,
    'user': 'your_user',
    'password': 'your_password'
}
```

### MongoDB with Connection String

```python
db_config = {
    'type': 'mongodb',
    'dbname': 'llm_wrapper_db',
    'connection_string': 'mongodb://localhost:27017/'
}
```


### Usage Analytics

```python
# Get overall statistics
stats = wrapper.get_usage_stats()

# Get customer-specific statistics
customer_stats = wrapper.get_usage_stats(customer_id=1)

# Get organization-specific statistics
org_stats = wrapper.get_usage_stats(organization_id=1)

# Get statistics for a specific time period
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=7)
end_date = datetime.now()

period_stats = wrapper.get_usage_stats(
    start_date=start_date,
    end_date=end_date
)
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_url` | str | Required | LLM service endpoint URL |
| `api_key` | str | Required | API key for authentication |
| `db_config` | dict | Required | Database configuration |
| `deployment_name` | str | None | LLM deployment name |
| `api_version` | str | None | API version |
| `default_model` | str | 'gpt-3.5-turbo' | Default model to use |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Maximum retry attempts |
| `retry_delay` | float | 1.0 | Delay between retries |

## API Reference

### Core Methods

#### `send_request(input_text, customer_id, organization_id, **kwargs)`

Send a request to the LLM service.

**Parameters:**
- `input_text` (str): The prompt text
- `customer_id` (int): Customer identifier
- `organization_id` (int): Organization identifier
- `temperature` (float, optional): Sampling temperature (0.0-1.0)
- `max_tokens` (int, optional): Maximum tokens in response
- `model` (str, optional): Model to use for this request

**Returns:**
- `dict`: Response containing output text, token counts, and metadata

#### `get_usage_stats(**filters)`

Get usage statistics with optional filtering.

**Parameters:**
- `customer_id` (int, optional): Filter by customer
- `organization_id` (int, optional): Filter by organization
- `start_date` (datetime, optional): Start date for filtering
- `end_date` (datetime, optional): End date for filtering

**Returns:**
- `dict`: Usage statistics including request counts, token usage, and performance metrics

#### `close()`

Close database connections and clean up resources.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Built with love for the AI/ML community

---