# aceiot-models

Pydantic models for the ACE IoT Aerodrome Platform

## Installation

```bash
pip install aceiot-models
```

## Usage

```python
from aceiot_models import Sample, BACnetModel

# Example usage will be added here
```

## Development

This project uses `uv` for dependency management. To set up a development environment:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/aceiot-models.git
cd aceiot-models

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .
```

## License

MIT License