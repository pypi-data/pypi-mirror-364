from typing import Any
from threecxapi.components.schema import Schema
from pydantic import Field


class StringCollectionResponse(Schema):
    value: list[str]


class ReferenceUpdate(Schema):
    id: str = Field(None, alias="@odata.id")
    type: str = Field(None, alias="@odata.type")


class ReferenceCreate(Schema):
    id: str = Field(None, alias="@odata.id")
    additionalProperties: Any


class BaseCollectionPaginationCountResponse(Schema):
    count: str = Field(None, alias="@odata.count")


class ReplaceMyGroupLicenseKeyRequestBody(Schema):
    licenseKey: str


class LinkMyGroupPartnerRequestBody(Schema):
    resellerId: str


class Enable2FARequestBody(Schema):
    enable: bool = False
    code: str


class RegenerateRequestBody(Schema):
    SipAuth: bool = False
    WebclientPassword: bool = False
    VoicemailPIN: bool = False
    DeskphonePassword: bool = False
    SendWelcomeEmail: bool = False
    ConfigurationLink: bool = False
    RpsKey: bool = False


class MakeCallUserRecordGreetingRequestBody(Schema):
    dn: str
    filename: str


class SetMonitorStatusRequestBody(Schema):
    days: int
