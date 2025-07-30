# ACE IoT Models API Client Extraction Requirements

## Executive Summary

This document outlines the requirements for extracting generic API client functionality from the `aceiot-models-cli` package into the upstream `aceiot-models` package. The analysis identified substantial API client code that is not CLI-specific and would benefit other Python applications needing programmatic access to the ACE IoT API.

## Components for Extraction

### 1. Core API Client (`aceiot_models.api_client`)

**Current Location**: `src/aceiot_models_cli/api_client.py`

**Components to Extract**:
- `APIError` exception class
- `APIClient` class with all methods
- HTTP retry logic and session management
- Bearer token authentication
- All API endpoint methods (clients, sites, gateways, points, DER events, Volttron agents)
- File upload functionality with progress callbacks

**Dependencies**:
- `requests` library
- `urllib3` for retry strategy
- `requests-toolbelt` for multipart uploads (optional, for progress tracking)
- Existing `aceiot_models` serializers

### 2. API Utilities (`aceiot_models.api_utils`)

**Current Location**: `src/aceiot_models_cli/utils/api_helpers.py`

**Components to Extract**:
- `get_api_results_paginated()` - Generic pagination handler
- `batch_process()` - Generic batch processing for API limits
- `process_points_from_api()` - Model conversion utilities
- `convert_api_response_to_points()` - Response transformation
- `convert_samples_to_models()` - Sample data conversion

### 3. Pagination Iterator (`aceiot_models.pagination`)

**Current Location**: `src/aceiot_models_cli/utils/pagination.py`

**Components to Extract**:
- `PaginatedResults` class - Generic pagination iterator

## Proposed Package Structure

```
aceiot_models/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── client.py          # APIClient and APIError
│   ├── utils.py           # Helper functions
│   └── pagination.py      # PaginatedResults
├── models/                # Existing models
├── serializers/           # Existing serializers
└── ...
```

## API Design Requirements

### 1. Client Initialization

```python
from aceiot_models.api import APIClient

# Basic initialization
client = APIClient(
    base_url="https://flightdeck.aceiot.cloud/api",
    api_key="your-api-key",
    timeout=30  # optional, defaults to 30
)
```

### 2. Error Handling

```python
from aceiot_models.api import APIError

try:
    result = client.get_sites()
except APIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response Data: {e.response_data}")
```

### 3. Pagination Support

```python
# Manual pagination
page1 = client.get_sites(page=1, per_page=100)
page2 = client.get_sites(page=2, per_page=100)

# Automatic pagination iterator
from aceiot_models.api import PaginatedResults

paginator = PaginatedResults(
    api_func=client.get_sites,
    per_page=500
)

for page_items in paginator:
    process_items(page_items)

# Or get all items at once
all_items = paginator.all_items()
```

### 4. Batch Processing

```python
from aceiot_models.api.utils import batch_process

# Process 1000 points in batches of 100
def create_batch(points):
    return client.create_points(points)

results = batch_process(
    items=large_point_list,
    process_func=create_batch,
    batch_size=100,
    progress_callback=lambda current, total: print(f"{current}/{total}")
)
```

### 5. File Uploads with Progress

```python
# Upload with progress tracking
def progress_handler(bytes_read, total_bytes):
    percent = (bytes_read / total_bytes) * 100
    print(f"Upload progress: {percent:.1f}%")

result = client.upload_volttron_agent_package(
    gateway_name="gateway-1",
    file_path="/path/to/agent.tar.gz",
    package_name="my-agent",
    description="My custom agent",
    progress_callback=progress_handler
)
```

## Configuration Support

The API client should support configuration through:

1. **Direct initialization** (as shown above)
2. **Environment variables**:
   - `ACEIOT_API_URL`
   - `ACEIOT_API_KEY`
   - `ACEIOT_API_TIMEOUT`
3. **Configuration object** (optional):

```python
from aceiot_models.api import APIConfig, APIClient

config = APIConfig(
    base_url="https://flightdeck.aceiot.cloud/api",
    api_key="your-api-key",
    timeout=60
)

client = APIClient.from_config(config)
```

## Testing Requirements

1. **Unit Tests**: Mock HTTP responses for all API methods
2. **Integration Tests**: Optional tests against a test API instance
3. **Type Hints**: Full type annotations for all public methods
4. **Documentation**: Docstrings for all classes and methods

## Migration Strategy

### Phase 1: Add to aceiot_models (Non-breaking)
1. Create new `api` subpackage in aceiot_models
2. Copy and adapt code from aceiot-models-cli
3. Add tests and documentation
4. Release new version of aceiot_models

### Phase 2: Update aceiot-models-cli (Non-breaking)
1. Add dependency on new aceiot_models version
2. Import API client from aceiot_models.api
3. Deprecate local copies with warnings
4. Maintain backward compatibility

### Phase 3: Remove Duplicates (Breaking)
1. Remove deprecated code from aceiot-models-cli
2. Update imports throughout
3. Release major version bump

## Benefits

1. **Code Reuse**: Other Python applications can use the API client
2. **Maintenance**: Single source of truth for API interactions
3. **Testing**: Centralized testing of API functionality
4. **Documentation**: Unified API documentation
5. **Type Safety**: Consistent type hints across projects

## Example Use Cases

### Web Application
```python
from aceiot_models.api import APIClient
from flask import Flask, jsonify

app = Flask(__name__)
client = APIClient(base_url=API_URL, api_key=API_KEY)

@app.route('/api/sites')
def get_sites():
    sites = client.get_sites(per_page=100)
    return jsonify(sites)
```

### Data Pipeline
```python
from aceiot_models.api import APIClient, PaginatedResults
import pandas as pd

client = APIClient(base_url=API_URL, api_key=API_KEY)

# Fetch all points
paginator = PaginatedResults(client.get_points, per_page=1000)
all_points = paginator.all_items()

# Convert to DataFrame
df = pd.DataFrame(all_points)
df.to_parquet('points_export.parquet')
```

### Automated Script
```python
from aceiot_models.api import APIClient
from aceiot_models import PointCreate

client = APIClient(base_url=API_URL, api_key=API_KEY)

# Bulk create points
new_points = [
    PointCreate(name=f"sensor/{i}", client_id=1, site_id=1)
    for i in range(100)
]

result = client.create_points(new_points)
print(f"Created {len(result['items'])} points")
```

## Conclusion

Extracting the API client functionality from aceiot-models-cli into aceiot_models will provide a robust, reusable Python SDK for the ACE IoT API. The proposed architecture maintains clean separation of concerns while enabling broader ecosystem adoption.
