# Pre-commit Setup

This project uses pre-commit hooks to ensure code quality and consistency.

## What's Included

The pre-commit configuration includes:

1. **Standard hooks** (from pre-commit-hooks):
   - Remove trailing whitespace
   - Fix end of files
   - Check YAML syntax
   - Check for large files
   - Check for merge conflicts
   - Check TOML syntax
   - Debug statement detection
   - Mixed line ending fixes

2. **Ruff** (Python linting and formatting):
   - `ruff` - Lints Python code and auto-fixes issues
   - `ruff-format` - Formats Python code consistently

3. **Mypy** (Type checking):
   - Type checks Python code
   - Includes types-requests for better type checking

## Installation

### Option 1: Using the setup script
```bash
./setup-pre-commit.sh
```

### Option 2: Manual installation
```bash
# Install pre-commit
uv pip install pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

## Usage

Once installed, pre-commit will run automatically on `git commit`.

To run manually:
```bash
# Run on staged files
pre-commit run

# Run on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files
```

## Updating hooks

To update the hooks to their latest versions:
```bash
pre-commit autoupdate
```

## Skipping hooks

If you need to skip pre-commit for a single commit:
```bash
git commit --no-verify
```

## Configuration

The configuration is stored in `.pre-commit-config.yaml`. Ruff-specific settings are in `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.format]`.
