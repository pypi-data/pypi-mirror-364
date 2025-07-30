import pytest
import requests
import time
from unittest.mock import patch, MagicMock, PropertyMock
from threecxapi.connection import ThreeCXApiConnection, AuthenticationToken
from threecxapi.exceptions import APIAuthenticationError, APIAuthenticationTokenRefreshError


class TestThreeCXApiConnection:

    @pytest.fixture
    def mock_response(self):
        # Mock a basic response object from requests
        response = MagicMock(spec=requests.Response)
        response.status_code = 200
        response.text = '{"key": "value"}'
        return response

    @pytest.fixture
    def api_connection(self):
        # Get a connection object with a mocked _make_request method
        with patch.object(ThreeCXApiConnection, "_make_request", return_value=MagicMock(spec=requests.Response)):
            api_connection = ThreeCXApiConnection(server_url="https://example.com")
            api_connection.session = MagicMock(spec=requests.Session)
            yield api_connection

    def test_api_url(self, api_connection):
        assert api_connection.api_url == "https://example.com/xapi/v1"

    def test_token_getter(self, api_connection):
        token = AuthenticationToken(
            **{"token_type": "Bearer", "expires_in": 3600, "access_token": "access", "refresh_token": "refresh"}
        )
        api_connection._token = token
        assert api_connection.token == token

    def test_token_setter(self, api_connection):
        token = {"token_type": "Bearer", "expires_in": 3600, "access_token": "access", "refresh_token": "refresh"}
        api_connection.token = token
        assert api_connection._token == AuthenticationToken(**token)

    @patch("threecxapi.connection.requests.Session")
    def test_init(self, mock_requests_session):
        # Setup the mock session that is created during init
        mock_session = MagicMock()
        mock_requests_session.return_value = mock_session

        # Initialize the object
        api_connection = ThreeCXApiConnection(server_url="https://example.com")

        # Assert all init variables are set correctly
        assert api_connection.server_url == "https://example.com"
        assert api_connection.api_path == "/xapi/v1"
        assert api_connection.session == mock_session
        assert api_connection.token_expiry_time == 0
        assert api_connection._token is None

    def test_get_api_endpoint_url(self, api_connection):
        assert api_connection._get_api_endpoint_url("endpoint") == "https://example.com/xapi/v1/endpoint"

    def test_get_with_params(self, api_connection, mock_response):
        # Set up our mock response from the _make_request method
        api_connection._make_request.return_value = mock_response
        # Set up parameters needed for making a get request
        return_data = {"key": "value"}
        query_params = MagicMock(model_dump=MagicMock(return_value=return_data))  # Mocking the QueryParameters class
        endpoint = "/test-endpoint"

        result = api_connection.get(endpoint, params=query_params)

        api_connection._make_request.assert_called_once_with("get", endpoint, params=return_data)
        query_params.model_dump.assert_called_once_with(exclude_none=True, by_alias=True)
        assert result == mock_response

    def test_get_without_params(mself, api_connection, mock_response):
        api_connection._make_request.return_value = mock_response
        endpoint = "/test-endpoint"

        result = api_connection.get(endpoint)

        api_connection._make_request.assert_called_once_with("get", endpoint, params=None)
        assert result == mock_response

    def test_post(self, api_connection, mock_response):
        data = {"key": "value"}
        api_connection._make_request.return_value = mock_response

        response = api_connection.post("endpoint", data)

        api_connection._make_request.assert_called_once_with("post", "endpoint", json=data)
        assert response == mock_response

    def test_patch(self, api_connection, mock_response):
        data = {"key": "value"}
        api_connection._make_request.return_value = mock_response

        response = api_connection.patch("endpoint", data)

        api_connection._make_request.assert_called_once_with("patch", "endpoint", json=data)
        assert response == mock_response

    def test_delete(self, api_connection, mock_response):
        data = 1
        api_connection._make_request.return_value = mock_response

        response = api_connection.delete("endpoint", data)

        api_connection._make_request.assert_called_once_with("delete", "endpoint", params=data)
        assert response == mock_response

    @patch("threecxapi.connection.requests.Session")
    def test_authenticate_success(self, mock_session_class):
        # Patch token again in the test to track setter calls
        with patch.object(ThreeCXApiConnection, "token", new_callable=PropertyMock) as mock_token:
            token = {
                "Token": {
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "access_token": "access",
                    "refresh_token": "refresh",
                }
            }
            mock_response = MagicMock()
            mock_response.json.return_value = token
            api_connection = ThreeCXApiConnection(server_url="https://example.com")
            api_connection.session.post.return_value = mock_response

            # Call the method that sets self.token
            api_connection.authenticate("username", "password")

            # Assert the setter was called with the correct token value
            mock_token.mock_calls
            mock_token.assert_called_with(token["Token"])

    def test_authenticate_failure(self, api_connection):
        with pytest.raises(APIAuthenticationError) as context:
            mock_response = MagicMock(spec=requests.models.Response)
            mock_response.status_code = 418
            mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
            api_connection.session.post.return_value = mock_response

            api_connection.authenticate("username", "password")

        exc = context.value
        assert exc.status_code == 418
        assert isinstance(exc.original_exception, requests.HTTPError)

    def test_is_token_expired(self, api_connection):
        api_connection.token_expiry_time = time.time() - 10  # Set expiry time in the past
        assert api_connection._is_token_expired() is True

        api_connection.token_expiry_time = time.time() + 10  # Set expiry time in the future
        assert api_connection._is_token_expired() is False

    def test_update_token_expiry_time(self, api_connection):
        current_time = time.time()
        api_connection._update_token_expiry_time(3600)
        assert api_connection.token_expiry_time > current_time

    def test_get_headers_with_token(self, api_connection):
        token = AuthenticationToken("Bearer", 3600, "access", "refresh")
        api_connection._token = token
        headers = api_connection._get_headers()
        assert headers["Authorization"] == "Bearer access"

    def test_get_headers_without_token(self, api_connection):
        headers = api_connection._get_headers()
        assert "Authorization" not in headers

    def test_make_request_with_expired_token(self, mock_response):
        api_connection = ThreeCXApiConnection(server_url="https://example.com")
        mock_session = MagicMock(spec=requests.Session)
        mock_session.request.return_value = mock_response
        api_connection.session = mock_session
        # Set up expected parameters for our call
        method = "method"
        endpoint = "endpoint"
        other_argument = {"other_argument": 100}
        endpoint_url = api_connection._get_api_endpoint_url(endpoint)
        headers = api_connection._get_headers()

        # Perform call where _is_token_expired is False and mock _refresh_access_token
        with patch.object(api_connection, "_is_token_expired", return_value=True), patch.object(
            api_connection, "_refresh_access_token"
        ) as mock_refresh:
            response = api_connection._make_request(method, endpoint, **other_argument)

        mock_refresh.assert_called_once_with()
        mock_session.request.assert_called_once_with(method, endpoint_url, headers=headers, **other_argument)
        mock_response.raise_for_status.assert_called_once_with()
        assert response == mock_response

    def test_make_request_without_expired_token(self, mock_response):
        api_connection = ThreeCXApiConnection(server_url="https://example.com")
        mock_session = MagicMock(spec=requests.Session)
        mock_session.request.return_value = mock_response
        api_connection.session = mock_session
        # Set up expected parameters for our call
        method = "method"
        endpoint = "endpoint"
        other_argument = {"other_argument": 100}
        endpoint_url = api_connection._get_api_endpoint_url(endpoint)
        headers = api_connection._get_headers()

        # Perform call where _is_token_expired is False and mock _refresh_access_token
        with patch.object(api_connection, "_is_token_expired", return_value=False), patch.object(
            api_connection, "_refresh_access_token"
        ) as mock_refresh:
            response = api_connection._make_request(method, endpoint, **other_argument)

        mock_refresh.assert_not_called()
        mock_session.request.assert_called_once_with(method, endpoint_url, headers=headers, **other_argument)
        mock_response.raise_for_status.assert_called_once_with()
        assert response == mock_response

    def test_refresh_access_token(self, api_connection):
        # Set the initial AuthToken
        api_connection._token = AuthenticationToken("Bearer", 3600, "access", "refresh")

        # Setup the response data and what
        response_data = {
            "token_type": "Bearer",
            "expires_in": 10000,
            "access_token": "new_access",
            "refresh_token": "new_refresh",
        }
        expected_auth_token = AuthenticationToken(**response_data)

        # Setup a mock response for our post request
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        api_connection.session.post.return_value = mock_response
        token_refresh_url = api_connection.server_url + "/connect/token"
        token_refresh_data = {
            "client_id": "Webclient",
            "grant_type": "refresh_token",
            "refresh_token": api_connection._token.refresh_token,
        }

        # Refresh the access token
        api_connection._refresh_access_token()

        # Verify the request was correct, that we checked for errors,
        # and that we ultimately have a new expected AuthToken
        api_connection.session.post.assert_called_once_with(url=token_refresh_url, data=token_refresh_data)
        mock_response.raise_for_status.assert_called_once_with()
        assert api_connection._token == expected_auth_token

    def test_refresh_access_token_with_http_error(self, api_connection):
        # Set the initial AuthToken
        api_connection._token = AuthenticationToken("Bearer", 3600, "access", "refresh")

        # Set up a mock response with an exception
        mock_response = MagicMock(spec=requests.models.Response)
        mock_response.status_code = 418
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        api_connection.session.post.return_value = mock_response

        # Refresh the access token
        with pytest.raises(APIAuthenticationTokenRefreshError) as context:
            api_connection._refresh_access_token()

        exc = context.value
        assert exc.status_code == 418
        assert isinstance(exc.original_exception, requests.HTTPError)

    @patch("threecxapi.connection.time")
    def test__update_token_expiry_time(self, mock_time_class, api_connection):
        """
        Test that _update_token_expiry_time correctly calculates the token expiry time.
        """
        # Setup time value
        expires_in = 100
        mock_time_class.time.return_value = 1000
        expected_time = expires_in + 1000

        # Update token expiry time
        api_connection._update_token_expiry_time(expires_in=expires_in)

        # Assert token expiry time is as expected
        assert api_connection.token_expiry_time == expected_time
