# API Client Changes Summary

## Overview
The API client has been updated to fully conform to the OpenAPI specification (swagger.json). All endpoints now match the documented API paths and parameters.

## Major Changes

### 1. Path Parameters - ID to Name Conversion
All numeric IDs have been replaced with string names to match swagger:
- `client_id` → `client_name`
- `site_id` → `site_name`
- `gateway_id` → `gateway_name`
- `point_id` → `point_name`

### 2. Removed Non-Existent Endpoints
The following methods that called non-existent endpoints have been removed:
- `update_client()` - PUT /clients/{id}
- `delete_client()` - DELETE /clients/{id}
- `update_site()` - PUT /sites/{id}
- `delete_site()` - DELETE /sites/{id}
- `update_gateway()` - PUT /gateways/{id} (replaced with `patch_gateway()`)
- `delete_gateway()` - DELETE /gateways/{id}
- `get_gateway_by_name()` - GET /gateways/by-name/{name}
- `delete_point()` - DELETE /points/{id}
- `get_discovered_points()` - GET /gateways/{id}/discovered-points
- Generic DER event methods (`get_der_events`, `create_der_event`, etc.)
- `get_samples()` - GET /samples

### 3. Added Missing Endpoints
New methods have been added for all endpoints defined in swagger:

#### Client Endpoints:
- `get_client_sites()` - GET /clients/{client_name}/sites
- `get_client_der_events()` - GET /clients/{client_name}/der_events
- `create_client_der_events()` - POST /clients/{client_name}/der_events
- `update_client_der_events()` - PUT /clients/{client_name}/der_events
- `get_client_volttron_agent_package_list()` - GET /clients/{client_name}/volttron_agent_package/list
- `download_client_volttron_agent_package()` - GET /clients/{client_name}/volttron_agent_package
- `upload_client_volttron_agent_package()` - POST /clients/{client_name}/volttron_agent_package

#### Site Endpoints:
- `get_site_points()` - GET /sites/{site_name}/points
- `get_site_configured_points()` - GET /sites/{site_name}/configured_points
- `get_site_timeseries()` - GET /sites/{site_name}/timeseries
- `post_site_timeseries()` - POST /sites/{site_name}/timeseries
- `get_site_weather()` - GET /sites/{site_name}/weather

#### Gateway Endpoints:
- `patch_gateway()` - PATCH /gateways/{gateway_name}
- `get_gateway_der_events()` - GET /gateways/{gateway_name}/der_events
- `create_gateway_token()` - POST /gateways/{gateway_name}/token
- `get_gateway_agent_configs()` - GET /gateways/{gateway_name}/agent_configs
- `create_gateway_agent_configs()` - POST /gateways/{gateway_name}/agent_configs
- `get_gateway_volttron_agents()` - GET /gateways/{gateway_name}/volttron_agents
- `create_gateway_volttron_agents()` - POST /gateways/{gateway_name}/volttron_agents
- `get_gateway_hawke_configuration()` - GET /gateways/{gateway_name}/hawke_configuration
- `create_gateway_hawke_configuration()` - POST /gateways/{gateway_name}/hawke_configuration
- `get_gateway_hawke_agent_configuration()` - GET /gateways/{gateway_name}/hawke_configuration/{hawke_agent_id}
- `create_gateway_hawke_agent_configuration()` - POST /gateways/{gateway_name}/hawke_configuration/{hawke_agent_id}
- `get_gateway_pcap_list()` - GET /gateways/{gateway_name}/pcap/list
- `download_gateway_pcap()` - GET /gateways/{gateway_name}/pcap
- `upload_gateway_pcap()` - POST /gateways/{gateway_name}/pcap
- `get_gateway_volttron_agent_config_package()` - GET /gateways/{gateway_name}/volttron_agent_config_package
- `create_gateway_volttron_agent_config_package()` - POST /gateways/{gateway_name}/volttron_agent_config_package

#### Point Endpoints:
- `get_point_timeseries()` - GET /points/{point_name}/timeseries
- `get_points_timeseries()` - POST /points/get_timeseries

### 4. Fixed Data Structures
- `create_points()` now wraps data in `{"points": [...]}` instead of `{"items": [...]}`
- Added support for `overwrite_m_tags` and `overwrite_kv_tags` parameters

### 5. Fixed Query Parameters
- Removed undocumented parameters:
  - `client_id` from `get_sites()`
  - `site_id`, `gateway_id`, `client_id` from `get_points()`
  - `site_id` from `get_gateways()`
- Added missing documented parameters:
  - `collect_enabled` and `show_archived` to `get_sites()`
  - `show_archived` to `get_gateways()`
  - Various endpoint-specific parameters

### 6. Endpoint Path Corrections
- Volttron agent packages: `/volttron-agent-packages` → `/volttron_agent_package`
- Hawke configs: `/hawke-configs` → `/hawke_configuration`
- DER events: `/der-events` → `/der_events`

## Breaking Changes

### Method Signature Changes
All methods that previously accepted numeric IDs now require string names:
```python
# Before
client.get_client(123)
client.get_site(456)
client.get_gateway(789)
client.get_point(101112)

# After
client.get_client("client_name")
client.get_site("site_name")
client.get_gateway("gateway_name")
client.get_point("point_name")
```

### Removed Methods
Any code using the removed methods will need to be updated:
- Update operations that don't exist in the API should be handled differently
- Delete operations that don't exist should be removed
- Generic DER event operations should use client or gateway-specific endpoints

### Parameter Changes
- `get_sites()` no longer accepts `client_id` parameter
- `get_points()` no longer accepts filtering parameters
- `get_gateways()` no longer accepts `site_id` parameter

## Migration Guide

1. **Update all ID references to names**: Search for method calls with numeric IDs and replace with string names
2. **Remove calls to deleted methods**: Search for and remove any calls to update/delete methods
3. **Update DER event handling**: Replace generic DER event methods with client/gateway-specific ones
4. **Update filtering logic**: Remove undocumented filter parameters or implement filtering client-side
5. **Test all API interactions**: Ensure all API calls work with the corrected endpoints

## Testing Requirements

The test files will need updates to:
1. Use string names instead of numeric IDs
2. Remove tests for non-existent endpoints
3. Add tests for new endpoints
4. Update mock responses to match new data structures
5. Update parameter assertions
