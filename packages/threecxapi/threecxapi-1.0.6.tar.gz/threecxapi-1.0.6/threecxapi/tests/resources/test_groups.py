import requests
import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock
from threecxapi.components.responses.other import HasDuplicatedEmailResponse
from threecxapi.components.responses.pbx import GroupCollectionResponse
from threecxapi.resources.exceptions.groups_exceptions import (
    GroupCreateError,
    GroupListError,
    GroupDeleteError,
    GroupGetError,
    GroupUpdateError,
)
from threecxapi.resources.groups import ListGroupParameters
from threecxapi.components.parameters import ListParameters
from threecxapi.resources.groups import GroupsResource
from threecxapi.connection import ThreeCXApiConnection
from threecxapi.components.schemas.pbx import Group


@pytest.fixture
def mock_response(group_error):
    mock_response = MagicMock(spec=requests.models.Response)
    mock_response.status_code = 418
    mock_response.json.return_value = group_error
    yield mock_response


@pytest.fixture
def http_error(mock_response):
    yield requests.HTTPError("An Error Occured", response=mock_response)


class TestListGroupParameters:

    def test_inherits_from_parameters(self):
        assert issubclass(ListGroupParameters, ListParameters)

    def test_valid_empty_parameters(self):
        test_list_group_parameters = ListGroupParameters()
        assert isinstance(test_list_group_parameters, ListGroupParameters)

    def test_valid_select(self):
        params = ListGroupParameters(select=Group.to_enum())
        assert isinstance(params, ListGroupParameters)

    def test_invalid_select(self):
        select = ["INVALID_VALUE"]
        with pytest.raises(ValidationError):
            ListGroupParameters(select=select)

    def test_valid_expand(self):
        expand = "test"
        params = ListGroupParameters(expand=expand)
        assert isinstance(params, ListGroupParameters)

    def test_invalid_expand(self):
        expand = 3
        with pytest.raises(ValidationError):
            ListGroupParameters(expand=expand)

    def test_valid_top(self):
        test_params = ListGroupParameters(top=1, skip=1)
        assert test_params.top == 1

    def test_invalid_top(self):
        with pytest.raises(ValidationError):
            test_params = ListGroupParameters(top=-1)

        test_params = ListGroupParameters(top=1)
        with pytest.raises(ValidationError):
            test_params.top = -1

    def test_valid_skip(self):
        test_params = ListGroupParameters(skip=1)
        assert test_params.skip == 1

    def test_invalid_skip(self):
        with pytest.raises(ValidationError):
            test_params = ListGroupParameters(skip=-1)

        test_params = ListGroupParameters(skip=1)
        with pytest.raises(ValidationError):
            test_params.skip = -1


