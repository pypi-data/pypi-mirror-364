from threecxapi.exceptions import APIError
from requests import HTTPError
from threecxapi.components.schemas.pbx import Group


class GroupCreateError(APIError):
    """Error raised when there is an issue creating a group."""

    def __init__(self, e: HTTPError, group: dict):
        group_number = group.get("Number", "N/A")
        error_message = f"Unable to create group with number {group_number}."
        super().__init__(e, error_message)


class GroupListError(APIError):
    """Error raised when there is an issue listing groups."""

    def __init__(self, e: HTTPError):
        super().__init__(e, "Unable to retrieve groups.")


class GroupGetError(APIError):
    """Error raised when there is an issue getting a group."""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to retrieve group with ID {group_id}."
        super().__init__(e, error_message)


class GroupUpdateError(APIError):
    """Error raised when there is an issue updating a group."""

    def __init__(self, e: HTTPError, group: Group):
        group_id = group.Id
        group_number = getattr(group, "Number", "N/A")
        error_message = f"Unable to update group with ID {group_id} and number {group_number}."
        super().__init__(e, error_message)


class GroupDeleteError(APIError):
    """Error raised when there is an issue deleting a group."""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to delete group with ID {group_id}."
        super().__init__(e, error_message)


class GroupHasDuplicatedEmailError(APIError):
    """Error raised when there is an issue determining if a group has a duplicated email."""

    def __init__(self, e: HTTPError, group_id: str):
        error_message = f"Unable to determine if group with ID {group_id} has a duplicated email."
        super().__init__(e, error_message)


class GroupGetRestrictionsError(APIError):
    """Error raised when there is an issue determining the group restrictions for a group."""

    def __init__(self, e: HTTPError, group_id: str):
        error_message = f"Unable to determine group restrictions for group with ID {group_id}"
        super().__init__(e, error_message)


class GroupDeleteCompanyByNumberError(APIError):
    """Error raised when there is an issue deleting a company by number"""

    def __init__(self, e: HTTPError, company_number: str):
        error_message = f"Unable to delete company by number {company_number}"
        super().__init__(e, error_message)


class GroupDeleteCompanyByIdError(APIError):
    """Error raised when there is an issue deleting a company by ID"""

    def __init__(self, e: HTTPError, company_id: int):
        error_message = f"Unable to delete company by ID {company_id}"
        super().__init__(e, error_message)


class GroupListMembersError(APIError):
    """Error raised when there is an issue fetching members of a group"""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to fetch members of group ID {group_id}"
        super().__init__(e, error_message)


class GroupListRightsError(APIError):
    """Error raised when there is an issue fetching rights of a group"""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to fetch rights of group ID {group_id}"
        super().__init__(e, error_message)


class GroupReplaceGroupLicenseKey(APIError):
    """Error raised when there is an issue replacing a group license key"""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to replace group license key for group ID {group_id}"
        super().__init__(e, error_message)


class GroupLinkGroupPartnerError(APIError):
    """Error raised when there is an issue linking a group partner"""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to replace group license key for group ID {group_id}"
        super().__init__(e, error_message)


class GroupUnlinkGroupPartnerError(APIError):
    """Error raised when there is an issue unlinking a group partner"""

    def __init__(self, e: HTTPError, group_id: int):
        error_message = f"Unable to replace group license key for group ID {group_id}"
        super().__init__(e, error_message)
