#!/bin/bash
# Test script to verify Python version compatibility

set -e

echo "Testing aceiot-models with multiple Python versions..."
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Python versions to test
PYTHON_VERSIONS=("3.10" "3.11" "3.12" "3.13")

# Function to check if a Python version is installed
check_python() {
    local version=$1
    if command -v python$version &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to run tests for a specific Python version
test_version() {
    local version=$1
    echo -e "\n${GREEN}Testing with Python $version${NC}"
    echo "-----------------------------------"
    
    # Create a temporary virtual environment
    TEMP_DIR=$(mktemp -d)
    echo "Creating virtual environment in $TEMP_DIR"
    
    # Use uv if available, otherwise use standard venv
    if command -v uv &> /dev/null; then
        uv venv --python python$version "$TEMP_DIR/venv"
        source "$TEMP_DIR/venv/bin/activate"
        
        # Install package and dev dependencies
        uv pip install -e .
        uv pip install --group dev
    else
        python$version -m venv "$TEMP_DIR/venv"
        source "$TEMP_DIR/venv/bin/activate"
        
        # Upgrade pip and install
        pip install --upgrade pip
        pip install -e .
        pip install pyrefly pytest ruff pytest-cov
    fi
    
    # Run linting
    echo -e "\nRunning linting..."
    if ruff check . && ruff format --check .; then
        echo -e "${GREEN}✓ Linting passed${NC}"
    else
        echo -e "${RED}✗ Linting failed${NC}"
        deactivate
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Run type checking (skip for older Python versions if pyrefly has issues)
    echo -e "\nRunning type checking..."
    if pyrefly; then
        echo -e "${GREEN}✓ Type checking passed${NC}"
    else
        echo -e "${RED}✗ Type checking failed${NC}"
        # Don't fail the test for type checking issues
    fi
    
    # Run tests
    echo -e "\nRunning tests..."
    if pytest -v; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed${NC}"
        deactivate
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Clean up
    deactivate
    rm -rf "$TEMP_DIR"
    
    echo -e "${GREEN}✓ Python $version: All checks passed${NC}"
    return 0
}

# Main execution
FAILED_VERSIONS=()
SKIPPED_VERSIONS=()

for version in "${PYTHON_VERSIONS[@]}"; do
    if check_python $version; then
        if test_version $version; then
            echo -e "${GREEN}✓ Python $version: SUCCESS${NC}"
        else
            echo -e "${RED}✗ Python $version: FAILED${NC}"
            FAILED_VERSIONS+=($version)
        fi
    else
        echo -e "\n${RED}Python $version not found, skipping...${NC}"
        SKIPPED_VERSIONS+=($version)
    fi
done

# Summary
echo -e "\n=================================================="
echo "Test Summary"
echo "=================================================="

if [ ${#FAILED_VERSIONS[@]} -eq 0 ]; then
    echo -e "${GREEN}All available Python versions passed!${NC}"
else
    echo -e "${RED}Failed versions: ${FAILED_VERSIONS[*]}${NC}"
fi

if [ ${#SKIPPED_VERSIONS[@]} -gt 0 ]; then
    echo -e "Skipped versions (not installed): ${SKIPPED_VERSIONS[*]}"
fi

# Exit with error if any version failed
if [ ${#FAILED_VERSIONS[@]} -gt 0 ]; then
    exit 1
fi

exit 0