class TestGroupsResource:
    @pytest.fixture
    def mock_connection(self):
        return MagicMock(spec=ThreeCXApiConnection)

    @pytest.fixture
    def mock_list_group_parameters(self):
        return MagicMock(spec=ListGroupParameters)

    @pytest.fixture
    def groups_resource(self, mock_connection):
        return GroupsResource(api=mock_connection)

    @pytest.fixture
    def group(self):
        group = Group(Id=123, Name="TestGroup", Number="123")
        yield group

    @pytest.fixture
    def group2(self):
        group = Group(Id=456, Name="TestGroup2", Number="456")
        yield group

    def test_endpoint(self, groups_resource):
        assert groups_resource.endpoint == "Groups"

    def test_create_group_success(self, groups_resource):
        group_dict = {"Id": 123, "FirstName": "TestFirstName", "LastName": "TestLastName", "Number": "123"}
        groups_resource.create_group(group_dict)
        groups_resource.api.post.assert_called_once_with(groups_resource.endpoint, group_dict)

    def test_create_group_failure(self, groups_resource, group, http_error):
        groups_resource.api.post.side_effect = http_error
        group_dict = group.model_dump()

        with pytest.raises(GroupCreateError) as context:
            groups_resource.create_group(group_dict)
        assert context.value.args[0] == "Unable to create group with number 123."

    def test_list_group_with_single_result(self, mock_list_group_parameters, groups_resource, group):
        api_response = {"value": [group.model_dump()]}
        groups_resource.api.get.return_value = MagicMock(json=MagicMock(return_value=api_response))
        expected_group = Group.model_construct(**group.model_dump())

        group_collection_response = groups_resource.list_group(mock_list_group_parameters)
        groups = group_collection_response.value

        assert isinstance(group_collection_response, GroupCollectionResponse)
        assert len(groups) == 1
        assert groups[0].model_dump() == expected_group.model_dump()
        groups_resource.api.get.assert_called_once_with("Groups", mock_list_group_parameters)

    def test_list_group_with_multiple_results(self, mock_list_group_parameters, groups_resource, group, group2):
        api_response = {"value": [group.model_dump(), group2.model_dump()]}
        groups_resource.api.get.return_value = MagicMock(json=MagicMock(return_value=api_response))

        params = ListGroupParameters()
        group_collection_response = groups_resource.list_group(params)
        groups = group_collection_response.value

        assert isinstance(group_collection_response, GroupCollectionResponse)
        assert len(groups) == 2
        assert groups[1].Id == group2.Id
        assert groups[1].Name == group2.Name
        assert groups[1].Number == group2.Number

        # Asserting that the API was called with the correct parameters
        groups_resource.api.get.assert_called_once_with("Groups", params)

    def test_list_group_failure(self, groups_resource, http_error):
        # Mocking the API response to simulate an error
        groups_resource.api.get.side_effect = http_error

        # Calling the method under test
        params = ListGroupParameters()
        with pytest.raises(GroupListError):
            groups_resource.list_group(params)

        # Asserting that the API was called with the correct parameters
        groups_resource.api.get.assert_called_once_with("Groups", params)

    def test_get_group_success(self, groups_resource, group, mock_response):
        mock_response.json.return_value = group.model_dump()
        groups_resource.api.get.return_value = mock_response

        params = ListGroupParameters()
        returned_group = groups_resource.get_group(group_id=group.Id, params=params)

        groups_resource.api.get.assert_called_once_with(endpoint=f"Groups({group.Id})", params=params)
        assert isinstance(group, Group)
        assert returned_group.Id == group.Id
        assert returned_group.Name == group.Name
        assert returned_group.Number == group.Number

    def test_get_group_failure(self, groups_resource, http_error):
        groups_resource.api.get.side_effect = http_error

        params = ListGroupParameters()
        with pytest.raises(GroupGetError):
            groups_resource.get_group(group_id=5000, params=params)

        groups_resource.api.get.assert_called_once_with(endpoint="Groups(5000)", params=params)

    def test_update_group_success(self, groups_resource, group):
        group_dict = group.model_dump(
            exclude_unset=True,
            exclude_none=True,
            serialize_as_any=True,
            by_alias=True,
        )
        mock_group = MagicMock(wraps=group)
        mock_group.model_dump.return_value = group_dict
        mock_group.Id = group.Id

        groups_resource.update_group(mock_group)

        mock_group.model_dump.assert_called_once_with(
            exclude_unset=True, exclude_none=True, serialize_as_any=True, by_alias=True
        )
        groups_resource.api.patch.assert_called_once_with(endpoint=f"Groups({group.Id})", data=group_dict)

    def test_update_group_failure(self, groups_resource, group, http_error):
        groups_resource.api.patch.side_effect = http_error
        with pytest.raises(GroupUpdateError):
            groups_resource.update_group(group)

    def test_delete_group(self, groups_resource, group):
        groups_resource.delete_group(group)
        groups_resource.api.delete.assert_called_once_with(endpoint="Groups", params=group.Id)

    def test_delete_group_failure(self, groups_resource, group, http_error):
        groups_resource.api.delete.side_effect = http_error
        with pytest.raises(GroupDeleteError):
            groups_resource.delete_group(group)

    def test_get_new_group(self):
        # Technically since there is no endpoint that returns a framework or default
        # setup for a new group, this is business logic and doesn't belong in this extension.
        # This will be removed later.
        pytest.skip()

    @patch("threecxapi.resources.groups.GroupsResource.list_group")
    def test_get_default_group(self, mock_list_group, groups_resource):
        mock_group = MagicMock(spec=Group)
        mock_group_collection_response = MagicMock(spec=GroupCollectionResponse)
        mock_group_collection_response.value = [mock_group]
        mock_list_group.return_value = mock_group_collection_response

        response = groups_resource.get_default_group()

        assert response == mock_group_collection_response.value[0]
