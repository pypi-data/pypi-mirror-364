"""Tests for the API client."""

from unittest.mock import Mock, patch

import pytest
import requests
from aceiot_models import ClientCreate

from aceiot_models_cli.api_client import APIClient, APIError


class TestAPIClient:
    """Test APIClient functionality."""

    @pytest.fixture
    def api_client(self):
        """Create an API client instance."""
        return APIClient("https://test.api.com", "test-api-key")

    def test_api_client_init(self, api_client):
        """Test API client initialization."""
        assert api_client.base_url == "https://test.api.com"
        assert api_client.api_key == "test-api-key"
        assert api_client.timeout == 30
        assert "Authorization" in api_client.session.headers
        assert api_client.session.headers["Authorization"] == "Bearer test-api-key"

    def test_api_client_custom_timeout(self):
        """Test API client with custom timeout."""
        client = APIClient("https://test.api.com", "key", timeout=60)
        assert client.timeout == 60

    @patch("aceiot_models_cli.api_client.requests.Session")
    def test_make_request_success(self, mock_session_class):
        """Test successful API request."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = APIClient("https://test.api.com", "key")
        result = client._make_request("GET", "/test")

        assert result == {"result": "success"}
        mock_session.request.assert_called_once()

    @patch("aceiot_models_cli.api_client.requests.Session")
    def test_make_request_error(self, mock_session_class):
        """Test API request with error response."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.json.return_value = {"error": "Not found"}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = APIClient("https://test.api.com", "key")

        with pytest.raises(APIError) as exc_info:
            client._make_request("GET", "/test")

        assert exc_info.value.status_code == 404
        assert "404" in str(exc_info.value)

    @patch("aceiot_models_cli.api_client.requests.Session")
    def test_make_request_network_error(self, mock_session_class):
        """Test API request with network error."""
        mock_session = Mock()
        mock_session.request.side_effect = requests.exceptions.ConnectionError("Network error")
        mock_session_class.return_value = mock_session

        client = APIClient("https://test.api.com", "key")

        with pytest.raises(APIError) as exc_info:
            client._make_request("GET", "/test")

        assert "Request failed: Network error" in str(exc_info.value)

    def test_get_clients(self, api_client):
        """Test get_clients method."""
        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {"items": []}
            result = api_client.get_clients(page=2, per_page=20)

            assert result == {"items": []}
            mock_request.assert_called_once_with(
                "GET", "/clients/", params={"page": 2, "per_page": 20}
            )

    def test_get_client(self, api_client):
        """Test get_client method."""
        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {"name": "test"}
            result = api_client.get_client("test")

            assert result == {"name": "test"}
            mock_request.assert_called_once_with("GET", "/clients/test")

    def test_create_client(self, api_client):
        """Test create_client method."""
        client = ClientCreate(name="new-client", nice_name="New Client")

        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {"id": 1}
            result = api_client.create_client(client)

            assert result == {"id": 1}
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0] == ("POST", "/clients/")
            assert "json_data" in call_args[1]

    def test_get_sites_all(self, api_client):
        """Test get_sites method for all sites."""
        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {"items": []}
            result = api_client.get_sites()

            assert result == {"items": []}
            mock_request.assert_called_once_with(
                "GET",
                "/sites/",
                params={
                    "page": 1,
                    "per_page": 10,
                    "collect_enabled": False,
                    "show_archived": False,
                },
            )

    def test_get_sites_for_client(self, api_client):
        """Test get_sites method for specific client."""
        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {"items": []}
            result = api_client.get_sites(client_name="client1")

            assert result == {"items": []}
            mock_request.assert_called_once_with(
                "GET",
                "/clients/client1/sites",
                params={
                    "page": 1,
                    "per_page": 10,
                    "collect_enabled": False,
                    "show_archived": False,
                },
            )

    def test_get_point_timeseries(self, api_client):
        """Test get_point_timeseries method."""
        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {"point_samples": []}
            result = api_client.get_point_timeseries("point1", "2024-01-01", "2024-01-02")

            assert result == {"point_samples": []}
            mock_request.assert_called_once_with(
                "GET",
                "/points/point1/timeseries",
                params={"start_time": "2024-01-01", "end_time": "2024-01-02"},
            )

    def test_base_url_trailing_slash(self):
        """Test that base URL trailing slash is handled correctly."""
        client1 = APIClient("https://test.api.com/", "key")
        client2 = APIClient("https://test.api.com", "key")

        assert client1.base_url == "https://test.api.com"
        assert client2.base_url == "https://test.api.com"

    def test_get_discovered_points(self, api_client):
        """Test get_discovered_points method."""
        with patch.object(api_client, "_make_request") as mock_request:
            mock_request.return_value = {
                "items": [{"name": "point1"}, {"name": "point2"}],
                "page": 1,
                "pages": 1,
            }
            result = api_client.get_discovered_points("test_site")

            assert len(result["items"]) == 2
            mock_request.assert_called_once_with(
                "GET",
                "/sites/test_site/points",
                params={"page": 1, "per_page": 500},
            )

    def test_get_points_timeseries_batch(self, api_client):
        """Test get_points_timeseries_batch method with automatic batching."""
        # Create 250 point names to test batching
        point_names = [f"point_{i}" for i in range(250)]

        with patch.object(api_client, "_make_request") as mock_request:
            # Mock responses for 3 batches
            mock_request.side_effect = [
                {"point_samples": [{"name": f"point_{i}", "value": i} for i in range(100)]},
                {"point_samples": [{"name": f"point_{i}", "value": i} for i in range(100, 200)]},
                {"point_samples": [{"name": f"point_{i}", "value": i} for i in range(200, 250)]},
            ]

            result = api_client.get_points_timeseries_batch(
                point_names, "2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z", batch_size=100
            )

            # Should have all 250 samples combined
            assert len(result["point_samples"]) == 250

            # Should have made 3 API calls
            assert mock_request.call_count == 3

            # Check first batch call
            first_call = mock_request.call_args_list[0]
            assert first_call[0][0] == "POST"
            assert first_call[0][1] == "/points/get_timeseries"
            assert len(first_call[1]["json_data"]["points"]) == 100
