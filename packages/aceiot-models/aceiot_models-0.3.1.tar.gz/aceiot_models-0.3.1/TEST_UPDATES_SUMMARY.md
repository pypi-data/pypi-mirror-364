# Test Updates Summary

## Overview
All tests have been updated to match the new API client implementation that conforms to the OpenAPI specification (swagger.json).

## Integration Test Changes (test_integration.py)

### 1. Updated Parameter Types
- Changed from numeric IDs to string names in test fixtures:
  - `client_id` → `client_name`
  - `site_id` → `site_name`
  - `gateway_id` → `gateway_name`
  - `point_ids` → `point_names`

### 2. Updated API Calls
- `get_client(client_id)` → `get_client(client_name)`
- `get_site(site_id)` → `get_site(site_name)`
- `get_gateway(gateway_id)` → `get_gateway(gateway_name)`
- `get_point(point_id)` → `get_point(point_name)`

### 3. Removed Tests for Non-Existent Endpoints
- Removed `test_get_gateway_by_name()` - endpoint doesn't exist
- Removed `test_discovered_points()` - endpoint doesn't exist
- Removed `test_get_samples()` - replaced with timeseries tests

### 4. Updated Tests to Use Correct Endpoints
- `test_get_sites_by_client()` now uses `get_client_sites(client_name)`
- `test_get_points_with_filters()` now uses `get_site_points(site_name)`
- DER events tests now use gateway/client specific endpoints
- Volttron package tests now use client-specific endpoints
- Hawke config tests now use the correct `/hawke_configuration` endpoint

### 5. Added New Tests
- `test_get_der_events_for_client()` - tests client DER events endpoint
- `test_get_volttron_agents_for_gateway()` - tests gateway agents endpoint
- `test_get_site_weather()` - tests weather endpoint
- `test_get_configured_points()` - tests configured points endpoint
- `test_gateway_token_creation()` - tests token creation endpoint
- `test_get_site_timeseries()` - tests site timeseries endpoint

### 6. Fixed Data Structures
- Updated timeseries tests to expect `point_samples` instead of `items`
- Removed invalid filter parameters from API calls

## Unit Test Changes (test_client.py)

### 1. Updated Method Signatures
- All test methods updated to use string names instead of numeric IDs
- Removed tests for deleted methods (update_client, delete_client, etc.)

### 2. Updated Mock Data
- Changed mock responses to match new API structure
- Fixed wrapped data structures (e.g., `{"points": [...]}` instead of `{"items": [...]}`)

### 3. Added New Test Methods
- `test_get_client_sites()` - replaces removed update_client test
- `test_get_gateway()` - replaces get_gateway_by_name test
- `test_get_point()` - replaces get_discovered_points test
- `test_get_gateway_der_events()` - tests gateway DER events
- `test_get_client_der_events()` - tests client DER events
- `test_get_point_timeseries()` - tests point timeseries
- `test_get_site_timeseries()` - tests site timeseries

### 4. Updated Existing Tests
- `test_get_sites()` now uses `show_archived` parameter
- `test_get_gateways()` now uses `show_archived` parameter
- `test_create_points()` verifies correct data wrapping with `{"points": [...]}`
- Volttron tests updated to use client endpoints
- Hawke tests updated to use correct endpoint paths

## Running the Tests

### Unit Tests
```bash
pytest tests/api/test_client.py -v
```

### Integration Tests (requires live API)
```bash
export ACEIOT_API_URL=https://flightdeck.aceiot.cloud/api
export ACEIOT_API_KEY=your-api-key
export ACEIOT_INTEGRATION_TESTS=true
pytest tests/api/test_integration.py -v
```

## Test Coverage

The updated tests now cover:
- All new endpoints added to the API client
- Correct parameter types (string names vs numeric IDs)
- Proper data structures as defined in swagger.json
- Error handling for 404 responses
- Pagination functionality
- File upload/download endpoints
- Token creation
- Timeseries data retrieval

## Breaking Changes for Test Users

If you have custom tests that use the API client, you'll need to:
1. Update all ID parameters to use names instead
2. Remove tests for deleted endpoints
3. Update filter parameters to match documented API
4. Update expected response structures
5. Use endpoint-specific methods instead of generic ones (e.g., DER events)
