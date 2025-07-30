import requests

from pydantic import TypeAdapter

from threecxapi.components.responses.pbx import GroupCollectionResponse, UserGroupCollectionResponse
from threecxapi.resources.api_resource import APIResource
from threecxapi.components.schemas.pbx import Group, UserGroup, Rights
from threecxapi.components.parameters import (
    ExpandParameters,
    ListParameters,
    OrderbyParameters,
    SelectParameters,
)

from threecxapi.resources.exceptions.groups_exceptions import (
    GroupCreateError,
    GroupLinkGroupPartnerError,
    GroupListError,
    GroupDeleteError,
    GroupGetError,
    GroupReplaceGroupLicenseKey,
    GroupUnlinkGroupPartnerError,
    GroupUpdateError,
    GroupGetRestrictionsError,
    GroupDeleteCompanyByNumberError,
    GroupDeleteCompanyByIdError,
    GroupListMembersError,
    GroupListRightsError,
)


class ListGroupParameters(ListParameters, OrderbyParameters, SelectParameters[Group.to_enum()], ExpandParameters): ...


class GetGroupParameters(SelectParameters[Group.to_enum()], ExpandParameters): ...


class ListUserGroupParameters(
    ListParameters, OrderbyParameters, SelectParameters[UserGroup.to_enum()], ExpandParameters
):
    """Used to fetch members of a group."""

    ...


class ListGroupRightsParameters(
    ListParameters, OrderbyParameters, SelectParameters[Rights.to_enum()], ExpandParameters
): ...


class GroupsResource(APIResource):
    endpoint: str = "Groups"

    def create_group(self, group: dict):
        """Add new entity to Groups"""
        try:
            self.api.post(self.get_endpoint(), group)
        except requests.HTTPError as e:
            raise GroupCreateError(e, group)

    def list_group(self, params: ListGroupParameters) -> GroupCollectionResponse:
        """Get entities from Groups"""
        try:
            response = self.api.get(self.get_endpoint(), params)
            return TypeAdapter(GroupCollectionResponse).validate_python(response.json())
        except requests.HTTPError as e:
            raise GroupListError(e)

    def get_group(self, group_id: int, params: GetGroupParameters) -> Group:
        try:
            response = self.api.get(endpoint=self.get_endpoint(group_id), params=params)
            return TypeAdapter(Group).validate_python(response.json())
        except requests.HTTPError as e:
            raise GroupGetError(e, group_id)

    def update_group(self, group: Group):
        """Update a group entity"""
        try:
            group_dict = group.model_dump(
                exclude_unset=True,
                exclude_none=True,
                serialize_as_any=True,
                by_alias=True,
            )
            self.api.patch(endpoint=self.get_endpoint(group.Id), data=group_dict)
        except requests.HTTPError as e:
            raise GroupUpdateError(e, group)

    def delete_group(self, group: Group):
        try:
            self.api.delete(endpoint=self.get_endpoint(), params=group.Id)
        except requests.HTTPError as e:
            raise GroupDeleteError(e, group.Id)

    # Group Special Actions
    def get_restrictions(self, group: Group):
        try:
            self.api.get(endpoint=self.get_endpoint(group.Id, "Pbx.GetRestrictions()"))
        except requests.HTTPError as e:
            raise GroupGetRestrictionsError(e, group.Id)

    def get_group_restrictions(self, group: Group):
        try:
            self.api.get(endpoint=self.get_endpoint(group.Id, "Pbx.GetRestrictions()"))
        except requests.HTTPError as e:
            raise GroupGetRestrictionsError(e, group.Id)

    def delete_company_by_number(self, number: str):
        try:
            self.api.post(endpoint=self.get_endpoint(None, "Pbx.DeleteCompanyByNumber"), data={"number": number})
        except requests.HTTPError as e:
            raise GroupDeleteCompanyByNumberError(e, number)

    def delete_company_by_id(self, id: int):
        try:
            self.api.post(endpoint=self.get_endpoint(None, "Pbx.DeleteCompanyById"), data={"id": id})
        except requests.HTTPError as e:
            raise GroupDeleteCompanyByIdError(e, id)

    def list_members(self, group: Group, params: ListUserGroupParameters) -> UserGroupCollectionResponse:
        """Get members of a group"""
        try:
            response = self.api.get(self.get_endpoint(group.Id, "Members"), params)
            return TypeAdapter(list[UserGroupCollectionResponse]).validate_python(response.json())
        except requests.HTTPError as e:
            raise GroupListMembersError(e)

    def list_rights(self, group: Group, params: ListGroupRightsParameters) -> UserGroupCollectionResponse:
        """Get rights of a group"""
        try:
            response = self.api.get(self.get_endpoint(group.Id, "Members"), params)
            return TypeAdapter(list[UserGroupCollectionResponse]).validate_python(response.json())
        except requests.HTTPError as e:
            raise GroupListRightsError(e)

    def replace_group_license_key(self, license_key: str, group: Group):
        try:
            self.api.post(
                endpoint=self.get_endpoint(None, "Pbx.ReplaceGroupLicenseKey"),
                data={"licenseKey": license_key, "groupId": group.Id},
            )
        except requests.HTTPError as e:
            raise GroupReplaceGroupLicenseKey(e, group.Id)

    def link_group_partner(self, reseller_id: str, group: Group):
        try:
            self.api.post(
                endpoint=self.get_endpoint(None, "Pbx.LinkGroupPartner"),
                data={"resellerId": reseller_id, "groupId": group.Id},
            )
        except requests.HTTPError as e:
            raise GroupLinkGroupPartnerError(e, group.Id)

    def unlink_group_partner(self):
        try:
            self.api.post(
                endpoint=self.get_endpoint(None, "Pbx.UnlinkGroupPartner"),
                data={},
            )
        except requests.HTTPError as e:
            raise GroupUnlinkGroupPartnerError(e)

    # Custom Helpers
    def get_group_defaults(self):
        return {}

    def get_default_group(self) -> Group | None:
        response = self.list_group(params=ListGroupParameters(filter="IsDefault eq true"))
        return response.value[0] if response.value else None
