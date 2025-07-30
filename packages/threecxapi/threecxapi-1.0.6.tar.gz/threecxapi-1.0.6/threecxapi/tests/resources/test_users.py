import requests
import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock
from threecxapi.components.responses.other import HasDuplicatedEmailResponse
from threecxapi.components.responses.pbx import UserCollectionResponse
from threecxapi.resources.exceptions.users_exceptions import (
    UserCreateError,
    UserListError,
    UserDeleteError,
    UserGetError,
    UserHotdeskLogoutError,
    UserHotdeskLookupError,
    UserUpdateError,
    UserHasDuplicatedEmailError,
)
from threecxapi.resources.users import ListUserParameters
from threecxapi.components.parameters import ListParameters
from threecxapi.resources.users import UsersResource
from threecxapi.connection import ThreeCXApiConnection
from threecxapi.components.schemas.pbx import User
import threecxapi.exceptions as TCX_Exceptions


@pytest.fixture
def user_error():
    return {
        "error": {
            "code": "",
            "message": "SAMPLE_FIELD:\nWARNINGS.XAPI.SAMPLE_ERROR",
            "details": [{"code": "", "message": "WARNINGS.XAPI.SAMPLE_ERROR", "target": "SAMPLE_FIELD"}],
        }
    }


@pytest.fixture
def mock_response(user_error):
    mock_response = MagicMock(spec=requests.models.Response)
    mock_response.status_code = 418
    mock_response.json.return_value = user_error
    yield mock_response


@pytest.fixture
def http_error(mock_response):
    yield requests.HTTPError("An Error Occured", response=mock_response)


class TestListUserParameters:

    def test_inherits_from_parameters(self):
        assert issubclass(ListUserParameters, ListParameters)

    def test_valid_empty_parameters(self):
        test_list_user_parameters = ListUserParameters()
        assert isinstance(test_list_user_parameters, ListUserParameters)

    def test_valid_select(self):
        params = ListUserParameters(select=User.to_enum())
        assert isinstance(params, ListUserParameters)

    def test_invalid_select(self):
        select = ["INVALID_VALUE"]
        with pytest.raises(ValidationError):
            ListUserParameters(select=select)

    def test_valid_expand(self):
        expand = "test"
        params = ListUserParameters(expand=expand)
        assert isinstance(params, ListUserParameters)

    def test_invalid_expand(self):
        expand = 3
        with pytest.raises(ValidationError):
            ListUserParameters(expand=expand)

    def test_valid_top(self):
        test_params = ListUserParameters(top=1, skip=1)
        assert test_params.top == 1

    def test_invalid_top(self):
        with pytest.raises(ValidationError):
            test_params = ListUserParameters(top=-1)

        test_params = ListUserParameters(top=1)
        with pytest.raises(ValidationError):
            test_params.top = -1

    def test_valid_skip(self):
        test_params = ListUserParameters(skip=1)
        assert test_params.skip == 1

    def test_invalid_skip(self):
        with pytest.raises(ValidationError):
            test_params = ListUserParameters(skip=-1)

        test_params = ListUserParameters(skip=1)
        with pytest.raises(ValidationError):
            test_params.skip = -1


