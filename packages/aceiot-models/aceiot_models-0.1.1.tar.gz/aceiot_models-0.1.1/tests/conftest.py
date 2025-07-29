"""Pytest configuration and fixtures for ACE IoT models tests."""

import json
from datetime import UTC, datetime
from typing import Any

import pytest


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing."""
    return datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)


@pytest.fixture
def sample_client_data() -> dict[str, Any]:
    """Sample client data for testing."""
    return {
        "id": 1,
        "name": "test_client",
        "nice_name": "Test Client",
        "address": "123 Test Street",
        "tech_contact": "tech@testclient.com",
        "bus_contact": "business@testclient.com",
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_site_data() -> dict[str, Any]:
    """Sample site data for testing."""
    return {
        "id": 1,
        "name": "test_site",
        "nice_name": "Test Site",
        "address": "123 Site Street",
        "vtron_ip": "192.168.1.100",
        "vtron_user": "volttron",
        "ansible_user": "deploy",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "geo_location": "New York, NY",
        "mqtt_prefix": "test_site",
        "client_id": 1,
        "client": "Test Client",
        "archived": False,
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_gateway_data() -> dict[str, Any]:
    """Sample gateway data for testing."""
    return {
        "id": 1,
        "name": "test_gateway",
        "site_id": 1,
        "client_id": 1,
        "site": "test_site",
        "client": "Test Client",
        "hw_type": "Raspberry Pi 4",
        "software_type": "VOLTTRON",
        "primary_mac": "b8:27:eb:12:34:56",
        "vpn_ip": "10.0.1.100",
        "device_token": "test_token_12345",
        "device_token_expires": "2024-12-31T23:59:59Z",
        "interfaces": {
            "eth0": {"ip": "192.168.1.100", "netmask": "255.255.255.0", "gateway": "192.168.1.1"}
        },
        "deploy_config": {"ssh_port": 22, "install_path": "/opt/volttron"},
        "archived": False,
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_bacnet_data() -> dict[str, Any]:
    """Sample BACnet data for testing."""
    return {
        "device_address": "192.168.1.10",
        "device_id": 1001,
        "object_type": "analogInput",
        "object_index": 1,
        "object_name": "Temperature_Sensor_1",
        "device_name": "HVAC_Controller_1",
        "object_description": "Temperature sensor in zone 1",
        "device_description": "Main HVAC controller",
        "scrape_interval": 300,
        "scrape_enabled": True,
        "present_value": "72.5",
    }


@pytest.fixture
def sample_point_data(sample_bacnet_data) -> dict[str, Any]:
    """Sample point data for testing."""
    return {
        "id": 1,
        "name": "temperature_zone_1",
        "site_id": 1,
        "client_id": 1,
        "site": "test_site",
        "client": "Test Client",
        "marker_tags": ["temp", "zone1", "sensor"],
        "kv_tags": {"unit": "fahrenheit", "zone": "1", "type": "temperature"},
        "bacnet_data": sample_bacnet_data,
        "collect_config": {"interval": 300, "deadband": 0.5},
        "point_type": "bacnet_analog",
        "collect_enabled": True,
        "collect_interval": 300,
        "topic_id": 12345,
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_der_event_data() -> dict[str, Any]:
    """Sample DER event data for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "timezone": "America/New_York",
        "event_start": "2024-06-15T14:00:00Z",
        "event_end": "2024-06-15T16:00:00Z",
        "event_type": "demand_response",
        "group_name": "commercial_customers",
        "client": "Test Client",
        "created_by_user": "user@testclient.com",
        "cancelled": False,
        "title": "Summer Peak Demand Response",
        "description": "Reduce load during peak summer hours",
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_volttron_agent_data() -> dict[str, Any]:
    """Sample Volttron agent data for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "identity": "weather_agent",
        "package_name": "weather_collector",
        "revision": "1.0.0",
        "tag": "production",
        "active": True,
        "package_id": "550e8400-e29b-41d4-a716-446655440003",
        "volttron_agent_package_id": "550e8400-e29b-41d4-a716-446655440003",
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_agent_config_data() -> dict[str, Any]:
    """Sample agent configuration data for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "agent_identity": "weather_agent",
        "config_name": "config",
        "config_hash": "abc123def456",
        "blob": json.dumps(
            {"api_key": "test_key", "update_interval": 3600, "weather_source": "openweathermap"}
        ),
        "active": True,
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_hawke_config_data() -> dict[str, Any]:
    """Sample Hawke configuration data for testing."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440005",
        "hawke_identity": "hawke.monitoring.agent",
        "content_hash": "def789ghi012",
        "content_blob": json.dumps(
            {
                "monitoring": {"enabled": True, "interval": 60},
                "thresholds": {"cpu": 80, "memory": 85, "disk": 90},
            }
        ),
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "contact": "+1-555-123-4567",
        "email": "testuser@example.com",
        "active": True,
        "confirmed_at": "2024-01-15T10:30:45Z",
        "fs_uniquifier": "unique_string_12345",
        "client_ids": [1, 2],
        "role_id": 2,
        "created": "2024-01-15T10:30:45Z",
        "updated": "2024-01-15T10:30:45Z",
    }


@pytest.fixture
def sample_point_sample_data() -> dict[str, Any]:
    """Sample point sample data for testing."""
    return {"name": "temperature_zone_1", "value": "72.5", "time": "2024-01-15T10:30:45Z"}


@pytest.fixture
def sample_timeseries_data(sample_point_sample_data) -> dict[str, Any]:
    """Sample timeseries data for testing."""
    return {
        "point_samples": [
            sample_point_sample_data,
            {"name": "humidity_zone_1", "value": "45.2", "time": "2024-01-15T10:30:45Z"},
        ]
    }


@pytest.fixture
def sample_paginated_response() -> dict[str, Any]:
    """Sample paginated response data for testing."""
    return {"page": 1, "pages": 5, "per_page": 10, "total": 47, "items": []}


# Utility functions for tests
def assert_model_fields(model, expected_data, exclude_fields=None):
    """Assert that model fields match expected data."""
    if exclude_fields is None:
        exclude_fields = set()

    model_data = model.model_dump()
    for key, expected_value in expected_data.items():
        if key in exclude_fields:
            continue

        assert key in model_data, f"Field {key} missing from model"

        # Handle datetime comparison
        if isinstance(expected_value, str) and key in [
            "created",
            "updated",
            "time",
            "event_start",
            "event_end",
        ]:
            if isinstance(model_data[key], datetime):
                # Convert both to ISO format for comparison
                expected_iso = (
                    expected_value.replace("Z", "+00:00")
                    if expected_value.endswith("Z")
                    else expected_value
                )
                model_iso = model_data[key].isoformat()
                assert model_iso == expected_iso, (
                    f"Datetime field {key}: expected {expected_iso}, got {model_iso}"
                )
            else:
                # Both are strings, normalize them
                expected_iso = (
                    expected_value.replace("Z", "+00:00")
                    if expected_value.endswith("Z")
                    else expected_value
                )
                model_iso = (
                    model_data[key].replace("Z", "+00:00")
                    if model_data[key].endswith("Z")
                    else model_data[key]
                )
                assert model_iso == expected_iso, (
                    f"Datetime field {key}: expected {expected_iso}, got {model_iso}"
                )
        else:
            assert model_data[key] == expected_value, (
                f"Field {key}: expected {expected_value}, got {model_data[key]}"
            )


def create_invalid_data_cases():
    """Create test cases with invalid data."""
    return [
        # Empty string cases
        {"name": ""},
        {"name": "   "},
        # None cases where required
        {"name": None},
        # Wrong type cases
        {"id": "not_an_integer"},
        {"active": "not_a_boolean"},
        # Out of range cases
        {"latitude": 91.0},
        {"longitude": -181.0},
    ]


@pytest.fixture
def invalid_data_cases():
    """Fixture providing invalid data test cases."""
    return create_invalid_data_cases()


# Mock data generators
class MockDataGenerator:
    """Generate mock data for testing."""

    @staticmethod
    def client(id=1, **overrides):
        """Generate mock client data."""
        data = {
            "id": id,
            "name": f"client_{id}",
            "nice_name": f"Client {id}",
            "address": f"{id} Test Street",
            "tech_contact": f"tech{id}@test.com",
            "bus_contact": f"bus{id}@test.com",
        }
        data.update(overrides)
        return data

    @staticmethod
    def site(id=1, client_id=1, **overrides):
        """Generate mock site data."""
        data = {
            "id": id,
            "name": f"site_{id}",
            "nice_name": f"Site {id}",
            "client_id": client_id,
            "latitude": 40.0 + id,
            "longitude": -74.0 - id,
        }
        data.update(overrides)
        return data

    @staticmethod
    def point(id=1, site_id=1, client_id=1, **overrides):
        """Generate mock point data."""
        data = {
            "id": id,
            "name": f"point_{id}",
            "site_id": site_id,
            "client_id": client_id,
            "collect_enabled": True,
            "collect_interval": 300,
        }
        data.update(overrides)
        return data


@pytest.fixture
def mock_data():
    """Fixture providing mock data generator."""
    return MockDataGenerator()
