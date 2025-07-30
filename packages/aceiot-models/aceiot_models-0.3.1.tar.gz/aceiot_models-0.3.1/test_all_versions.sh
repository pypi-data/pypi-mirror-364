#!/bin/bash
# Simple multi-version test script

set -e

echo "Testing aceiot-models with multiple Python versions"
echo "=================================================="

# Test with each Python version
for version in 3.10 3.11 3.12 3.13; do
    if command -v python$version &> /dev/null; then
        echo -e "\n### Testing with Python $version ###"
        
        # Create a temp directory for this version
        TEMP_DIR=$(mktemp -d)
        
        # Create venv and install
        python$version -m venv "$TEMP_DIR/venv"
        source "$TEMP_DIR/venv/bin/activate"
        
        # Install the package in editable mode
        pip install -q --upgrade pip
        pip install -q -e .
        
        # Run the compatibility test
        python test_compatibility.py
        
        # Cleanup
        deactivate
        rm -rf "$TEMP_DIR"
    else
        echo -e "\n### Python $version not found, skipping ###"
    fi
done

echo -e "\n=================================================="
echo "All tests completed!"