class TestUsersResource:
    @pytest.fixture
    def mock_connection(self):
        return MagicMock(spec=ThreeCXApiConnection)

    @pytest.fixture
    def mock_list_user_parameters(self):
        return MagicMock(spec=ListUserParameters)

    @pytest.fixture
    def users_resource(self, mock_connection):
        return UsersResource(api=mock_connection)

    @pytest.fixture
    def user(self):
        user = User(Id=123, FirstName="TestFirstName", LastName="TestLastName", Number="123")
        yield user

    @pytest.fixture
    def user2(self):
        user = User(Id=456, FirstName="TestFirstName2", LastName="TestLastName2", Number="456")
        yield user

    def test_endpoint(self, users_resource):
        assert users_resource.endpoint == "Users"

    def test_create_user_success(self, users_resource):
        user_dict = {"Id": 123, "FirstName": "TestFirstName", "LastName": "TestLastName", "Number": "123"}
        users_resource.create_user(user_dict)
        users_resource.api.post.assert_called_once_with(users_resource.endpoint, user_dict)

    def test_create_user_failure(self, users_resource, user, http_error):
        users_resource.api.post.side_effect = http_error
        user_dict = user.model_dump()

        with pytest.raises(UserCreateError) as context:
            users_resource.create_user(user_dict)
        assert context.value.args[0] == "Unable to create user with number 123."

    def test_list_user_with_single_result(self, mock_list_user_parameters, users_resource, user):
        api_response = {"value": [user.model_dump()]}
        users_resource.api.get.return_value = MagicMock(json=MagicMock(return_value=api_response))
        expected_user = User.model_construct(**user.model_dump())

        user_collection_response = users_resource.list_user(mock_list_user_parameters)
        users = user_collection_response.value

        assert isinstance(user_collection_response, UserCollectionResponse)
        assert len(users) == 1
        assert users[0].model_dump() == expected_user.model_dump()
        users_resource.api.get.assert_called_once_with("Users", mock_list_user_parameters)

    def test_list_user_with_multiple_results(self, mock_list_user_parameters, users_resource, user, user2):
        api_response = {"value": [user.model_dump(), user2.model_dump()]}
        users_resource.api.get.return_value = MagicMock(json=MagicMock(return_value=api_response))

        params = ListUserParameters()
        user_collection_response = users_resource.list_user(params)
        users = user_collection_response.value

        assert isinstance(user_collection_response, UserCollectionResponse)
        assert len(users) == 2
        assert users[1].Id == user2.Id
        assert users[1].FirstName == user2.FirstName
        assert users[1].LastName == user2.LastName

        # Asserting that the API was called with the correct parameters
        users_resource.api.get.assert_called_once_with("Users", params)

    def test_list_user_failure(self, users_resource, http_error):
        # Mocking the API response to simulate an error
        users_resource.api.get.side_effect = http_error

        # Calling the method under test
        params = ListUserParameters()
        with pytest.raises(UserListError):
            users_resource.list_user(params)

        # Asserting that the API was called with the correct parameters
        users_resource.api.get.assert_called_once_with("Users", params)

    def test_get_user_success(self, users_resource, user, mock_response):
        mock_response.json.return_value = user.model_dump()
        users_resource.api.get.return_value = mock_response

        params = ListUserParameters()
        returned_user = users_resource.get_user(user_id=user.Id, params=params)

        users_resource.api.get.assert_called_once_with(endpoint=f"Users({user.Id})", params=params)
        assert isinstance(user, User)
        assert returned_user.FirstName == user.FirstName
        assert returned_user.LastName == user.LastName

    def test_get_user_failure(self, users_resource, http_error):
        users_resource.api.get.side_effect = http_error

        params = ListUserParameters()
        with pytest.raises(UserGetError):
            users_resource.get_user(user_id=5000, params=params)

        users_resource.api.get.assert_called_once_with(endpoint="Users(5000)", params=params)

    def test_update_user_success(self, users_resource, user):
        user_dict = user.model_dump(
            exclude_unset=True,
            exclude_none=True,
            serialize_as_any=True,
            by_alias=True,
        )
        mock_user = MagicMock(wraps=user)
        mock_user.model_dump.return_value = user_dict
        mock_user.Id = user.Id

        users_resource.update_user(mock_user)

        mock_user.model_dump.assert_called_once_with(
            exclude_unset=True, exclude_none=True, serialize_as_any=True, by_alias=True
        )
        users_resource.api.patch.assert_called_once_with(endpoint=f"Users({user.Id})", data=user_dict)

    def test_update_user_failure(self, users_resource, user, http_error):
        users_resource.api.patch.side_effect = http_error
        with pytest.raises(UserUpdateError):
            users_resource.update_user(user)

    def test_delete_user(self, users_resource, user):
        users_resource.delete_user(user)
        users_resource.api.delete.assert_called_once_with(endpoint="Users", params=user.Id)

    def test_delete_user_failure(self, users_resource, user, http_error):
        users_resource.api.delete.side_effect = http_error
        with pytest.raises(UserDeleteError):
            users_resource.delete_user(user)

    @patch.object(UsersResource, "list_user")
    @patch("threecxapi.resources.users.ListUserParameters")
    def test_get_hotdesks_by_assigned_user_number(self, mock_params_class, mock_list_user, users_resource, user):
        expected_results = [user, user, user, user]
        mock_list_user.return_value = expected_results
        mock_params = MagicMock()
        mock_params_class.return_value = mock_params

        hotdesk_users = users_resource.get_hotdesks_by_assigned_user_number("123")

        mock_params_class.assert_called_once_with(filter="HotdeskingAssignment eq '123'")
        users_resource.list_user.assert_called_once_with(params=mock_params)
        assert hotdesk_users == expected_results

    @patch.object(UsersResource, "list_user")
    @patch("threecxapi.resources.users.ListUserParameters")
    def test_get_hotdesks_by_assigned_user_number_no_results(
        self, mock_params_class, mock_list_user, users_resource, user
    ):
        expected_results = []
        mock_list_user.return_value = expected_results
        mock_params = MagicMock()
        mock_params_class.return_value = mock_params

        hotdesk_users = users_resource.get_hotdesks_by_assigned_user_number("123")

        mock_params_class.assert_called_once_with(filter="HotdeskingAssignment eq '123'")
        users_resource.list_user.assert_called_once_with(params=mock_params)
        assert hotdesk_users is None

    @patch.object(UsersResource, "list_user")
    def test_get_hotdesks_by_assigned_user_number_failure(self, mock_list_user, users_resource, user, http_error):
        mock_list_user.side_effect = http_error

        with pytest.raises(UserHotdeskLookupError):
            users_resource.get_hotdesks_by_assigned_user_number("123")

    def test_clear_hotdesk_assignment(self, users_resource, user):
        users_resource.clear_hotdesk_assignment(user)

        users_resource.api.patch.assert_called_once_with(endpoint="Users(123)", data={"HotdeskingAssignment": ""})

    def test_clear_hotdesk_assignment_failure(self, users_resource, user, http_error):
        users_resource.api.patch.side_effect = http_error
        with pytest.raises(UserHotdeskLogoutError):
            users_resource.clear_hotdesk_assignment(user)

    @pytest.mark.parametrize("value", [True, False])
    def test_has_duplicated_email(self, value, mock_response, users_resource, user):
        response = {"@odata.context": "https://owensboro.my3cx.us:5001/xapi/v1/$metadata#Edm.Boolean", "value": value}
        users_resource.api.get.return_value = mock_response
        mock_response.json.return_value = response
        result = users_resource.has_duplicated_email(user)

        assert isinstance(result, HasDuplicatedEmailResponse)
        assert result.value == value

    def test_has_duplicated_email_failure(self, users_resource, user, http_error):
        users_resource.api.get.side_effect = http_error

        with pytest.raises(UserHasDuplicatedEmailError):
            users_resource.has_duplicated_email(user)

    def test_get_new_user(self):
        # Technically since there is no endpoint that returns a framework or default
        # setup for a new user, this is business logic and doesn't belong in this extension.
        # This will be removed later.
        pytest.skip()
