import json
from unittest.mock import MagicMock, patch, PropertyMock
from requests import HTTPError, Response
import pytest
from threecxapi.exceptions import APIError, APIAuthenticationError, APIAuthenticationTokenRefreshError
from threecxapi.components.schemas.pbx.ODataErrors.ODataErrors import ODataError


class TestAPIError:

    @pytest.fixture
    def http_error(self) -> HTTPError:
        mock_response = MagicMock()
        mock_response.status_code = 401
        error_response = {
                "error": {
                    "code": "",
                    "message": "Number:\nWARNINGS.XAPI.SAMPLE_ERROR",
                    "details": [
                        {
                            "code": "",
                            "message": "WARNINGS.XAPI.SAMPLE_ERROR",
                            "target": "SAMPLE_FIELD",
                        }
                    ],
                }
            }
        mock_response.json.return_value = error_response
        mock_response.text = json.dumps(error_response)
        return HTTPError("An error occured.", response=mock_response)

    def test_init(self, http_error):
        # Instantiate the APIError
        with patch.object(APIError, "_parse_http_error") as mock_parse_http_error:
            api_error = APIError(http_error, message="Test API Error")
            mock_parse_http_error.assert_called_once_with()

        assert api_error.http_error == http_error
        assert api_error.odata_error is None
        assert api_error.message == "Test API Error"

    def test_parse_http_error(self, http_error):
        api_error = APIError(http_error, message="Test API Error")
        assert isinstance(api_error.odata_error, ODataError)
        assert str(api_error) == "Test API Error OData Error: Number:\nWARNINGS.XAPI.SAMPLE_ERROR"

    def test_parse_http_error_invalid_json_response(self, http_error):
        http_error.response.json.side_effect = json.JSONDecodeError("test", "test", 1)
        api_error = APIError(http_error, message="Test API Error")

        assert api_error.http_error == http_error
        assert api_error.odata_error is None
        assert f"Invalid JSON in response: {http_error.response.text}" in api_error.message

    def test_parse_http_error_invalid_odata_error_response(self, http_error):
        # Mock the HTTPError and its response
        http_error.response.json.return_value = {
            "error": {
                "invalid_field": "This field is not part of the schema"
            }
        }

        api_error = APIError(http_error, message="Test API Error")

        assert api_error.http_error == http_error
        assert api_error.odata_error is None
        assert "Error parsing ODataError" in api_error.message

    def test_parse_http_error_general_exception(self, http_error):
        http_error.response.json.side_effect = Exception("Uknown Error")
        api_error = APIError(http_error, message="Test API Error")

        assert api_error.http_error == http_error
        assert api_error.odata_error is None
        assert "An unknown error has occured: Uknown Error" in api_error.message

    def test_parse_http_error_missing_response(self, http_error):
        http_error.response = None
        api_error = APIError(http_error, message="Test API Error")

        assert api_error.http_error == http_error
        assert api_error.odata_error is None
        assert "No response available in HTTPError." in api_error.message

    def test_str_with_odata_error(self, http_error):
        # With odata error present
        api_error = APIError(http_error, message="Test API Error")
        assert str(api_error) == "Test API Error OData Error: Number:\nWARNINGS.XAPI.SAMPLE_ERROR"
    
    def test_str_without_odata_error(self, http_error):
        # With odata error missing
        api_error = APIError(http_error, message="Test API Error")
        api_error.odata_error = None
        assert str(api_error) == "Test API Error"


class TestAPIAuthenticationError:

    @pytest.fixture
    def mock_response(self):
        mock_response = MagicMock()
        mock_response.status_code = 401
        yield mock_response

    @pytest.fixture
    def http_error(self, mock_response):
        http_error = HTTPError("Test Error Message", response=mock_response)
        yield http_error

    def test_init(self, http_error):
        auth_error = APIAuthenticationError(http_error)

        assert auth_error.original_exception == http_error

    def test_status_code_with_response(self, http_error):
        auth_error = APIAuthenticationError(http_error)

        assert auth_error.status_code == 401

    def test_status_code_without_response(self):
        auth_error = APIAuthenticationError(HTTPError())

        assert auth_error.status_code is None

    def test_error_message(self, http_error):
        auth_error = APIAuthenticationError(http_error)

        assert auth_error.error_message == "Test Error Message"

    def test_str(self):
        # Mock HTTPError with response and message
        http_error = HTTPError("Invalid Credentials.")
        http_error.response = MagicMock(spec=Response)

        with patch.object(APIAuthenticationError, "status_code", new_callable=PropertyMock) as mock_status_code:
            mock_status_code.return_value = 418
            auth_error = APIAuthenticationError(http_error)
            assert str(auth_error) == "Authentication Failure. (418) Invalid Credentials."


class TestAPIAuthenticationTokenRefreshError:
    def test_str(self):
        # Mock HTTPError with response and message
        mock_http_error = HTTPError("An Error Occured.")
        mock_http_error.response = MagicMock(spec=Response)

        with patch.object(APIAuthenticationTokenRefreshError, "status_code", new_callable=PropertyMock) as mock_status_code:
            mock_status_code.return_value = 418
            auth_error = APIAuthenticationTokenRefreshError(mock_http_error)
            assert str(auth_error) == "Failed to refresh authentication token. (418) An Error Occured."
