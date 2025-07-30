# Python Version Compatibility

## Supported Versions

aceiot-models now supports Python 3.10, 3.11, 3.12, and 3.13.

## Key Changes for Compatibility

### 1. Replaced `datetime.UTC` with `timezone.utc`
- `datetime.UTC` was introduced in Python 3.11
- Replaced all occurrences with `timezone.utc` for Python 3.10 compatibility
- Files updated:
  - All model files using datetime
  - All test files
  - Total: 12 files modified

### 2. Union Type Syntax (`|`)
- The pipe operator for type unions requires Python 3.10+
- This is used extensively throughout the codebase
- No changes needed as our minimum version is 3.10

### 3. Testing Infrastructure

#### GitHub Actions Workflow
- Created `.github/workflows/test-multi-python.yml`
- Tests run on Python 3.10, 3.11, 3.12, and 3.13
- Matrix testing across Ubuntu, macOS, and Windows
- Automatic testing on push and pull requests

#### Release Workflow
- Created `.github/workflows/release.yml`
- Runs full test suite on all Python versions before release
- Ensures compatibility before publishing to PyPI

#### Local Testing Options

1. **Shell Script**: `test_python_versions.sh`
   ```bash
   ./test_python_versions.sh
   ```

2. **Tox**: `tox.ini` configuration
   ```bash
   tox  # Run all environments
   tox -e py310  # Test specific version
   ```

3. **Manual Testing**
   ```bash
   uv venv --python python3.10
   source .venv/bin/activate
   uv pip install -e .
   uv pip install --group dev
   pytest
   ```

## Version-Specific Features to Avoid

To maintain Python 3.10 compatibility, avoid:
- `datetime.UTC` (use `timezone.utc`)
- `match`/`case` statements (structural pattern matching)
- `ExceptionGroup` and `except*`
- `Self` type from typing (use string literals)
- Any Python 3.11+ standard library features

## Version Update

This compatibility work is released as version 0.3.0, marking a significant improvement in Python version support.