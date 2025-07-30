# API Integration Tests

This directory contains integration tests for the ACE IoT API client that verify:
- All read operations work correctly
- API responses can be deserialized into Pydantic models
- Pagination works as expected
- Error handling is correct

## Running Integration Tests

Integration tests are **disabled by default** because they require a live API endpoint and valid credentials.

### Prerequisites

1. Access to a live ACE IoT API instance
2. A valid API key with read permissions
3. Environment variables configured (see below)

### Environment Variables

Set the following environment variables before running integration tests:

```bash
# Required: API endpoint and authentication
export ACEIOT_API_URL="https://flightdeck.aceiot.cloud/api"
export ACEIOT_API_KEY="your-api-key-here"

# Required: Enable integration tests
export ACEIOT_INTEGRATION_TESTS="true"

# Optional: Set timeout for API requests (default: 30 seconds)
export ACEIOT_API_TIMEOUT="60"
```

### Running the Tests

```bash
# Run only integration tests
pytest tests/api/test_integration.py -v

# Run with coverage
pytest tests/api/test_integration.py -v --cov=aceiot_models.api

# Run specific test
pytest tests/api/test_integration.py::TestAPIIntegration::test_get_clients_and_deserialize -v
```

### Test Coverage

The integration tests cover:

1. **Client Operations**
   - List clients with pagination
   - Get single client by ID
   - Deserialize to Client model

2. **Site Operations**
   - List sites with pagination
   - Filter sites by client
   - Get single site by ID
   - Deserialize to Site model

3. **Gateway Operations**
   - List gateways with pagination
   - Get single gateway by ID
   - Get gateway by name
   - Deserialize to Gateway model

4. **Point Operations**
   - List points with pagination
   - Filter points by site/gateway/client
   - Get single point by ID
   - Get discovered points
   - Deserialize to Point model using utility functions

5. **DER Event Operations**
   - List DER events
   - Deserialize to DEREvent model

6. **Volttron Operations**
   - List Volttron agent packages
   - Deserialize to VolttronAgentPackage model

7. **Hawke Config Operations**
   - List Hawke configurations
   - Deserialize to HawkeConfig model

8. **Time Series Data**
   - Get sample data for points
   - Deserialize to Sample model

9. **Pagination**
   - Iterator pattern with PaginatedResults
   - Helper function with max_items limit

10. **Error Handling**
    - 404 errors for non-existent resources
    - Invalid filter parameters

### Skipped Tests

Some tests may be skipped if:
- The API endpoint doesn't support certain features (e.g., DER events)
- No test data is available (e.g., no gateways configured)
- Specific endpoints return 404 (feature not enabled)

### Adding New Tests

When adding new integration tests:
1. Use the `api_client` fixture to get a configured client
2. Check for test data availability and skip if needed
3. Verify both API response structure and model deserialization
4. Handle expected errors gracefully
5. Limit the amount of data fetched to keep tests fast

### Security Notes

- Never commit API keys or credentials
- Use environment variables for all sensitive configuration
- Consider using a dedicated test account with limited permissions
- Be mindful of rate limits on production APIs
