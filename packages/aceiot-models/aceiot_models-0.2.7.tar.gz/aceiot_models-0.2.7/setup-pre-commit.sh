#!/bin/bash
# Script to set up pre-commit hooks

echo "Setting up pre-commit hooks..."

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    uv pip install pre-commit
fi

# Install the pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to check current state
echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "Pre-commit setup complete!"
echo "Hooks will now run automatically on git commit."
