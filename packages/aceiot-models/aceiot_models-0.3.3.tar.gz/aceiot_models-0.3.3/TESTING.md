# Testing aceiot-models

This project uses `tox` with `uv` backend for testing across multiple Python versions.

## Prerequisites

- Python 3.10, 3.11, 3.12, or 3.13
- uv (installed automatically with the project)

## Installation

```bash
# Install the project with dev dependencies
uv pip install -e . --group dev
```

## Running Tests

### Test all Python versions
```bash
# Test all available Python versions in parallel
tox -p auto

# Or test specific versions
tox -e py310,py311,py312,py313
```

### Test current Python version only
```bash
# Quick test
tox -e quick

# With coverage
tox -e coverage
```

### Run specific test environments
```bash
# Linting
tox -e lint

# Auto-format code
tox -e format

# Type checking
tox -e type

# Pre-commit hooks
tox -e pre-commit
```

### Advanced usage
```bash
# Run specific test file
tox -e py313 -- tests/test_common.py

# Run with verbose output
tox -e py313 -- -v

# Run until first failure
tox -e quick -- -x

# Run specific test
tox -e py313 -- tests/test_common.py::TestPaginatedResponse::test_paginated_response_creation
```

## Continuous Integration

The project uses GitHub Actions to automatically test on all supported Python versions for every pull request and release.

## Benefits of using tox with uv

1. **Fast**: uv is much faster than pip for package installation
2. **Consistent**: Same test environment locally and in CI
3. **Isolated**: Each Python version gets its own isolated environment
4. **Parallel**: Tests can run in parallel with `-p auto`
5. **Simple**: One command tests everything