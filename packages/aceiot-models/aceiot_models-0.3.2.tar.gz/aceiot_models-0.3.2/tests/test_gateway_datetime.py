"""Test Gateway model datetime parsing and MAC address validation."""

from datetime import datetime, timezone

import pytest

from aceiot_models.gateways import Gateway


class TestGatewayDatetimeParsing:
    """Test Gateway model's ability to parse various datetime formats."""

    def test_parse_non_iso_datetime_string(self):
        """Test parsing non-ISO datetime string format."""
        gateway_data = {
            "name": "test_gateway",
            "device_token_expires": "2025-11-04 17:02:38.149735",
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)

        # Check that the datetime was parsed correctly
        assert gateway.device_token_expires is not None
        assert isinstance(gateway.device_token_expires, datetime)
        assert gateway.device_token_expires.year == 2025
        assert gateway.device_token_expires.month == 11
        assert gateway.device_token_expires.day == 4
        assert gateway.device_token_expires.hour == 17
        assert gateway.device_token_expires.minute == 2
        assert gateway.device_token_expires.second == 38
        assert gateway.device_token_expires.microsecond == 149735

        # Check that timezone was added (UTC)
        assert gateway.device_token_expires.tzinfo is not None
        assert gateway.device_token_expires.tzinfo == timezone.utc

    def test_parse_iso_datetime_string(self):
        """Test parsing ISO datetime string format."""
        gateway_data = {
            "name": "test_gateway",
            "device_token_expires": "2025-11-04T17:02:38.149735Z",
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)

        assert gateway.device_token_expires is not None
        assert isinstance(gateway.device_token_expires, datetime)
        assert gateway.device_token_expires.year == 2025

    def test_parse_datetime_object(self):
        """Test handling datetime object directly."""
        dt = datetime(2025, 11, 4, 17, 2, 38, 149735)
        gateway_data = {
            "name": "test_gateway",
            "device_token_expires": dt,
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)

        assert gateway.device_token_expires is not None
        assert isinstance(gateway.device_token_expires, datetime)
        # Should have timezone added
        assert gateway.device_token_expires.tzinfo is not None

    def test_parse_none_datetime(self):
        """Test handling None for datetime field."""
        gateway_data = {
            "name": "test_gateway",
            "device_token_expires": None,
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)

        assert gateway.device_token_expires is None

    def test_invalid_datetime_string_raises_error(self):
        """Test that invalid datetime string raises error."""
        gateway_data = {
            "name": "test_gateway",
            "device_token_expires": "not a datetime",
            "site_id": 1,
            "client_id": 1,
        }

        with pytest.raises(ValueError, match="Invalid date format"):
            Gateway(**gateway_data)


class TestGatewayMacAddressValidation:
    """Test Gateway model's MAC address validation."""

    def test_string_none_converted_to_none(self):
        """Test that string 'None' is converted to actual None."""
        gateway_data = {"name": "test_gateway", "primary_mac": "None", "site_id": 1, "client_id": 1}

        gateway = Gateway(**gateway_data)
        assert gateway.primary_mac is None

    def test_mac_with_hyphens(self):
        """Test MAC address with hyphens is accepted."""
        gateway_data = {
            "name": "test_gateway",
            "primary_mac": "18-c0-4d-84-ca-5b",
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)
        assert gateway.primary_mac == "18-c0-4d-84-ca-5b"

    def test_mac_with_colons(self):
        """Test MAC address with colons is accepted."""
        gateway_data = {
            "name": "test_gateway",
            "primary_mac": "18:c0:4d:84:ca:5b",
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)
        assert gateway.primary_mac == "18:c0:4d:84:ca:5b"

    def test_mac_with_dots(self):
        """Test MAC address with dots (Cisco format) is accepted."""
        gateway_data = {
            "name": "test_gateway",
            "primary_mac": "18c0.4d84.ca5b",
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)
        assert gateway.primary_mac == "18c0.4d84.ca5b"

    def test_mac_no_separators(self):
        """Test MAC address without separators is accepted."""
        gateway_data = {
            "name": "test_gateway",
            "primary_mac": "18c04d84ca5b",
            "site_id": 1,
            "client_id": 1,
        }

        gateway = Gateway(**gateway_data)
        assert gateway.primary_mac == "18c04d84ca5b"

    def test_none_mac_address(self):
        """Test actual None for MAC address is accepted."""
        gateway_data = {"name": "test_gateway", "primary_mac": None, "site_id": 1, "client_id": 1}

        gateway = Gateway(**gateway_data)
        assert gateway.primary_mac is None

    def test_invalid_mac_raises_error(self):
        """Test invalid MAC address raises error."""
        gateway_data = {
            "name": "test_gateway",
            "primary_mac": "invalid-mac",
            "site_id": 1,
            "client_id": 1,
        }

        with pytest.raises(ValueError, match="Invalid MAC address format"):
            Gateway(**gateway_data)
