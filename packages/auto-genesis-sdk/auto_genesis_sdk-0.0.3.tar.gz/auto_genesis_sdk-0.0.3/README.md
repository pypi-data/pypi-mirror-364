# Auto Genesis SDK

![Python Version](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![PyPI Version](https://img.shields.io/pypi/v/auto-genesis-sdk?style=for-the-badge&logo=pypi)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![Imports](https://img.shields.io/badge/imports-isort-1674b1?style=for-the-badge&logo=pycharm)
![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue?style=for-the-badge&logo=python)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?style=for-the-badge&logo=pytest)

The Auto Genesis SDK serves as the unified interface for all Autonomize service SDKs. It provides a streamlined way to access and utilize various Autonomize capabilities through a single, cohesive package. This centralized approach simplifies dependency management and ensures version compatibility across all Autonomize SDKs.

## Features

The Auto Genesis SDK provides several key advantages:

- **Unified Access**: Single entry point for all Autonomize SDKs
- **Version Compatibility**: Guaranteed compatibility between different SDK modules
- **Simplified Dependencies**: Managed dependencies and requirements across all SDKs
- **Consistent Interface**: Standardized API patterns across all SDK modules
- **Integrated Configuration**: Unified configuration management for all services

## Available SDKs

Currently, the Auto Genesis SDK includes the following modules:

### Telemetry SDK
Comprehensive observability solution built on OpenTelemetry, providing:
- Unified metrics, logging, and tracing capabilities
- FastAPI auto-instrumentation
- Configurable export endpoints
- Structured logging with context
- Custom metric creation and management

## Installation

You can install the Auto Genesis SDK using pip:

```bash
pip install auto-genesis-sdk
```

Or using Poetry:

```bash
poetry add auto-genesis-sdk
```

## Quick Start

Here's how to get started with the Auto Genesis SDK:

```python
from auto_genesis_sdk import Telemetry, TelemetryConfig

# Configure telemetry service
config = TelemetryConfig(
    service_name="my-service",
    environment="production",
    otlp_endpoint="http://localhost:4317",
    version="1.0.0"
)

# Initialize telemetry
telemetry = Telemetry(config)
await telemetry.start()

try:
    # Use telemetry features
    telemetry.logging.info("Application started", {"version": "1.0.0"})

    # Create metrics
    request_counter = telemetry.metrics.create_counter(
        name="http.requests",
        description="Number of HTTP requests"
    )

    # Use tracing
    async def my_operation():
        return "result"

    result = await telemetry.tracing.create_span(
        "my-operation",
        my_operation
    )
finally:
    await telemetry.shutdown()
```


## Configuration

Each SDK module maintains its own configuration options while sharing common patterns. For example, the Telemetry SDK configuration:

```python
TelemetryConfig(
    service_name="my-service",
    environment="production",
    version="1.0.0",
    otlp_endpoint="http://localhost:4317",
    metric_interval_ms=5000,
    log_level="INFO"
)
```

## Development

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/autonomize-ai/auto-genesis-sdk.git
```

2. Install dependencies with `uv`:
```bash
uv venv
uv pip install -e .
```

3. Install pre-commit hooks:
```bash
uv pip install pre-commit
pre-commit install
```

## Testing

Run the test suite using pytest:
```bash
uv pip install pytest
pytest
```

## Contributing

We welcome contributions to the Auto Genesis SDK! Please read our [Contributing Guide](CONTRIBUTING.md) before making any changes.

When contributing, keep in mind:
- Follow the existing code style and documentation patterns
- Add tests for new features
- Update documentation as needed
- Maintain compatibility with existing SDK modules
## License

This project is licensed under the terms of the [LICENSE](LICENSE).
