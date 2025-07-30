# API Compliance Report: swagger.json vs api_client.py

## Executive Summary

This report analyzes the conformance between the OpenAPI specification (swagger.json) and the implemented API client (aceiot_models/api/client.py).

### Key Findings:
1. **Critical Path Parameter Mismatch**: The API client uses numeric IDs (e.g., `client_id`, `site_id`) while swagger.json uses string names (e.g., `client_name`, `site_name`)
2. **Non-existent Endpoints**: Multiple methods in the API client call endpoints that don't exist in the swagger specification
3. **Undocumented Parameters**: The API client passes several filter parameters (`client_id`, `site_id`, `gateway_id`) that are not documented in swagger.json
4. **Missing Implementations**: Many endpoints defined in swagger.json are not implemented in the API client
5. **Incorrect Endpoint Paths**: Several endpoints use different paths than specified (e.g., `/hawke-configs` vs `/hawke_configuration`)

## Major Discrepancies Found

### 1. Client Endpoints

#### Path Parameter Mismatch
- **Issue**: Swagger uses `{client_name}` (string) but client.py uses numeric IDs
- **Swagger**: `/clients/{client_name}`
- **Implementation**: `/clients/{client_id}` (using integers)

#### Non-existent Endpoints
The following methods exist in client.py but have NO corresponding endpoints in swagger.json:
- `update_client()` - PUT /clients/{client_id}
- `delete_client()` - DELETE /clients/{client_id}

#### Missing Implementations
The following endpoints exist in swagger.json but are NOT implemented:
- GET /clients/{client_name}/der_events
- PUT /clients/{client_name}/der_events
- POST /clients/{client_name}/der_events
- GET /clients/{client_name}/sites
- GET /clients/{client_name}/volttron_agent_package
- POST /clients/{client_name}/volttron_agent_package
- GET /clients/{client_name}/volttron_agent_package/list

### 2. Gateway Endpoints

#### Path Parameter Issues
- **Issue**: Most swagger endpoints use `{gateway_name}` but some client methods use numeric IDs
- **Examples**:
  - `get_gateway(gateway_id)` uses `/gateways/{gateway_id}` but swagger expects name
  - `create_gateway()`, `update_gateway()`, `delete_gateway()` use IDs not present in swagger

#### Non-existent Endpoints
- `update_gateway()` - PUT endpoint doesn't exist
- `delete_gateway()` - DELETE endpoint doesn't exist
- `get_gateway_by_name()` - GET /gateways/by-name/{gateway_name} doesn't exist

#### Missing Implementations
- GET /gateways/{gateway_name}/agent_configs
- POST /gateways/{gateway_name}/agent_configs
- GET /gateways/{gateway_name}/der_events
- GET /gateways/{gateway_name}/hawke_configuration
- POST /gateways/{gateway_name}/hawke_configuration
- GET /gateways/{gateway_name}/hawke_configuration/{hawke_agent_id}
- POST /gateways/{gateway_name}/hawke_configuration/{hawke_agent_id}
- GET /gateways/{gateway_name}/hawke_configuration/{hawke_agent_id}/list
- GET /gateways/{gateway_name}/pcap
- POST /gateways/{gateway_name}/pcap
- GET /gateways/{gateway_name}/pcap/list
- POST /gateways/{gateway_name}/token
- GET /gateways/{gateway_name}/volttron_agent_config_package
- POST /gateways/{gateway_name}/volttron_agent_config_package
- GET /gateways/{gateway_name}/volttron_agents
- POST /gateways/{gateway_name}/volttron_agents

### 3. Site Endpoints

#### Non-existent Endpoints
- `update_site()` - PUT endpoint doesn't exist
- `delete_site()` - DELETE endpoint doesn't exist

#### Missing Implementations
- GET /sites/{site_name}/configured_points
- GET /sites/{site_name}/points
- GET /sites/{site_name}/timeseries
- POST /sites/{site_name}/timeseries
- GET /sites/{site_name}/weather

#### Parameter Issues
- `get_sites()` includes undocumented `client_id` parameter
- Missing `collect_enabled` and `show_archived` parameters from swagger

### 4. Point Endpoints

#### Path Parameter Issues
- Uses numeric IDs instead of point names
- Swagger uses `/points/{point_name}` but implementation uses `/points/{point_id}`

#### Non-existent Endpoints
- `delete_point()` - DELETE endpoint doesn't exist
- `get_discovered_points()` - No such endpoint in swagger

#### Missing Implementations
- POST /points/get_timeseries
- GET /points/{point_name}/timeseries

#### Parameter Issues
- `get_points()` includes undocumented parameters: `site_id`, `gateway_id`, `client_id`
- `create_points()` wraps data in {"items": ...} but swagger expects {"points": ...}
- Missing `overwrite_m_tags` and `overwrite_kv_tags` parameters for POST/PUT

### 5. Completely Missing Endpoint Categories

#### DER Events
- Client implementation uses `/der-events` but swagger has these under `/clients/{client_name}/der_events` and `/gateways/{gateway_name}/der_events`
- The generic `/der-events` endpoints don't exist in swagger

#### Samples
- `get_samples()` uses `/samples` endpoint which doesn't exist in swagger
- Timeseries data should use the point-specific endpoints

#### Volttron Agent Packages
- Implementation uses non-existent paths like `/gateways/{gateway_name}/volttron-agent-packages`
- Swagger uses `/clients/{client_name}/volttron_agent_package`

#### Hawke Configs
- Implementation uses `/gateways/{gateway_name}/hawke-configs`
- Swagger uses `/gateways/{gateway_name}/hawke_configuration`

### 6. Undocumented Parameters Being Passed

The following parameters are being passed by the API client but are NOT documented in swagger.json:

#### Sites Endpoint (GET /sites/)
- `client_id` - Being passed as a filter parameter (line 222 in client.py)
- Swagger only documents: `page`, `per_page`, `collect_enabled`, `show_archived`, `X-Fields`

#### Points Endpoint (GET /points/)
- `site_id` - Being passed as a filter parameter (line 360 in client.py)
- `gateway_id` - Being passed as a filter parameter (line 362 in client.py)
- `client_id` - Being passed as a filter parameter (line 364 in client.py)
- Swagger only documents: `page`, `per_page`, `X-Fields`

#### Gateways Endpoint (GET /gateways/)
- `site_id` - Being passed as a filter parameter (line 281 in client.py)
- Swagger only documents: `page`, `per_page`, `show_archived`, `X-Fields`

### 7. Missing Common Parameters

The following parameters are defined in swagger but not supported:
- `X-Fields` header (for field masking) - available on most GET endpoints
- `collect_enabled` parameter for GET /sites/
- `show_archived` parameter for GET /sites/ and GET /gateways/

### 8. Authentication

- Swagger specifies `authorization` header with apiKey type
- Implementation uses `Bearer {api_key}` format which may be correct but isn't clearly specified

## Recommendations

1. **Critical**: Fix all path parameter mismatches (ID vs name)
2. **Critical**: Remove methods that call non-existent endpoints
3. **High**: Implement missing endpoints from swagger
4. **High**: Fix parameter naming and structure to match swagger exactly
5. **Medium**: Add support for X-Fields header parameter
6. **Medium**: Add missing query parameters for filtering and options
7. **Low**: Add proper response model validation

## Code Changes Needed

1. Refactor client methods to use names instead of IDs where required
2. Remove or fix non-existent endpoint methods
3. Update endpoint paths to match swagger exactly
4. Fix parameter structures (e.g., points wrapping)
5. Add missing query parameters to method signatures
6. Implement missing endpoint methods
