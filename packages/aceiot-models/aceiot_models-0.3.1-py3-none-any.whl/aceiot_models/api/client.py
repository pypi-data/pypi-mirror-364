"""ACE IoT API Client.

This module provides the main APIClient class for interacting with the ACE IoT API,
including authentication, error handling, retry logic, and all API endpoints.
"""

import mimetypes
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        """Initialize APIError.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from API
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class APIClient:
    """Client for interacting with the ACE IoT API."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 30,
    ):
        """Initialize API client.

        Args:
            base_url: Base URL for the API. Defaults to ACEIOT_API_URL env var.
            api_key: API key for authentication. Defaults to ACEIOT_API_KEY env var.
            timeout: Request timeout in seconds. Defaults to 30.
        """
        self.base_url = base_url or os.environ.get(
            "ACEIOT_API_URL", "https://flightdeck.aceiot.cloud/api"
        )
        self.api_key = api_key or os.environ.get("ACEIOT_API_KEY")
        # Use provided timeout, or env var, or default
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = int(os.environ.get("ACEIOT_API_TIMEOUT", "30"))

        if not self.api_key:
            raise ValueError(
                "API key is required. Set ACEIOT_API_KEY environment variable or pass api_key parameter."
            )

        # Setup session with retry logic
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: JSON data to send
            params: Query parameters
            files: Files to upload
            headers: Additional headers

        Returns:
            Response data

        Raises:
            APIError: If request fails
        """
        # Ensure base_url ends with / and endpoint doesn't start with /
        # to make urljoin work correctly
        base = self.base_url.rstrip("/") + "/"
        endpoint_path = endpoint.lstrip("/")
        url = urljoin(base, endpoint_path)

        # Prepare request kwargs
        kwargs = {
            "timeout": self.timeout,
            "params": params,
        }

        if files:
            kwargs["files"] = files
            # Don't send JSON data when uploading files
            if data:
                kwargs["data"] = data
        else:
            kwargs["json"] = data

        # Handle headers properly
        if headers:
            kwargs["headers"] = {**self.session.headers, **headers}

        try:
            # For file uploads, temporarily remove Content-Type from session
            if files:
                original_content_type = self.session.headers.pop("Content-Type", None)
                try:
                    response = self.session.request(method, url, **kwargs)
                finally:
                    # Restore Content-Type header
                    if original_content_type:
                        self.session.headers["Content-Type"] = original_content_type
            else:
                response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            error_data = {"detail": "Request failed"}
            status_code = None

            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_data = e.response.json()
                except Exception:
                    error_data = {"detail": e.response.text}

                # Log the error details for debugging
                if status_code == 400:
                    print(f"400 Bad Request for URL: {url}")
                    print(f"Request params: {params}")
                    print(f"Response: {error_data}")

            raise APIError(
                f"API request failed: {e}",
                status_code=status_code,
                response_data=error_data,
            ) from e
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}") from e

    # Client endpoints
    def get_clients(self, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        """Get clients with pagination.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            Paginated response with clients
        """
        return self._request("GET", "/clients", params={"page": page, "per_page": per_page})

    def get_client(self, client_name: str) -> dict[str, Any]:
        """Get a specific client.

        Args:
            client_name: Client name

        Returns:
            Client data
        """
        return self._request("GET", f"/clients/{quote(client_name, safe='')}")

    def create_client(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new client.

        Args:
            client_data: Client data

        Returns:
            Created client
        """
        return self._request("POST", "/clients", data=client_data)

    # Client-specific endpoints from swagger
    def get_client_sites(
        self, client_name: str, page: int = 1, per_page: int = 100
    ) -> dict[str, Any]:
        """Get sites that belong to a client.

        Args:
            client_name: Client name
            page: Page number
            per_page: Items per page

        Returns:
            Paginated response with sites
        """
        return self._request(
            "GET",
            f"/clients/{quote(client_name, safe='')}/sites",
            params={"page": page, "per_page": per_page},
        )

    def get_client_der_events(
        self,
        client_name: str,
        page: int = 1,
        per_page: int = 100,
        get_past_events: bool = False,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Get DER events for a client.

        Args:
            client_name: Client name
            page: Page number
            per_page: Items per page
            get_past_events: Get events from past 24 hours
            group_name: Filter by group name

        Returns:
            Paginated response with DER events
        """
        params = {"page": page, "per_page": per_page, "get_past_events": get_past_events}
        if group_name:
            params["group_name"] = group_name
        return self._request(
            "GET", f"/clients/{quote(client_name, safe='')}/der_events", params=params
        )

    def create_client_der_events(
        self, client_name: str, der_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create DER events for a client.

        Args:
            client_name: Client name
            der_events: List of DER events to create

        Returns:
            Created DER events
        """
        return self._request(
            "POST",
            f"/clients/{quote(client_name, safe='')}/der_events",
            data={"der_events": der_events},
        )

    def update_client_der_events(
        self, client_name: str, der_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update DER events for a client.

        Args:
            client_name: Client name
            der_events: List of DER events to update

        Returns:
            Updated DER events
        """
        return self._request(
            "PUT",
            f"/clients/{quote(client_name, safe='')}/der_events",
            data={"der_events": der_events},
        )

    # Site endpoints
    def get_sites(
        self,
        page: int = 1,
        per_page: int = 100,
        collect_enabled: bool | None = None,
        show_archived: bool = False,
    ) -> dict[str, Any]:
        """Get sites with pagination.

        Args:
            page: Page number
            per_page: Items per page
            collect_enabled: Filter sites with at least one collect enabled point
            show_archived: Whether to collect archived sites

        Returns:
            Paginated response with sites
        """
        params = {"page": page, "per_page": per_page, "show_archived": show_archived}
        if collect_enabled is not None:
            params["collect_enabled"] = collect_enabled
        return self._request("GET", "/sites", params=params)

    def get_site(self, site_name: str) -> dict[str, Any]:
        """Get a specific site.

        Args:
            site_name: Site name

        Returns:
            Site data
        """
        return self._request("GET", f"/sites/{quote(site_name, safe='')}")

    def create_site(self, site_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new site.

        Args:
            site_data: Site data

        Returns:
            Created site
        """
        return self._request("POST", "/sites", data=site_data)

    def get_site_points(self, site_name: str, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        """Get points for a specific site.

        Args:
            site_name: Site name
            page: Page number
            per_page: Items per page

        Returns:
            Paginated response with points
        """
        return self._request(
            "GET",
            f"/sites/{quote(site_name, safe='')}/points",
            params={"page": page, "per_page": per_page},
        )

    def get_site_configured_points(
        self, site_name: str, page: int = 1, per_page: int = 100
    ) -> dict[str, Any]:
        """Get configured points for a specific site.

        Args:
            site_name: Site name
            page: Page number
            per_page: Items per page

        Returns:
            Paginated response with configured points
        """
        return self._request(
            "GET",
            f"/sites/{quote(site_name, safe='')}/configured_points",
            params={"page": page, "per_page": per_page},
        )

    def get_site_timeseries(self, site_name: str, start_time: str, end_time: str) -> dict[str, Any]:
        """Get timeseries data for a site.

        Args:
            site_name: Site name
            start_time: ISO format start time
            end_time: ISO format end time

        Returns:
            Timeseries data
        """
        return self._request(
            "GET",
            f"/sites/{quote(site_name, safe='')}/timeseries",
            params={"start_time": start_time, "end_time": end_time},
        )

    def post_site_timeseries(self, site_name: str, samples: list[dict[str, Any]]) -> dict[str, Any]:
        """Post timeseries data to a site.

        Args:
            site_name: Site name
            samples: List of timeseries samples

        Returns:
            Response data
        """
        return self._request(
            "POST",
            f"/sites/{quote(site_name, safe='')}/timeseries",
            data={"point_samples": samples},
        )

    def get_site_weather(self, site_name: str) -> dict[str, Any]:
        """Get weather data for a site.

        Args:
            site_name: Site name

        Returns:
            Weather data
        """
        return self._request("GET", f"/sites/{quote(site_name, safe='')}/weather")

    # Gateway endpoints
    def get_gateways(
        self, page: int = 1, per_page: int = 100, show_archived: bool = False
    ) -> dict[str, Any]:
        """Get gateways with pagination.

        Args:
            page: Page number
            per_page: Items per page
            show_archived: Whether to collect archived gateways

        Returns:
            Paginated response with gateways
        """
        params = {"page": page, "per_page": per_page, "show_archived": show_archived}
        return self._request("GET", "/gateways", params=params)

    def get_gateway(self, gateway_name: str) -> dict[str, Any]:
        """Get a specific gateway.

        Args:
            gateway_name: Gateway name

        Returns:
            Gateway data
        """
        return self._request("GET", f"/gateways/{quote(gateway_name, safe='')}")

    def create_gateway(self, gateway_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new gateway.

        Args:
            gateway_data: Gateway data

        Returns:
            Created gateway
        """
        return self._request("POST", "/gateways", data=gateway_data)

    def patch_gateway(self, gateway_name: str, gateway_data: dict[str, Any]) -> dict[str, Any]:
        """Update properties on a gateway.

        Args:
            gateway_name: Gateway name
            gateway_data: Gateway properties to update

        Returns:
            Updated gateway
        """
        return self._request(
            "PATCH", f"/gateways/{quote(gateway_name, safe='')}", data=gateway_data
        )

    # Point endpoints
    def get_points(self, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        """Get points with pagination.

        Args:
            page: Page number
            per_page: Items per page

        Returns:
            Paginated response with points
        """
        params = {"page": page, "per_page": per_page}
        return self._request("GET", "/points", params=params)

    def get_point(self, point_name: str) -> dict[str, Any]:
        """Get a specific point.

        Args:
            point_name: Point name

        Returns:
            Point data
        """
        return self._request("GET", f"/points/{quote(point_name, safe='')}")

    def create_points(
        self,
        points_data: list[dict[str, Any]],
        overwrite_m_tags: bool = False,
        overwrite_kv_tags: bool = False,
    ) -> dict[str, Any]:
        """Create multiple points.

        Args:
            points_data: List of point data
            overwrite_m_tags: Enable to overwrite current Marker Tags
            overwrite_kv_tags: Enable to overwrite current Key Value Tags

        Returns:
            Created points
        """
        params = {"overwrite_m_tags": overwrite_m_tags, "overwrite_kv_tags": overwrite_kv_tags}
        # API expects the list wrapped in a dict with 'points' key according to swagger
        return self._request("POST", "/points", data={"points": points_data}, params=params)

    def update_point(
        self,
        point_name: str,
        point_data: dict[str, Any],
        overwrite_m_tags: bool = False,
        overwrite_kv_tags: bool = False,
    ) -> dict[str, Any]:
        """Update a point.

        Args:
            point_name: Point name
            point_data: Updated point data
            overwrite_m_tags: Enable to overwrite current Marker Tags
            overwrite_kv_tags: Enable to overwrite current Key Value Tags

        Returns:
            Updated point
        """
        params = {"overwrite_m_tags": overwrite_m_tags, "overwrite_kv_tags": overwrite_kv_tags}
        return self._request(
            "PUT", f"/points/{quote(point_name, safe='')}", data=point_data, params=params
        )

    def get_point_timeseries(
        self, point_name: str, start_time: str, end_time: str
    ) -> dict[str, Any]:
        """Get timeseries data for a point.

        Args:
            point_name: Point name
            start_time: ISO format start time
            end_time: ISO format end time

        Returns:
            Timeseries data
        """
        return self._request(
            "GET",
            f"/points/{quote(point_name, safe='')}/timeseries",
            params={"start_time": start_time, "end_time": end_time},
        )

    def get_points_timeseries(
        self, points: list[str], start_time: str, end_time: str
    ) -> dict[str, Any]:
        """Get timeseries data for multiple points.

        Args:
            points: List of point names
            start_time: ISO format start time
            end_time: ISO format end time

        Returns:
            Timeseries data
        """
        return self._request(
            "POST",
            "/points/get_timeseries",
            data={"points": points},
            params={"start_time": start_time, "end_time": end_time},
        )

    # Gateway-specific endpoints
    def get_gateway_der_events(
        self,
        gateway_name: str,
        page: int = 1,
        per_page: int = 100,
        get_past_events: bool = False,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """Get DER events for a gateway.

        Args:
            gateway_name: Gateway name
            page: Page number
            per_page: Items per page
            get_past_events: Get events from past 24 hours
            group_name: Filter by group name

        Returns:
            Paginated response with DER events
        """
        params = {"page": page, "per_page": per_page, "get_past_events": get_past_events}
        if group_name:
            params["group_name"] = group_name
        return self._request(
            "GET", f"/gateways/{quote(gateway_name, safe='')}/der_events", params=params
        )

    def create_gateway_token(self, gateway_name: str) -> dict[str, Any]:
        """Create a new token for a gateway.

        Args:
            gateway_name: Gateway name

        Returns:
            Authorization token
        """
        return self._request("POST", f"/gateways/{quote(gateway_name, safe='')}/token")

    # Volttron Agent endpoints for clients
    def get_client_volttron_agent_package_list(
        self,
        client_name: str,
        page: int = 1,
        per_page: int = 100,
        voltron_agent_package_name: str | None = None,
    ) -> dict[str, Any]:
        """Get list of Volttron agent packages for a client.

        Args:
            client_name: Client name
            page: Page number
            per_page: Items per page
            voltron_agent_package_name: Filter by package name

        Returns:
            Paginated response with agent packages
        """
        params = {"page": page, "per_page": per_page}
        if voltron_agent_package_name:
            params["voltron_agent_package_name"] = voltron_agent_package_name
        return self._request(
            "GET",
            f"/clients/{quote(client_name, safe='')}/volttron_agent_package/list",
            params=params,
        )

    def download_client_volttron_agent_package(
        self, client_name: str, volttron_agent_package_id: str
    ) -> bytes:
        """Download a Volttron agent package file.

        Args:
            client_name: Client name
            volttron_agent_package_id: Package ID to download

        Returns:
            File content as bytes
        """
        # This endpoint returns file content, not JSON
        # TODO: Implement proper binary download handling
        raise NotImplementedError("Binary file download not yet implemented")

    def upload_client_volttron_agent_package(
        self,
        client_name: str,
        file_path: str,
        package_name: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Upload a Volttron agent package for a client.

        Args:
            client_name: Client name
            file_path: Path to package file
            package_name: Package name
            description: Package description

        Returns:
            Upload result
        """
        file_path_obj = Path(file_path)
        # For .tar.gz files, force the MIME type to match what Swagger UI uses
        if str(file_path_obj).endswith(".tar.gz"):
            mime_type = "application/x-gzip"
        else:
            # Guess MIME type based on file extension
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                # Default MIME type for other file types
                if file_path_obj.suffix in (".whl", ".zip"):
                    mime_type = "application/zip"
                elif file_path_obj.suffix == ".gz":
                    mime_type = "application/x-gzip"
                else:
                    mime_type = "application/octet-stream"

        with file_path_obj.open("rb") as f:
            files = {"file": (file_path_obj.name, f, mime_type)}
            params = {"package_name": package_name}
            if description:
                params["description"] = description

            return self._request(
                "POST",
                f"/clients/{quote(client_name, safe='')}/volttron_agent_package",
                files=files,
                params=params,
            )

    # Volttron Agent endpoints for gateways
    def get_gateway_volttron_agents(
        self,
        gateway_name: str,
        page: int = 1,
        per_page: int = 100,
        volttron_agent_identity: str | None = None,
    ) -> dict[str, Any]:
        """Get list of Volttron agents for a gateway.

        Args:
            gateway_name: Gateway name
            page: Page number
            per_page: Items per page
            volttron_agent_identity: Filter by agent identity

        Returns:
            Paginated response with agents
        """
        params = {"page": page, "per_page": per_page}
        if volttron_agent_identity:
            params["volttron_agent_identity"] = volttron_agent_identity
        return self._request(
            "GET", f"/gateways/{quote(gateway_name, safe='')}/volttron_agents", params=params
        )

    def create_gateway_volttron_agents(
        self, gateway_name: str, volttron_agents: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create or update Volttron agents for a gateway.

        Args:
            gateway_name: Gateway name
            volttron_agents: List of agent configurations

        Returns:
            Created/updated agents
        """
        return self._request(
            "POST",
            f"/gateways/{quote(gateway_name, safe='')}/volttron_agents",
            data={"volttron_agents": volttron_agents},
        )

    # Hawke configuration endpoints
    def get_gateway_hawke_configuration(
        self,
        gateway_name: str,
        page: int = 1,
        per_page: int = 100,
        hash: str | None = None,
        use_base64_hash: bool = False,
    ) -> dict[str, Any]:
        """Get Hawke configurations for a gateway.

        Args:
            gateway_name: Gateway name
            page: Page number
            per_page: Items per page
            hash: Optional specific hash to retrieve
            use_base64_hash: Use base64 encoding for hash

        Returns:
            Paginated response with Hawke configs
        """
        params = {"page": page, "per_page": per_page, "use_base64_hash": use_base64_hash}
        if hash:
            params["hash"] = hash
        return self._request(
            "GET", f"/gateways/{quote(gateway_name, safe='')}/hawke_configuration", params=params
        )

    def create_gateway_hawke_configuration(
        self, gateway_name: str, hawke_configs: list[dict[str, Any]], use_base64_hash: bool = False
    ) -> dict[str, Any]:
        """Create or activate Hawke configurations.

        Args:
            gateway_name: Gateway name
            hawke_configs: List of Hawke configurations
            use_base64_hash: Use base64 encoding for hash

        Returns:
            Created/activated configs
        """
        return self._request(
            "POST",
            f"/gateways/{quote(gateway_name, safe='')}/hawke_configuration",
            data={"hawke_agents": hawke_configs},
            params={"use_base64_hash": use_base64_hash},
        )

    def get_gateway_hawke_agent_configuration(
        self,
        gateway_name: str,
        hawke_agent_id: str,
        hash: str | None = None,
        use_base64_hash: bool = False,
    ) -> dict[str, Any]:
        """Get configuration for specific Hawke agent.

        Args:
            gateway_name: Gateway name
            hawke_agent_id: Hawke agent ID
            hash: Optional specific hash to retrieve
            use_base64_hash: Use base64 encoding for hash

        Returns:
            Hawke agent configuration
        """
        params = {"use_base64_hash": use_base64_hash}
        if hash:
            params["hash"] = hash
        return self._request(
            "GET",
            f"/gateways/{quote(gateway_name, safe='')}/hawke_configuration/{quote(hawke_agent_id, safe='')}",
            params=params,
        )

    def create_gateway_hawke_agent_configuration(
        self,
        gateway_name: str,
        hawke_agent_id: str,
        config_data: dict[str, Any],
        use_base64_hash: bool = False,
    ) -> dict[str, Any]:
        """Create or activate Hawke agent configuration.

        Args:
            gateway_name: Gateway name
            hawke_agent_id: Hawke agent ID
            config_data: Configuration data
            use_base64_hash: Use base64 encoding for hash

        Returns:
            Created/activated config
        """
        return self._request(
            "POST",
            f"/gateways/{quote(gateway_name, safe='')}/hawke_configuration/{quote(hawke_agent_id, safe='')}",
            data=config_data,
            params={"use_base64_hash": use_base64_hash},
        )

    # Additional gateway endpoints
    def get_gateway_agent_configs(
        self,
        gateway_name: str,
        page: int = 1,
        per_page: int = 100,
        agent_identity: str | None = None,
        active: bool = True,
        use_base64_hash: bool = False,
    ) -> dict[str, Any]:
        """Get agent configurations for a gateway.

        Args:
            gateway_name: Gateway name
            page: Page number
            per_page: Items per page
            agent_identity: Filter by agent identity
            active: Filter active configs only
            use_base64_hash: Use base64 encoding for hash

        Returns:
            Paginated response with agent configs
        """
        params = {
            "page": page,
            "per_page": per_page,
            "active": active,
            "use_base64_hash": use_base64_hash,
        }
        if agent_identity:
            params["agent_identity"] = agent_identity
        return self._request(
            "GET", f"/gateways/{quote(gateway_name, safe='')}/agent_configs", params=params
        )

    def create_gateway_agent_configs(
        self, gateway_name: str, agent_configs: list[dict[str, Any]], use_base64_hash: bool = False
    ) -> dict[str, Any]:
        """Create agent configurations for a gateway.

        Args:
            gateway_name: Gateway name
            agent_configs: List of agent configurations
            use_base64_hash: Use base64 encoding for hash

        Returns:
            Created configs
        """
        return self._request(
            "POST",
            f"/gateways/{quote(gateway_name, safe='')}/agent_configs",
            data={"agent_configs": agent_configs},
            params={"use_base64_hash": use_base64_hash},
        )

    # PCAP endpoints
    def get_gateway_pcap_list(
        self, gateway_name: str, start_time: str, end_time: str, page: int = 1, per_page: int = 100
    ) -> dict[str, Any]:
        """Get list of PCAP files for a gateway.

        Args:
            gateway_name: Gateway name
            start_time: ISO format start time
            end_time: ISO format end time
            page: Page number
            per_page: Items per page

        Returns:
            Paginated response with file names
        """
        return self._request(
            "GET",
            f"/gateways/{quote(gateway_name, safe='')}/pcap/list",
            params={
                "start_time": start_time,
                "end_time": end_time,
                "page": page,
                "per_page": per_page,
            },
        )

    def download_gateway_pcap(self, gateway_name: str, file_name: str) -> bytes:
        """Download a PCAP file from a gateway.

        Args:
            gateway_name: Gateway name
            file_name: File name to download

        Returns:
            File content as bytes
        """
        # This endpoint returns file content, not JSON
        # TODO: Implement proper binary download handling
        raise NotImplementedError("Binary file download not yet implemented")

    def upload_gateway_pcap(self, gateway_name: str, file_path: str) -> dict[str, Any]:
        """Upload a PCAP file for a gateway.

        Args:
            gateway_name: Gateway name
            file_path: Path to PCAP file

        Returns:
            Upload result
        """
        file_path_obj = Path(file_path)
        # PCAP files have a specific MIME type
        mime_type = "application/vnd.tcpdump.pcap"

        with file_path_obj.open("rb") as f:
            files = {"file": (file_path_obj.name, f, mime_type)}
            return self._request(
                "POST", f"/gateways/{quote(gateway_name, safe='')}/pcap", files=files
            )

    # Volttron agent config package endpoint
    def get_gateway_volttron_agent_config_package(
        self,
        gateway_name: str,
        volttron_agent_identity: str,
        use_agent_config_base64_hash: bool = False,
    ) -> dict[str, Any]:
        """Get Volttron agent with config and package.

        Args:
            gateway_name: Gateway name
            volttron_agent_identity: Agent identity
            use_agent_config_base64_hash: Use base64 encoding for config hash

        Returns:
            Agent with config and package info
        """
        return self._request(
            "GET",
            f"/gateways/{quote(gateway_name, safe='')}/volttron_agent_config_package",
            params={
                "volttron_agent_identity": volttron_agent_identity,
                "use_agent_config_base64_hash": use_agent_config_base64_hash,
            },
        )

    def create_gateway_volttron_agent_config_package(
        self,
        gateway_name: str,
        volttron_agent: dict[str, Any],
        agent_config: dict[str, Any] | None = None,
        use_agent_config_base64_hash: bool = False,
    ) -> dict[str, Any]:
        """Create Volttron agent with config and package link.

        Args:
            gateway_name: Gateway name
            volttron_agent: Agent data (required)
            agent_config: Agent config data (optional)
            use_agent_config_base64_hash: Use base64 encoding for config hash

        Returns:
            Created agent with config
        """
        data = {"volttron_agent": volttron_agent}
        if agent_config:
            data["agent_config"] = agent_config

        return self._request(
            "POST",
            f"/gateways/{quote(gateway_name, safe='')}/volttron_agent_config_package",
            data=data,
            params={"use_agent_config_base64_hash": use_agent_config_base64_hash},
        )

    @classmethod
    def from_config(cls, config: Any) -> "APIClient":
        """Create API client from config object.

        Args:
            config: Configuration object with base_url, api_key, and timeout attributes

        Returns:
            APIClient instance
        """
        return cls(
            base_url=getattr(config, "base_url", None),
            api_key=getattr(config, "api_key", None),
            timeout=getattr(config, "timeout", 30),
        )
