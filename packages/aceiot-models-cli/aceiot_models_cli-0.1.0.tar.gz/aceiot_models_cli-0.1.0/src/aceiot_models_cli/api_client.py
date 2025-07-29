"""API client for interacting with the ACE IoT API."""

import contextlib
from typing import Any
from urllib.parse import urljoin

import requests
from aceiot_models import (
    ClientCreate,
    DerEventCreate,
    DerEventUpdate,
    GatewayCreate,
    GatewayUpdate,
    PointCreate,
    PointUpdate,
    SiteCreate,
)
from aceiot_models.serializers import serialize_for_api
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None, response_data: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class APIClient:
    """Client for interacting with the ACE IoT API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """Initialize the API client.

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Create session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "authorization": f"Bearer {self.api_key}",  # Bearer token format
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            json_data: JSON data to send in request body
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        # Ensure base_url ends with / and endpoint doesn't start with /
        base = self.base_url.rstrip("/") + "/"
        endpoint_path = endpoint.lstrip("/")
        url = urljoin(base, endpoint_path)

        # Debug logging
        import os

        if os.environ.get("ACEIOT_DEBUG"):
            print(f"DEBUG: Making {method} request to {url}")
            if params:
                print(f"DEBUG: Query params: {params}")
            print(
                f"DEBUG: Authorization header: {self.session.headers.get('authorization', 'Not set')}"
            )

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout,
                **kwargs,
            )

            # Check for errors
            if response.status_code >= 400:
                error_data = None
                with contextlib.suppress(Exception):
                    error_data = response.json()

                raise APIError(
                    f"API request failed: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            # Return JSON response
            if response.content:
                try:
                    return response.json()
                except ValueError as e:
                    # If JSON parsing fails, raise an informative error
                    raise APIError(
                        f"Invalid JSON response: {e}. Response content: {response.text[:200]}"
                    )
            return {}

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}") from e

    # Client operations
    def get_clients(self, page: int = 1, per_page: int = 10) -> dict[str, Any]:
        """Get list of clients."""
        return self._make_request("GET", "/clients/", params={"page": page, "per_page": per_page})

    def get_client(self, client_name: str) -> dict[str, Any]:
        """Get a specific client."""
        return self._make_request("GET", f"/clients/{client_name}")

    def create_client(self, client: ClientCreate) -> dict[str, Any]:
        """Create a new client."""
        data = serialize_for_api(client)
        return self._make_request("POST", "/clients/", json_data=data)

    # Site operations
    def get_sites(
        self,
        page: int = 1,
        per_page: int = 10,
        client_name: str | None = None,
        collect_enabled: bool = False,
        show_archived: bool = False,
    ) -> dict[str, Any]:
        """Get list of sites."""
        params = {
            "page": page,
            "per_page": per_page,
            "collect_enabled": collect_enabled,
            "show_archived": show_archived,
        }

        if client_name:
            # Get sites for specific client
            return self._make_request("GET", f"/clients/{client_name}/sites", params=params)
        else:
            # Get all sites
            return self._make_request("GET", "/sites/", params=params)

    def get_site(self, site_name: str) -> dict[str, Any]:
        """Get a specific site."""
        return self._make_request("GET", f"/sites/{site_name}")

    def create_site(self, site: SiteCreate) -> dict[str, Any]:
        """Create a new site."""
        data = serialize_for_api(site)
        return self._make_request("POST", "/sites/", json_data=data)

    def get_site_timeseries(self, site_name: str, start_time: str, end_time: str) -> dict[str, Any]:
        """Get timeseries data for a site."""
        params = {"start_time": start_time, "end_time": end_time}
        return self._make_request("GET", f"/sites/{site_name}/timeseries", params=params)

    def get_site_weather(self, site_name: str) -> dict[str, Any]:
        """Get weather data for a site."""
        return self._make_request("GET", f"/sites/{site_name}/weather")

    # Gateway operations
    def get_gateways(
        self, page: int = 1, per_page: int = 10, show_archived: bool = False
    ) -> dict[str, Any]:
        """Get list of gateways."""
        params = {"page": page, "per_page": per_page, "show_archived": show_archived}
        return self._make_request("GET", "/gateways/", params=params)

    def get_gateway(self, gateway_name: str) -> dict[str, Any]:
        """Get a specific gateway."""
        return self._make_request("GET", f"/gateways/{gateway_name}")

    def create_gateway(self, gateway: GatewayCreate) -> dict[str, Any]:
        """Create a new gateway."""
        data = serialize_for_api(gateway)
        return self._make_request("POST", "/gateways/", json_data=data)

    def update_gateway(self, gateway_name: str, gateway: GatewayUpdate) -> dict[str, Any]:
        """Update a gateway."""
        data = serialize_for_api(gateway)
        return self._make_request("PATCH", f"/gateways/{gateway_name}", json_data=data)

    def create_gateway_token(self, gateway_name: str) -> dict[str, Any]:
        """Create a new token for a gateway."""
        return self._make_request("POST", f"/gateways/{gateway_name}/token")

    # Point operations
    def get_points(self, page: int = 1, per_page: int = 10) -> dict[str, Any]:
        """Get list of points."""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", "/points/", params=params)

    def get_point(self, point_name: str) -> dict[str, Any]:
        """Get a specific point."""
        return self._make_request("GET", f"/points/{point_name}")

    def create_points(
        self,
        points: list[PointCreate],
        overwrite_m_tags: bool = False,
        overwrite_kv_tags: bool = False,
    ) -> dict[str, Any]:
        """Create new points."""
        data = {"points": [serialize_for_api(p) for p in points]}
        params = {"overwrite_m_tags": overwrite_m_tags, "overwrite_kv_tags": overwrite_kv_tags}
        return self._make_request("POST", "/points/", json_data=data, params=params)

    def update_point(
        self,
        point_name: str,
        point: PointUpdate,
        overwrite_m_tags: bool = False,
        overwrite_kv_tags: bool = False,
    ) -> dict[str, Any]:
        """Update a point."""
        data = serialize_for_api(point)
        params = {"overwrite_m_tags": overwrite_m_tags, "overwrite_kv_tags": overwrite_kv_tags}
        return self._make_request("PUT", f"/points/{point_name}", json_data=data, params=params)

    def get_point_timeseries(
        self, point_name: str, start_time: str, end_time: str
    ) -> dict[str, Any]:
        """Get timeseries data for a point."""
        params = {"start_time": start_time, "end_time": end_time}
        return self._make_request("GET", f"/points/{point_name}/timeseries", params=params)

    def get_points_timeseries(
        self, point_names: list[str], start_time: str, end_time: str
    ) -> dict[str, Any]:
        """Get timeseries data for multiple points."""
        data = {"points": [{"name": name} for name in point_names]}
        params = {"start_time": start_time, "end_time": end_time}
        return self._make_request("POST", "/points/get_timeseries", json_data=data, params=params)

    def get_site_points(self, site_name: str, page: int = 1, per_page: int = 10) -> dict[str, Any]:
        """Get points for a specific site."""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", f"/sites/{site_name}/points", params=params)

    def get_site_configured_points(
        self, site_name: str, page: int = 1, per_page: int = 10
    ) -> dict[str, Any]:
        """Get configured points for a specific site."""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", f"/sites/{site_name}/configured_points", params=params)

    # DER Event operations
    def get_client_der_events(
        self,
        client_name: str,
        get_past_events: bool = False,
        group_name: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        """Get DER events for a client."""
        params = {
            "get_past_events": get_past_events,
            "page": page,
            "per_page": per_page,
        }
        if group_name:
            params["group_name"] = group_name

        return self._make_request("GET", f"/clients/{client_name}/der_events", params=params)

    def create_client_der_events(
        self, client_name: str, events: list[DerEventCreate]
    ) -> dict[str, Any]:
        """Create DER events for a client."""
        data = {"der_events": [serialize_for_api(e) for e in events]}
        return self._make_request("POST", f"/clients/{client_name}/der_events", json_data=data)

    def update_client_der_events(
        self, client_name: str, events: list[DerEventUpdate]
    ) -> dict[str, Any]:
        """Update DER events for a client."""
        data = {"der_events": [serialize_for_api(e) for e in events]}
        return self._make_request("PUT", f"/clients/{client_name}/der_events", json_data=data)

    def get_gateway_der_events(
        self,
        gateway_name: str,
        get_past_events: bool = False,
        group_name: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        """Get DER events for a gateway."""
        params = {
            "get_past_events": get_past_events,
            "page": page,
            "per_page": per_page,
        }
        if group_name:
            params["group_name"] = group_name

        return self._make_request("GET", f"/gateways/{gateway_name}/der_events", params=params)

    # Volttron Agent operations
    def get_gateway_volttron_agents(
        self,
        gateway_name: str,
        volttron_agent_identity: str | None = None,
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        """Get Volttron agents for a gateway."""
        params = {"page": page, "per_page": per_page}
        if volttron_agent_identity:
            params["volttron_agent_identity"] = volttron_agent_identity

        return self._make_request("GET", f"/gateways/{gateway_name}/volttron_agents", params=params)

    # Agent Config operations
    def get_gateway_agent_configs(
        self,
        gateway_name: str,
        agent_identity: str | None = None,
        active: bool = True,
        use_base64_hash: bool = False,
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        """Get agent configs for a gateway."""
        params = {
            "page": page,
            "per_page": per_page,
            "active": active,
            "use_base64_hash": use_base64_hash,
        }
        if agent_identity:
            params["agent_identity"] = agent_identity

        return self._make_request("GET", f"/gateways/{gateway_name}/agent_configs", params=params)

    # Hawke configuration operations
    def get_gateway_hawke_configs(
        self,
        gateway_name: str,
        hash_value: str | None = None,
        use_base64_hash: bool = False,
        page: int = 1,
        per_page: int = 10,
    ) -> dict[str, Any]:
        """Get Hawke configurations for a gateway."""
        params = {
            "page": page,
            "per_page": per_page,
            "use_base64_hash": use_base64_hash,
        }
        if hash_value:
            params["hash"] = hash_value

        return self._make_request(
            "GET", f"/gateways/{gateway_name}/hawke_configuration", params=params
        )

    # BACnet-specific operations
    def get_discovered_points(
        self, site_name: str, page: int = 1, per_page: int = 500
    ) -> dict[str, Any]:
        """Get discovered BACnet points for a site.

        This endpoint returns points that have been discovered through BACnet
        scanning but may not yet be configured for collection.

        Args:
            site_name: Name of the site
            page: Page number
            per_page: Items per page

        Returns:
            Dictionary with 'items' containing discovered points
        """
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", f"/sites/{site_name}/points", params=params)

    def get_points_timeseries_batch(
        self,
        point_names: list[str],
        start_time: str,
        end_time: str,
        batch_size: int = 100,
    ) -> dict[str, Any]:
        """Get timeseries data for multiple points with automatic batching.

        This method automatically handles large lists of points by splitting
        them into batches to avoid API limits.

        Args:
            point_names: List of point names
            start_time: Start time in ISO format
            end_time: End time in ISO format
            batch_size: Maximum points per request (default: 100)

        Returns:
            Combined timeseries data from all batches
        """
        from .utils import batch_process

        all_samples = []
        params = {"start_time": start_time, "end_time": end_time}

        def process_batch(batch: list[str]) -> dict[str, Any]:
            data = {"points": [{"name": name} for name in batch]}
            response = self._make_request(
                "POST", "/points/get_timeseries", json_data=data, params=params
            )
            all_samples.extend(response.get("point_samples", []))
            return response

        # Process in batches
        batch_process(point_names, process_batch, batch_size=batch_size)

        return {"point_samples": all_samples}
