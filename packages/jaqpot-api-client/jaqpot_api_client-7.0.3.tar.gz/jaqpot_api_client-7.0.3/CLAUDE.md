# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python client library for the Jaqpot API, auto-generated from OpenAPI specifications. The Jaqpot API is a modern RESTful API for model management and prediction services, built using Spring Boot and Kotlin.

## Architecture

This project follows a standard OpenAPI-generated Python client structure:

- **src/jaqpot_api_client/**: Main package containing the generated client code
  - **api/**: API endpoint classes (ApiKeysApi, AuthApi, DatasetApi, ModelApi, etc.)
  - **models/**: Data model classes auto-generated from OpenAPI schemas
  - **api_client.py**: Core ApiClient class handling HTTP communication
  - **configuration.py**: Configuration management for the client
  - **exceptions.py**: Custom exception classes for API errors

- **etc/**: Contains build and generation scripts
  - **openapi-generate.sh**: Script to regenerate the client from OpenAPI specs

## Common Development Commands

### OpenAPI Client Generation
```bash
# Regenerate the API client from the latest OpenAPI specification
./etc/openapi-generate.sh
```

This script:
- Installs openapi-generator-cli if not present
- Fetches the latest OpenAPI spec from the Jaqpot API repository
- Generates Python client code in a temporary directory
- Copies the generated code to src/jaqpot_api_client/

### Building and Packaging
The project uses Hatch as the build system (defined in pyproject.toml):

```bash
# Build the package
python -m build

# Install in development mode
pip install -e .
```

### Type Checking
```bash
# Run mypy type checking (if hatch is available)
hatch run types:check
```

### Testing
```bash
# Run tests (standard pytest pattern)
python -m pytest tests/
```

## Key Implementation Details

- The package uses modern Python packaging with pyproject.toml
- Supports Python 3.8+ 
- Generated code includes type hints via py.typed marker
- No external dependencies in the base package (self-contained client)
- Uses standard HTTP libraries for REST API communication

## Generated Code Warning

Most files in src/jaqpot_api_client/ are auto-generated and should not be edited manually. The generation script will overwrite any manual changes. The only exception is typically configuration or custom wrapper code that might be added outside the generated directories.

## Version Management

Version is managed in src/jaqpot_api_client/__about__.py and automatically handled by Hatch build system.
