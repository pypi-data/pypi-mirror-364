"""Tests for ACE IoT API Client."""

import os
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import HTTPError, RequestException

from aceiot_models.api import APIClient, APIError


class TestAPIClient:
    """Test cases for APIClient."""

    @pytest.fixture
    def api_client(self):
        """Create API client instance for testing."""
        return APIClient(base_url="https://test.api.com", api_key="test-key", timeout=30)

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock()
        response.status_code = 200
        response.text = '{"test": "data"}'
        response.json.return_value = {"test": "data"}
        return response

    def test_init_with_params(self):
        """Test initialization with parameters."""
        client = APIClient(base_url="https://example.com", api_key="key123", timeout=60)
        assert client.base_url == "https://example.com"
        assert client.api_key == "key123"
        assert client.timeout == 60

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "ACEIOT_API_URL": "https://env.api.com",
                "ACEIOT_API_KEY": "env-key",
                "ACEIOT_API_TIMEOUT": "45",
            },
        ):
            client = APIClient(timeout=None)  # Pass None to use env var
            assert client.base_url == "https://env.api.com"
            assert client.api_key == "env-key"
            assert client.timeout == 45

    def test_init_missing_api_key(self):
        """Test initialization fails without API key."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(ValueError, match="API key is required"),
        ):
            APIClient(base_url="https://example.com")

    def test_request_success(self, api_client, mock_response):
        """Test successful request."""
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client._request("GET", "/test")
            assert result == {"test": "data"}

    def test_request_http_error(self, api_client):
        """Test request with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = '{"detail": "Not found"}'
        mock_response.json.return_value = {"detail": "Not found"}

        # Create HTTPError with response
        http_error = HTTPError("404 Not Found")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error

        with patch.object(api_client.session, "request", return_value=mock_response):
            with pytest.raises(APIError) as exc_info:
                api_client._request("GET", "/test")
            assert exc_info.value.status_code == 404
            assert exc_info.value.response_data == {"detail": "Not found"}

    def test_request_connection_error(self, api_client):
        """Test request with connection error."""
        with (
            patch.object(
                api_client.session, "request", side_effect=RequestException("Connection failed")
            ),
            pytest.raises(APIError, match="Request failed"),
        ):
            api_client._request("GET", "/test")

    # Client endpoint tests
    def test_get_clients(self, api_client, mock_response):
        """Test get_clients method."""
        mock_response.json.return_value = {
            "items": [{"id": 1, "name": "Client 1"}],
            "total_pages": 1,
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_clients(page=1, per_page=50)
            assert result["items"][0]["name"] == "Client 1"

    def test_get_client(self, api_client, mock_response):
        """Test get_client method."""
        mock_response.json.return_value = {"id": 1, "name": "Client1"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_client("Client1")
            assert result["name"] == "Client1"

    def test_create_client(self, api_client, mock_response):
        """Test create_client method."""
        client_data = {"name": "New Client"}
        mock_response.json.return_value = {"id": 2, "name": "New Client"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.create_client(client_data)
            assert result["id"] == 2

    def test_get_client_sites(self, api_client, mock_response):
        """Test get_client_sites method."""
        mock_response.json.return_value = {"items": [{"id": 1, "name": "Site1"}], "total_pages": 1}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_client_sites("Client1")
            assert result["items"][0]["name"] == "Site1"

    # Site endpoint tests
    def test_get_sites(self, api_client, mock_response):
        """Test get_sites method."""
        mock_response.json.return_value = {"items": [{"id": 1, "name": "Site1"}], "total_pages": 1}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_sites(show_archived=False)
            assert result["items"][0]["name"] == "Site1"

    def test_get_site(self, api_client, mock_response):
        """Test get_site method."""
        mock_response.json.return_value = {"id": 1, "name": "Site1"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_site("Site1")
            assert result["name"] == "Site1"

    def test_create_site(self, api_client, mock_response):
        """Test create_site method."""
        site_data = {"name": "New Site", "client_id": 1}
        mock_response.json.return_value = {"id": 2, "name": "New Site"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.create_site(site_data)
            assert result["id"] == 2

    # Gateway endpoint tests
    def test_get_gateways(self, api_client, mock_response):
        """Test get_gateways method."""
        mock_response.json.return_value = {
            "items": [{"id": 1, "name": "Gateway1"}],
            "total_pages": 1,
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_gateways(show_archived=False)
            assert result["items"][0]["name"] == "Gateway1"

    def test_get_gateway(self, api_client, mock_response):
        """Test get_gateway method."""
        mock_response.json.return_value = {"id": 1, "name": "gateway-1"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_gateway("gateway-1")
            assert result["name"] == "gateway-1"

    # Point endpoint tests
    def test_get_points(self, api_client, mock_response):
        """Test get_points method."""
        mock_response.json.return_value = {
            "items": [{"id": 1, "name": "sensor/temp"}],
            "total_pages": 1,
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_points()
            assert result["items"][0]["name"] == "sensor/temp"

    def test_create_points(self, api_client, mock_response):
        """Test create_points method."""
        points_data = [{"name": "sensor/1", "site_id": 1}]
        mock_response.json.return_value = {"items": [{"id": 1, "name": "sensor/1"}]}
        with patch.object(
            api_client.session, "request", return_value=mock_response
        ) as mock_request:
            result = api_client.create_points(points_data)
            assert result["items"][0]["id"] == 1
            # Verify the request was made with wrapped data
            args, kwargs = mock_request.call_args
            assert kwargs["json"] == {"points": points_data}

    def test_get_point(self, api_client, mock_response):
        """Test get_point method."""
        mock_response.json.return_value = {"id": 1, "name": "sensor/temp"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_point("sensor/temp")
            assert result["name"] == "sensor/temp"

    # DER Event endpoint tests
    def test_get_gateway_der_events(self, api_client, mock_response):
        """Test get_gateway_der_events method."""
        mock_response.json.return_value = {
            "items": [{"id": 1, "event_type": "dispatch"}],
            "total_pages": 1,
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_gateway_der_events("gateway-1")
            assert result["items"][0]["event_type"] == "dispatch"

    def test_get_client_der_events(self, api_client, mock_response):
        """Test get_client_der_events method."""
        mock_response.json.return_value = {
            "items": [{"id": 1, "event_type": "dispatch"}],
            "total_pages": 1,
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_client_der_events("client-1")
            assert result["items"][0]["event_type"] == "dispatch"

    # Volttron Agent endpoint tests
    def test_get_client_volttron_agent_package_list(self, api_client, mock_response):
        """Test get_client_volttron_agent_package_list method."""
        mock_response.json.return_value = {"items": [{"package_name": "agent1", "id": "1"}]}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_client_volttron_agent_package_list("client-1")
            assert result["items"][0]["package_name"] == "agent1"

    def test_upload_client_volttron_agent_package(self, api_client, mock_response, tmp_path):
        """Test upload_client_volttron_agent_package method."""
        # Create a temporary file
        test_file = tmp_path / "agent.tar.gz"
        test_file.write_bytes(b"test content")

        mock_response.json.return_value = {"status": "uploaded"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.upload_client_volttron_agent_package(
                "client-1",
                str(test_file),
                "test-agent",
                "Test agent package",
            )
            assert result["status"] == "uploaded"

    # Hawke config endpoint tests
    def test_get_gateway_hawke_configuration(self, api_client, mock_response):
        """Test get_gateway_hawke_configuration method."""
        mock_response.json.return_value = {
            "items": [{"content_hash": "abc123", "hawke_identity": "hawke1"}]
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_gateway_hawke_configuration("gateway-1")
            assert result["items"][0]["content_hash"] == "abc123"

    def test_create_gateway_hawke_configuration(self, api_client, mock_response):
        """Test create_gateway_hawke_configuration method."""
        config_data = [{"hawke_identity": "hawke1", "content_blob": "config data"}]
        mock_response.json.return_value = {"status": "created"}
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.create_gateway_hawke_configuration("gateway-1", config_data)
            assert result["status"] == "created"

    # Timeseries endpoint tests
    def test_get_point_timeseries(self, api_client, mock_response):
        """Test get_point_timeseries method."""
        mock_response.json.return_value = {
            "point_samples": [
                {"name": "sensor/temp", "time": "2024-01-01T00:00:00Z", "value": "23.5"}
            ]
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_point_timeseries(
                "sensor/temp", "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"
            )
            assert result["point_samples"][0]["value"] == "23.5"

    def test_get_site_timeseries(self, api_client, mock_response):
        """Test get_site_timeseries method."""
        mock_response.json.return_value = {
            "point_samples": [
                {"name": "sensor/temp", "time": "2024-01-01T00:00:00Z", "value": "23.5"}
            ]
        }
        with patch.object(api_client.session, "request", return_value=mock_response):
            result = api_client.get_site_timeseries(
                "site-1", "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"
            )
            assert result["point_samples"][0]["value"] == "23.5"

    def test_from_config(self):
        """Test creating client from config object."""
        config = Mock()
        config.base_url = "https://config.api.com"
        config.api_key = "config-key"
        config.timeout = 45

        client = APIClient.from_config(config)
        assert client.base_url == "https://config.api.com"
        assert client.api_key == "config-key"
        assert client.timeout == 45
