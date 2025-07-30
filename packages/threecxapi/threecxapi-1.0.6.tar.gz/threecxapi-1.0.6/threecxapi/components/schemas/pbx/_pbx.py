from decimal import Decimal
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import Field
from threecxapi.components.schema import Schema
from threecxapi.components.schemas import BaseCollectionPaginationCountResponse
from threecxapi.components.schemas.pbx.enums import *


class AbandonedChatsStatistics(Schema):
    ChatId: int = Field(default_factory=list)
    DateOfRequest: datetime = Field(default_factory=list)
    ParticipantEmail: str = Field(default_factory=list)
    ParticipantMessage: str = Field(default_factory=list)
    ParticipantName: Optional[str] = Field(default=None)
    ParticipantNumber: str = Field(default_factory=list)
    QueueDisplayName: Optional[str] = Field(default=None)
    QueueNo: str = Field(default_factory=list)
    ReasonForAbandoned: Optional[str] = Field(default=None)
    ReasonForDealtWith: Optional[str] = Field(default=None)
    Source: str = Field(default_factory=list)


class AbandonedQueueCalls(Schema):
    CallerId: Optional[str] = Field(default=None)
    CallHistoryId: Optional[str] = Field(default=None)
    CallTime: Optional[datetime] = Field(default=None)
    CallTimeForCsv: Optional[datetime] = Field(default=None)
    ExtensionDisplayName: Optional[str] = Field(default=None)
    ExtensionDn: Optional[str] = Field(default=None)
    IsLoggedIn: Optional[bool] = Field(default=None)
    PollingAttempts: Optional[int] = Field(default=None)
    QueueDisplayName: Optional[str] = Field(default=None)
    QueueDn: str = Field(default_factory=list)
    WaitTime: Optional[str] = Field(default=None)


class ActiveCall(Schema):
    Callee: Optional[str] = Field(default=None)
    Caller: Optional[str] = Field(default=None)
    EstablishedAt: Optional[datetime] = Field(default=None)
    Id: int = Field(default_factory=list)
    LastChangeStatus: Optional[datetime] = Field(default=None)
    ServerNow: Optional[datetime] = Field(default=None)
    Status: Optional[str] = Field(default=None)


class ActivityLogEvent(Schema):
    Index: int = Field(default_factory=list)
    Message: Optional[str] = Field(default=None)
    TimeStamp: Optional[datetime] = Field(default=None)


class AgentLoginHistory(Schema):
    Agent: str = Field(default_factory=list)
    AgentNo: str = Field(default_factory=list)
    Day: Optional[datetime] = Field(default=None)
    LoggedInDayInterval: Optional[str] = Field(default=None)
    loggedInDt: Optional[datetime] = Field(default=None)
    LoggedInInterval: Optional[str] = Field(default=None)
    LoggedInTotalInterval: Optional[str] = Field(default=None)
    LoggedOutDt: Optional[datetime] = Field(default=None)
    QueueNo: str = Field(default_factory=list)
    TalkingDayInterval: Optional[str] = Field(default=None)
    TalkingInterval: Optional[str] = Field(default=None)
    TalkingTotalInterval: Optional[str] = Field(default=None)


class AgentsInQueueStatistics(Schema):
    AnsweredCount: Optional[int] = Field(default=None)
    AnsweredPercent: Optional[int] = Field(default=None)
    AnsweredPerHourCount: Optional[int] = Field(default=None)
    AvgRingTime: Optional[str] = Field(default=None)
    AvgTalkTime: Optional[str] = Field(default=None)
    Dn: str = Field(default_factory=list)
    DnDisplayName: Optional[str] = Field(default=None)
    LoggedInTime: Optional[str] = Field(default=None)
    LostCount: Optional[int] = Field(default=None)
    Queue: Optional[str] = Field(default=None)
    QueueDisplayName: Optional[str] = Field(default=None)
    RingTime: Optional[str] = Field(default=None)
    TalkTime: Optional[str] = Field(default=None)


class AntiHackingSettings(Schema):
    HackAuthRequests: Optional[int] = Field(default=None)
    HackBarrierAmber: Optional[int] = Field(default=None)
    HackBarrierGreen: Optional[int] = Field(default=None)
    HackBarrierRed: Optional[int] = Field(default=None)
    HackBlacklistDuration: Optional[int] = Field(default=None)
    HackChallengeRequests: Optional[int] = Field(default=None)
    MaxRequestPerPeriod: Optional[int] = Field(default=None)
    SecurityDefenseProgram: Optional[bool] = Field(default=None)
    ThrottlePeriodLength: Optional[int] = Field(default=None)


class ArchiveSubsystem(Schema):
    Archiving: Optional[bool] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    Folder: Optional[str] = Field(default=None)
    ScheduleDays: Optional[int] = Field(default=None)


class AuditLog(Schema):
    Action: Optional[int] = Field(default=None)
    Id: int = Field(default_factory=list)
    Ip: Optional[str] = Field(default=None)
    NewData: Optional[str] = Field(default=None)
    ObjectName: Optional[str] = Field(default=None)
    ObjectType: Optional[int] = Field(default=None)
    PrevData: Optional[str] = Field(default=None)
    Source: Optional[int] = Field(default=None)
    Timestamp: Optional[datetime] = Field(default=None)
    UserName: Optional[str] = Field(default=None)


class AutoSchedulerSettings(Schema):
    Enabled: Optional[bool] = Field(default=None)
    ProfileAvailable: Optional[str] = Field(default=None)
    ProfileAway: Optional[str] = Field(default=None)
    ProfileDND: Optional[str] = Field(default=None)


class BackupExtras(Schema):
    Footprint: Optional[int] = Field(default=None)
    IsEncrypted: Optional[bool] = Field(default=None)
    Version: str = Field(default_factory=list)


class BackupFailoverSettings(Schema):
    Condition: Optional[FailoverCondition] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    Interval: Optional[int] = Field(default=None)
    Mode: Optional[FailoverMode] = Field(default=None)
    PostStartScript: Optional[str] = Field(default=None)
    PreStartScript: Optional[str] = Field(default=None)
    RemoteServer: Optional[str] = Field(default=None)
    TestSIPServer: Optional[bool] = Field(default=None)
    TestTunnel: Optional[bool] = Field(default=None)
    TestWebServer: Optional[bool] = Field(default=None)


class BackupSchedule(Schema):
    Day: Optional[DayOfWeek] = Field(default=None)
    RepeatHours: Optional[int] = Field(default=None)
    schedule_type: Optional[ScheduleType] = Field(default=None, alias="ScheduleType")
    Time: Optional[str] = Field(default=None)


class Backups(Schema):
    CreationTime: Optional[datetime] = Field(default=None)
    DownloadLink: str = Field(default_factory=list)
    FileName: str = Field(default_factory=list)
    Size: Optional[int] = Field(default=None)


class BaseCollectionPaginationCountResponse(Schema):
    count: Optional[int] = Field(default=None, alias="@odata.count")


class AbandonedChatsStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[AbandonedChatsStatistics] = Field(default_factory=list)


class AbandonedQueueCallsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[AbandonedQueueCalls] = Field(default_factory=list)


class ActiveCallCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ActiveCall] = Field(default_factory=list)


class ActivityLogEventCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ActivityLogEvent] = Field(default_factory=list)


class AgentLoginHistoryCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[AgentLoginHistory] = Field(default_factory=list)


class AgentsInQueueStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[AgentsInQueueStatistics] = Field(default_factory=list)


class AuditLogCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[AuditLog] = Field(default_factory=list)


class BackupsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Backups] = Field(default_factory=list)


class BlackListNumber(Schema):
    CallerId: str = Field(default_factory=list)
    Description: Optional[str] = Field(default=None)
    Id: str = Field(default_factory=list)


class BlackListNumberCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[BlackListNumber] = Field(default_factory=list)


class BlocklistAddr(Schema):
    added_by: Optional[AddedBy] = Field(default=None, alias="AddedBy")
    block_type: Optional[BlockType] = Field(default=None, alias="BlockType")
    Description: Optional[str] = Field(default=None)
    ExpiresAt: Optional[datetime] = Field(default=None)
    Id: int = Field(default_factory=list)
    IPAddrMask: Optional[str] = Field(default=None)


class BlocklistAddrCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[BlocklistAddr] = Field(default_factory=list)


class BreachesSla(Schema):
    CallerId: str = Field(default_factory=list)
    CallTime: datetime = Field(default_factory=list)
    Queue: str = Field(default_factory=list)
    QueueDnNumber: Optional[str] = Field(default=None)
    WaitingTime: Optional[str] = Field(default=None)


class BreachesSlaCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[BreachesSla] = Field(default_factory=list)


class CDRSettingsField(Schema):
    Length: Optional[int] = Field(default=None)
    Name: Optional[str] = Field(default=None)


class CDRSettings(Schema):
    Enabled: Optional[bool] = Field(default=None)
    EnabledFields: list[CDRSettingsField] = Field(default_factory=list)
    LogSize: Optional[int] = Field(default=None)
    LogType: Optional[TypeOfCDRLog] = Field(default=None)
    PossibleFields: list[str] = Field(default_factory=list)
    RemoveCommaDelimiters: Optional[bool] = Field(default=None)
    SocketIpAddress: Optional[str] = Field(default=None)
    SocketPort: Optional[int] = Field(default=None)


class CDRSettingsFieldCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CDRSettingsField] = Field(default_factory=list)


class CIDFormatting(Schema):
    ReplacePattern: Optional[str] = Field(default=None)
    SourcePattern: Optional[str] = Field(default=None)


class CIDFormattingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CIDFormatting] = Field(default_factory=list)


class CallCostByExtensionGroup(Schema):
    BillingCost: Optional[Decimal] = Field(default=None)
    CallType: Optional[str] = Field(default=None)
    DstDn: Optional[str] = Field(default=None)
    DstDnClass: Optional[int] = Field(default=None)
    GroupName: Optional[str] = Field(default=None)
    IsAnswered: Optional[bool] = Field(default=None)
    RingingDur: Optional[str] = Field(default=None)
    SegId: str = Field(default_factory=list)
    SrcDisplayName: Optional[str] = Field(default=None)
    SrcDn: Optional[str] = Field(default=None)
    StartTime: Optional[datetime] = Field(default=None)
    TalkingDur: Optional[str] = Field(default=None)


class CallCostByExtensionGroupCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallCostByExtensionGroup] = Field(default_factory=list)


class CallCostSettings(Schema):
    CountryName: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    Invalid: Optional[bool] = Field(default=None)
    Prefix: Optional[str] = Field(default=None)
    Rate: Optional[float | str | ReferenceNumeric] = Field(default=None)
    ReadOnly: Optional[bool] = Field(default=None)


class CallCostSettingsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallCostSettings] = Field(default_factory=list)


class CallDistribution(Schema):
    DateTimeInterval: datetime = Field(default_factory=list)
    IncomingCount: int = Field(default_factory=list)
    OutgoingCount: int = Field(default_factory=list)


class CallDistributionCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallDistribution] = Field(default_factory=list)


class CallFlowScript(Schema):
    Description: Optional[str] = Field(default=None)
    Help: Optional[str] = Field(default=None)
    Id: str = Field(default_factory=list)
    Versions: list[str] = Field(default_factory=list)


class CallFlowScriptCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallFlowScript] = Field(default_factory=list)


class CallHistoryView(Schema):
    CallAnswered: Optional[bool] = Field(default=None)
    CallTime: str = Field(default_factory=list)
    DstCallerNumber: Optional[str] = Field(default=None)
    DstDisplayName: Optional[str] = Field(default=None)
    DstDn: Optional[str] = Field(default=None)
    DstDnType: int = Field(default_factory=list)
    DstExtendedDisplayName: Optional[str] = Field(default=None)
    DstExternal: bool = Field(default_factory=list)
    DstId: int = Field(default_factory=list)
    DstInternal: bool = Field(default_factory=list)
    DstParticipantId: int = Field(default_factory=list)
    DstRecId: Optional[int] = Field(default=None)
    SegmentActionId: int = Field(default_factory=list)
    SegmentEndTime: datetime = Field(default_factory=list)
    SegmentId: int = Field(default_factory=list)
    SegmentStartTime: datetime = Field(default_factory=list)
    SegmentType: int = Field(default_factory=list)
    SrcCallerNumber: Optional[str] = Field(default=None)
    SrcDisplayName: Optional[str] = Field(default=None)
    SrcDn: Optional[str] = Field(default=None)
    SrcDnType: int = Field(default_factory=list)
    SrcExtendedDisplayName: Optional[str] = Field(default=None)
    SrcExternal: bool = Field(default_factory=list)
    SrcId: int = Field(default_factory=list)
    SrcInternal: bool = Field(default_factory=list)
    SrcParticipantId: int = Field(default_factory=list)
    SrcRecId: Optional[int] = Field(default=None)


class CallHistoryViewCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallHistoryView] = Field(default_factory=list)


class CallLogData(Schema):
    ActionDnCallerId: Optional[str] = Field(default=None)
    ActionDnDisplayName: Optional[str] = Field(default=None)
    actionDnDn: Optional[str] = Field(default=None)
    ActionDnType: Optional[int] = Field(default=None)
    ActionType: Optional[int] = Field(default=None)
    Answered: Optional[bool] = Field(default=None)
    CallCost: Optional[Decimal] = Field(default=None)
    CallHistoryId: Optional[str] = Field(default=None)
    CallId: int = Field(default_factory=list)
    CallType: Optional[str] = Field(default=None)
    CdrId: str = Field(default_factory=list)
    DestinationCallerId: Optional[str] = Field(default=None)
    DestinationDisplayName: Optional[str] = Field(default=None)
    DestinationDn: Optional[str] = Field(default=None)
    destination_type: Optional[int] = Field(default=None, alias="DestinationType")
    Direction: Optional[str] = Field(default=None)
    DstRecId: Optional[int] = Field(default=None)
    Indent: Optional[int] = Field(default=None)
    MainCallHistoryId: Optional[str] = Field(default=None)
    QualityReport: Optional[bool] = Field(default=None)
    Reason: Optional[str] = Field(default=None)
    RecordingUrl: Optional[str] = Field(default=None)
    RingingDuration: Optional[str] = Field(default=None)
    SegmentId: Optional[int] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)
    SourceCallerId: Optional[str] = Field(default=None)
    SourceDisplayName: Optional[str] = Field(default=None)
    SourceDn: Optional[str] = Field(default=None)
    SourceType: Optional[int] = Field(default=None)
    SrcRecId: Optional[int] = Field(default=None)
    StartTime: Optional[datetime] = Field(default=None)
    Status: Optional[str] = Field(default=None)
    SubrowDescNumber: Optional[int] = Field(default=None)
    Summary: Optional[str] = Field(default=None)
    TalkingDuration: Optional[str] = Field(default=None)
    Transcription: Optional[str] = Field(default=None)


class CallLogDataCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallLogData] = Field(default_factory=list)


class CallParkingSettings(Schema):
    AutoPickupEnabled: Optional[bool] = Field(default=None)
    AutoPickupForwardDN: Optional[str] = Field(default=None)
    AutoPickupForwardExternalNumber: Optional[str] = Field(default=None)
    AutoPickupForwardType: Optional[TypeOfAutoPickupForward] = Field(default=None)
    AutoPickupTimeout: Optional[int] = Field(default=None)
    MaximumParkedCalls: Optional[int] = Field(default=None)
    MusicOnHold: Optional[str] = Field(default=None)


class CallParticipant(Schema):
    CallId: int = Field(default_factory=list)
    DeviceId: str = Field(default_factory=list)
    DirectControl: bool = Field(default_factory=list)
    DN: str = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    LegId: int = Field(default_factory=list)
    PartyCallerId: str = Field(default_factory=list)
    PartyCallerName: str = Field(default_factory=list)
    PartyDn: str = Field(default_factory=list)
    PartyDnType: str = Field(default_factory=list)
    Status: str = Field(default_factory=list)


class CallControlResultResponse(Schema):
    FinalStatus: str = Field(default_factory=list)
    Reason: str = Field(default_factory=list)
    ReasonText: str = Field(default_factory=list)
    Result: Optional[CallParticipant] = Field(default=None)
    VttId: Optional[str] = Field(default=None)


class CallTypeInfo(Schema):
    DigitsLength: Optional[str] = Field(default=None)
    Prefix: Optional[str] = Field(default=None)


class CallTypesSettings(Schema):
    International: Optional[CallTypeInfo] = Field(default=None)
    Local: Optional[CallTypeInfo] = Field(default=None)
    Mobile: Optional[CallTypeInfo] = Field(default=None)
    National: Optional[CallTypeInfo] = Field(default=None)


class CategoryUpdate(Schema):
    Category: Optional[str] = Field(default=None)
    Count: int = Field(default_factory=list)


class CategoryUpdateCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CategoryUpdate] = Field(default_factory=list)


class ChatHistoryView(Schema):
    ChatName: Optional[str] = Field(default=None)
    ConversationId: int = Field(default_factory=list)
    FromName: Optional[str] = Field(default=None)
    FromNo: Optional[str] = Field(default=None)
    IsExternal: bool = Field(default_factory=list)
    Message: Optional[str] = Field(default=None)
    ParticipantEmail: Optional[str] = Field(default=None)
    ParticipantIp: Optional[str] = Field(default=None)
    ParticipantPhone: Optional[str] = Field(default=None)
    ParticipantsGroupsArray: list[str] = Field(default_factory=list)
    ProviderName: Optional[str] = Field(default=None)
    ProviderType: Optional[ChatType] = Field(default=None)
    QueueNumber: Optional[str] = Field(default=None)
    Source: Optional[str] = Field(default=None)
    TimeSent: datetime = Field(default_factory=list)


class ChatHistoryViewCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ChatHistoryView] = Field(default_factory=list)


class ChatLinkNameValidation(Schema):
    FriendlyName: str = Field(default_factory=list)
    Pair: str = Field(default_factory=list)


class ChatLogSettings(Schema):
    AutoClearMonths: Optional[int] = Field(default=None)
    AutoCloseDays: Optional[int] = Field(default=None)
    RemoteStorageEnabled: Optional[bool] = Field(default=None)


class ChatMessagesHistoryView(Schema):
    ConversationId: int = Field(default_factory=list)
    IsExternal: bool = Field(default_factory=list)
    Message: Optional[str] = Field(default=None)
    MessageId: int = Field(default_factory=list)
    ParticipantsGroupsArray: list[str] = Field(default_factory=list)
    QueueNumber: Optional[str] = Field(default=None)
    Recipients: Optional[str] = Field(default=None)
    SenderParticipantEmail: Optional[str] = Field(default=None)
    SenderParticipantIp: Optional[str] = Field(default=None)
    SenderParticipantName: Optional[str] = Field(default=None)
    SenderParticipantNo: Optional[str] = Field(default=None)
    SenderParticipantPbx: Optional[str] = Field(default=None)
    SenderParticipantPhone: Optional[str] = Field(default=None)
    TimeSent: datetime = Field(default_factory=list)


class ChatMessagesHistoryViewCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ChatMessagesHistoryView] = Field(default_factory=list)


class Choice(Schema):
    Key: str = Field(default_factory=list)
    Value: str = Field(default_factory=list)


class ChoiceCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Choice] = Field(default_factory=list)


class Codec(Schema):
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    RfcName: Optional[str] = Field(default=None)


class CodecCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Codec] = Field(default_factory=list)


class CodecsSettings(Schema):
    ExternalCodecList: list[str] = Field(default_factory=list)
    LocalCodecList: list[str] = Field(default_factory=list)


class ConcealedDataFile(Schema):
    Concealed: Optional[bool] = Field(default=None)
    Contents: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)


class ConcealedPassword(Schema):
    Concealed: Optional[bool] = Field(default=None)
    Value: Optional[str] = Field(default=None)


class BackupContents(Schema):
    CallHistory: Optional[bool] = Field(default=None)
    DisableBackupCompression: Optional[bool] = Field(default=None)
    EncryptBackup: Optional[bool] = Field(default=None)
    EncryptBackupPassword: Optional[ConcealedPassword] = Field(default=None)
    FQDN: Optional[bool] = Field(default=None)
    License: Optional[bool] = Field(default=None)
    PhoneProvisioning: Optional[bool] = Field(default=None)
    Prompts: Optional[bool] = Field(default=None)
    Recordings: Optional[bool] = Field(default=None)
    VoiceMails: Optional[bool] = Field(default=None)


class BackupSettings(Schema):
    Contents: Optional[BackupContents] = Field(default=None)
    Rotation: Optional[int] = Field(default=None)
    Schedule: Optional[BackupSchedule] = Field(default=None)
    ScheduleEnabled: Optional[bool] = Field(default=None)


class ConferenceSettings(Schema):
    AutoCallParticipants: Optional[bool] = Field(default=None)
    EnableLocalMCU: Optional[bool] = Field(default=None)
    EnablePin: Optional[bool] = Field(default=None)
    Extension: Optional[str] = Field(default=None)
    ExternalNumbers: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    LogoPath: Optional[str] = Field(default=None)
    MusicOnHold: Optional[str] = Field(default=None)
    PinNumber: Optional[str] = Field(default=None)
    Zone: Optional[str] = Field(default=None)


class ConsoleRestrictions(Schema):
    AccessRestricted: Optional[bool] = Field(default=None)
    Id: str = Field(default_factory=list)
    IpWhitelist: list[str] = Field(default_factory=list)
    MyIpAddress: Optional[str] = Field(default=None)


class Contact(Schema):
    Business: Optional[str] = Field(default=None)
    Business2: Optional[str] = Field(default=None)
    BusinessFax: Optional[str] = Field(default=None)
    CompanyName: Optional[str] = Field(default=None)
    contact_type: Optional[str] = Field(default=None, alias="ContactType")
    Department: Optional[str] = Field(default=None)
    Email: Optional[str] = Field(default=None)
    FirstName: Optional[str] = Field(default=None)
    Home: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    LastName: Optional[str] = Field(default=None)
    Mobile2: Optional[str] = Field(default=None)
    Other: Optional[str] = Field(default=None)
    Pager: Optional[str] = Field(default=None)
    PhoneNumber: Optional[str] = Field(default=None)
    Tag: Optional[str] = Field(default=None)
    Title: Optional[str] = Field(default=None)


class ContactCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Contact] = Field(default_factory=list)


class ContactsDirSearchSettings(Schema):
    ExchangeCalendarProfileSwitching: Optional[bool] = Field(default=None)
    ExchangeEmailAddresses: list[str] = Field(default_factory=list)
    ExchangeFolders: list[str] = Field(default_factory=list)
    ExchangePassword: Optional[ConcealedPassword] = Field(default=None)
    ExchangeServerUrl: Optional[str] = Field(default=None)
    ExchangeUser: Optional[str] = Field(default=None)


class Country(Schema):
    Continent: Optional[str] = Field(default=None)
    CountryCode: Optional[str] = Field(default=None)
    CountryCodes: list[str] = Field(default_factory=list)
    DownloadUrl: Optional[str] = Field(default=None)
    ErpCode: Optional[str] = Field(default=None)
    ExitCode: Optional[str] = Field(default=None)
    Name: str = Field(default_factory=list)
    ParentErpCode: Optional[str] = Field(default=None)
    StunServer: Optional[str] = Field(default=None)
    VoicemailNo: Optional[str] = Field(default=None)
    WebMeetingZone: Optional[str] = Field(default=None)


class CountryCodes(Schema):
    country_codes: list[str] = Field(default_factory=list, alias="CountryCodes")


class CountryCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Country] = Field(default_factory=list)


class CreateBackup(Schema):
    Contents: Optional[BackupContents] = Field(default=None)
    Name: str = Field(default_factory=list)


class CreateTicket(Schema):
    CanCreateTicket: Optional[bool] = Field(default=None)
    create_ticket_status: Optional[CreateTicketStatus] = Field(default=None, alias="CreateTicketStatus")
    FixUrl: Optional[str] = Field(default=None)


class CrmAuthentication(Schema):
    Type: Optional[AuthenticationType] = Field(default=None)
    Values: list[str] = Field(default_factory=list)


class CrmChoice(Schema):
    Key: str = Field(default_factory=list)
    Value: Optional[str] = Field(default=None)


class CrmChoiceCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CrmChoice] = Field(default_factory=list)


class CrmContact(Schema):
    CompanyName: Optional[str] = Field(default=None)
    ContactRawData: Optional[str] = Field(default=None)
    contact_type: Optional[ContactType] = Field(default=None, alias="ContactType")
    ContactUrl: Optional[str] = Field(default=None)
    Department: Optional[str] = Field(default=None)
    Email: Optional[str] = Field(default=None)
    FaxBusiness: Optional[str] = Field(default=None)
    FirstName: Optional[str] = Field(default=None)
    LastName: Optional[str] = Field(default=None)
    Pager: Optional[str] = Field(default=None)
    PhoneBusiness: Optional[str] = Field(default=None)
    PhoneBusiness2: Optional[str] = Field(default=None)
    PhoneHome: Optional[str] = Field(default=None)
    PhoneMobile: Optional[str] = Field(default=None)
    PhoneMobile2: Optional[str] = Field(default=None)
    PhoneOther: Optional[str] = Field(default=None)
    PhotoUrl: Optional[str] = Field(default=None)
    Title: Optional[str] = Field(default=None)


class CrmContactCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CrmContact] = Field(default_factory=list)


class CrmParameter(Schema):
    Default: Optional[str] = Field(default=None)
    Editor: Optional[EditorType] = Field(default=None)
    ListValues: list[str] = Field(default_factory=list)
    ListValuesText: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Parent: Optional[str] = Field(default=None)
    RequestUrl: Optional[str] = Field(default=None)
    RequestUrlParameters: Optional[str] = Field(default=None)
    ResponseScenario: Optional[str] = Field(default=None)
    Title: Optional[str] = Field(default=None)
    Type: Optional[ParameterType] = Field(default=None)
    Validation: Optional[str] = Field(default=None)


class CrmParameterCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CrmParameter] = Field(default_factory=list)


class CrmSelectableValue(Schema):
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)


class CrmIntegration(Schema):
    country: Optional[str] = Field(default=None, alias="Country")
    EnabledForDidCalls: Optional[bool] = Field(default=None)
    EnabledForExternalCalls: Optional[bool] = Field(default=None)
    Id: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    phonebook_priority_options: Optional[PhonebookPriorityOptions] = Field(default=None, alias="PhonebookPriorityOptions")
    PhonebookSynchronization: Optional[bool] = Field(default=None)
    PossibleValues: list[CrmSelectableValue] = Field(default_factory=list)
    VariableChoices: list[CrmChoice] = Field(default_factory=list)


class CrmSelectableValueCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CrmSelectableValue] = Field(default_factory=list)


class CrmTemplate(Schema):
    authentication: Optional[CrmAuthentication] = Field(default=None, alias="Authentication")
    Name: str = Field(default_factory=list)
    Parameters: list[CrmParameter] = Field(default_factory=list)


class CrmTemplateCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CrmTemplate] = Field(default_factory=list)


class CrmTemplateSource(Schema):
    Value: Optional[str] = Field(default=None)


class CrmTestResult(Schema):
    IsError: Optional[bool] = Field(default=None)
    Log: Optional[str] = Field(default=None)
    Message: Optional[str] = Field(default=None)
    SearchResult: list[CrmContact] = Field(default_factory=list)


class CustomPrompt(Schema):
    CanBeDeleted: bool = Field(default_factory=list)
    DisplayName: str = Field(default_factory=list)
    FileLink: str = Field(default_factory=list)
    Filename: str = Field(default_factory=list)
    prompt_type: PromptType = Field(..., alias="PromptType")


class CustomPromptCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CustomPrompt] = Field(default_factory=list)


class CustomQueueRingtone(Schema):
    Queue: Optional[str] = Field(default=None)
    Ringtone: Optional[str] = Field(default=None)


class CustomQueueRingtoneCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CustomQueueRingtone] = Field(default_factory=list)


class DNProperty(Schema):
    Description: Optional[str] = Field(default=None)
    Id: Optional[int] = Field(default=None)
    Name: str = Field(default_factory=list)
    Value: str = Field(default_factory=list)


class DNPropertyCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[DNProperty] = Field(default_factory=list)


class DNRange(Schema):
    From: Optional[str] = Field(default=None)
    To: Optional[str] = Field(default=None)


class DNRangeCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[DNRange] = Field(default_factory=list)


class Destination(Schema):
    External: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    Tags: list[UserTag] = Field(default_factory=list)
    To: DestinationType = Field(...)
    Type: Optional[PeerType] = Field(default=None)


class AvailableRouting(Schema):
    BusyAllCalls: Optional[bool] = Field(default=None)
    BusyExternal: Optional[Destination] = Field(default=None)
    BusyInternal: Optional[Destination] = Field(default=None)
    NoAnswerAllCalls: Optional[bool] = Field(default=None)
    NoAnswerExternal: Optional[Destination] = Field(default=None)
    NoAnswerInternal: Optional[Destination] = Field(default=None)
    NotRegisteredAllCalls: Optional[bool] = Field(default=None)
    NotRegisteredExternal: Optional[Destination] = Field(default=None)
    NotRegisteredInternal: Optional[Destination] = Field(default=None)


class AwayRouting(Schema):
    AllHoursExternal: Optional[bool] = Field(default=None)
    AllHoursInternal: Optional[bool] = Field(default=None)
    External: Optional[Destination] = Field(default=None)
    Internal: Optional[Destination] = Field(default=None)


class DetailedQueueStatistics(Schema):
    AnsweredCount: Optional[int] = Field(default=None)
    AvgRingTime: Optional[str] = Field(default=None)
    AvgTalkTime: Optional[str] = Field(default=None)
    CallbacksCount: Optional[int] = Field(default=None)
    CallsCount: Optional[int] = Field(default=None)
    QueueDn: Optional[str] = Field(default=None)
    QueueDnNumber: str = Field(default_factory=list)
    RingTime: Optional[str] = Field(default=None)
    TalkTime: Optional[str] = Field(default=None)


class DetailedQueueStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[DetailedQueueStatistics] = Field(default_factory=list)


class DeviceInfo(Schema):
    Assigned: Optional[bool] = Field(default=None)
    AssignedUser: Optional[str] = Field(default=None)
    DetectedAt: Optional[datetime] = Field(default=None)
    FirmwareVersion: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    InterfaceLink: Optional[str] = Field(default=None)
    MAC: Optional[str] = Field(default=None)
    Model: Optional[str] = Field(default=None)
    NetworkAddress: Optional[str] = Field(default=None)
    NetworkPath: Optional[str] = Field(default=None)
    Parameters: Optional[str] = Field(default=None)
    SbcName: Optional[str] = Field(default=None)
    TemplateName: Optional[str] = Field(default=None)
    UserAgent: Optional[str] = Field(default=None)
    Vendor: Optional[str] = Field(default=None)
    ViaSBC: Optional[bool] = Field(default=None)


class DeviceInfoCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[DeviceInfo] = Field(default_factory=list)


class DeviceLine(Schema):
    Key: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    Number: str = Field(default_factory=list)


class DeviceLineCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[DeviceLine] = Field(default_factory=list)


class DialCodeSettings(Schema):
    DialCodeBillingCode: Optional[str] = Field(default=None)
    DialCodeHideCallerID: Optional[str] = Field(default=None)
    DialCodeHotdesking: Optional[str] = Field(default=None)
    DialCodeHotelAccess: Optional[str] = Field(default=None)
    DialCodeIntercom: Optional[str] = Field(default=None)
    DialCodeLoggedInQueue: Optional[str] = Field(default=None)
    DialCodeLoggedOutQueue: Optional[str] = Field(default=None)
    DialCodeOutOffice: Optional[str] = Field(default=None)
    DialCodePark: Optional[str] = Field(default=None)
    DialCodePickup: Optional[str] = Field(default=None)
    DialCodeProfileStatus: Optional[str] = Field(default=None)
    DialCodeUnpark: Optional[str] = Field(default=None)
    DialCodeVMail: Optional[str] = Field(default=None)


class DirectoryParameters(Schema):
    Filesystem: FileSystemType = Field(...)
    Json: Optional[str] = Field(default=None)
    Path: Optional[str] = Field(default=None)


class E164Settings(Schema):
    AreaCode: Optional[str] = Field(default=None)
    CountryCode: Optional[str] = Field(default=None)
    CountryName: Optional[str] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    InternationalCode: Optional[str] = Field(default=None)
    NationalCode: Optional[str] = Field(default=None)
    Prefix: Optional[str] = Field(default=None)
    RemoveAreaCode: Optional[bool] = Field(default=None)
    RemoveCountryCode: Optional[bool] = Field(default=None)


class EmailTemplate(Schema):
    Body: str = Field(default_factory=list)
    From: Optional[str] = Field(default=None)
    IsConference: Optional[bool] = Field(default=None)
    IsDefault: Optional[bool] = Field(default=None)
    Lang: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Subject: Optional[str] = Field(default=None)
    TemplatePath: str = Field(default_factory=list)


class EmailTemplateCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[EmailTemplate] = Field(default_factory=list)


class EmergencyGeoLocation(Schema):
    FriendlyName: str = Field(default_factory=list)
    Id: str = Field(default_factory=list)


class EmergencyGeoLocationCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[EmergencyGeoLocation] = Field(default_factory=list)


class EmergencyGeoTrunkLocation(Schema):
    Id: str = Field(default_factory=list)
    Location: EmergencyGeoLocation = Field(...)
    ProviderUri: str = Field(default_factory=list)
    TrunkDn: Optional[str] = Field(default=None)


class EmergencyGeoTrunkLocationCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[EmergencyGeoTrunkLocation] = Field(default_factory=list)


class EntityRestrictions(Schema):
    Allowed: Optional[int] = Field(default=None)
    Unlimited: Optional[bool] = Field(default=None)
    Used: Optional[int] = Field(default=None)


class EventLog(Schema):
    EventId: Optional[int] = Field(default=None)
    Group: Optional[str] = Field(default=None)
    GroupName: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    Message: Optional[str] = Field(default=None)
    Params: list[str] = Field(default_factory=list)
    Source: Optional[str] = Field(default=None)
    TimeGenerated: Optional[datetime] = Field(default=None)
    Type: Optional[EventLogType] = Field(default=None)


class EventLogCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[EventLog] = Field(default_factory=list)


class ExtensionFilter(Schema):
    CallIds: list[str] = Field(default_factory=list)
    Number: Optional[str] = Field(default=None)


class ActivityLogsFilter(Schema):
    Extensions: list[ExtensionFilter] = Field(default_factory=list)


class ExtensionFilterCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ExtensionFilter] = Field(default_factory=list)


class ExtensionStatistics(Schema):
    DisplayName: Optional[str] = Field(default=None)
    Dn: str = Field(default_factory=list)
    InboundAnsweredCount: Optional[int] = Field(default=None)
    InboundAnsweredTalkingDur: Optional[str] = Field(default=None)
    InboundUnansweredCount: Optional[int] = Field(default=None)
    OutboundAnsweredCount: Optional[int] = Field(default=None)
    OutboundAnsweredTalkingDur: Optional[str] = Field(default=None)
    OutboundUnansweredCount: Optional[int] = Field(default=None)


class ExtensionStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ExtensionStatistics] = Field(default_factory=list)


class ExtensionsStatisticsByRingGroups(Schema):
    ExtensionAnsweredCount: Optional[int] = Field(default=None)
    ExtensionDisplayName: Optional[str] = Field(default=None)
    ExtensionDn: str = Field(default_factory=list)
    RingGroupDisplayName: Optional[str] = Field(default=None)
    RingGroupDn: str = Field(default_factory=list)
    RingGroupReceivedCount: Optional[int] = Field(default=None)
    RingGroupUnansweredCount: Optional[int] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)
    SortOrder: Optional[int] = Field(default=None)


class ExtensionsStatisticsByRingGroupsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ExtensionsStatisticsByRingGroups] = Field(default_factory=list)


class ExternalAccount(Schema):
    Email: str = Field(default_factory=list)
    Id: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)


class ExternalAccountCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ExternalAccount] = Field(default_factory=list)


class ExternalAccountsPage(Schema):
    NextPageToken: Optional[str] = Field(default=None)
    Users: list[ExternalAccount] = Field(default_factory=list)


class FailoverScriptFile(Schema):
    Filename: str = Field(default_factory=list)


class FaxServerSettings(Schema):
    AuthId: Optional[str] = Field(default=None)
    AuthPassword: Optional[ConcealedPassword] = Field(default=None)
    AutoCleanup: Optional[bool] = Field(default=None)
    Email: Optional[str] = Field(default=None)
    FaxServerId: Optional[int] = Field(default=None)
    G711ToT38Fallback: Optional[bool] = Field(default=None)
    MaxAge: Optional[int] = Field(default=None)
    Number: str = Field(default_factory=list)
    RemoteStorageEnabled: Optional[bool] = Field(default=None)


class FirewallState(Schema):
    Html: Optional[str] = Field(default=None)
    Id: str = Field(default_factory=list)
    Running: Optional[bool] = Field(default=None)
    Stopping: Optional[bool] = Field(default=None)


class Firmware(Schema):
    Filename: Optional[str] = Field(default=None)
    Id: str = Field(default_factory=list)
    Model: Optional[str] = Field(default=None)
    Vendor: Optional[str] = Field(default=None)
    Version: Optional[str] = Field(default=None)


class FirmwareCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Firmware] = Field(default_factory=list)


class FirmwareState(Schema):
    Count: Optional[int] = Field(default=None)
    FileNames: list[str] = Field(default_factory=list)
    Id: Optional[str] = Field(default=None)
    TotalSize: Optional[int] = Field(default=None)


class FirstAvailableNumber(Schema):
    Number: Optional[str] = Field(default=None)


class ForwardingProfile(Schema):
    AcceptMultipleCalls: Optional[bool] = Field(default=None)
    AvailableRoute: Optional[AvailableRouting] = Field(default=None)
    AwayRoute: Optional[AwayRouting] = Field(default=None)
    BlockPushCalls: Optional[bool] = Field(default=None)
    CustomMessage: Optional[str] = Field(default=None)
    CustomName: Optional[str] = Field(default=None)
    DisableRingGroupCalls: Optional[bool] = Field(default=None)
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    NoAnswerTimeout: Optional[int] = Field(default=None)
    OfficeHoursAutoQueueLogOut: Optional[bool] = Field(default=None)
    RingMyMobile: Optional[bool] = Field(default=None)


class ForwardingProfileCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ForwardingProfile] = Field(default_factory=list)


class FxsModel(Schema):
    CanBeSBC: Optional[bool] = Field(default=None)
    DisplayName: str = Field(default_factory=list)
    UserAgent: str = Field(default_factory=list)


class FxsModelCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[FxsModel] = Field(default_factory=list)


class FxsProvisioning(Schema):
    LocalAudioPortEnd: Optional[int] = Field(default=None)
    LocalAudioPortStart: Optional[int] = Field(default=None)
    LocalInterface: Optional[str] = Field(default=None)
    LocalSipPort: Optional[int] = Field(default=None)
    Method: Optional[ProvType] = Field(default=None)
    ProvLink: Optional[str] = Field(default=None)
    RemoteFQDN: Optional[str] = Field(default=None)
    RemotePort: Optional[int] = Field(default=None)
    SbcName: Optional[str] = Field(default=None)


class FxsVariableChoice(Schema):
    DisplayName: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)


class FxsVariable(Schema):
    Choices: list[FxsVariableChoice] = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    Title: str = Field(default_factory=list)
    ValidationType: Optional[str] = Field(default=None)


class FxsTemplate(Schema):
    AllowedNetConfigs: list[str] = Field(default_factory=list)
    AllowSSLProvisioning: Optional[bool] = Field(default=None)
    Brand: str = Field(default_factory=list)
    Content: Optional[str] = Field(default=None)
    device_type: DeviceType = Field(..., alias="DeviceType")
    Id: str = Field(default_factory=list)
    IsCustom: bool = Field(default_factory=list)
    Languages: list[str] = Field(default_factory=list)
    Models: list[FxsModel] = Field(default_factory=list)
    NumberOfExtensions: int = Field(default_factory=list)
    RpsEnabled: Optional[bool] = Field(default=None)
    template_type: TemplateType = Field(..., alias="TemplateType")
    TimeZones: list[str] = Field(default_factory=list)
    URL: str = Field(default_factory=list)
    Variables: list[FxsVariable] = Field(default_factory=list)


class FxsTemplateCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[FxsTemplate] = Field(default_factory=list)


class FxsVariableChoiceCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[FxsVariableChoice] = Field(default_factory=list)


class FxsVariableCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[FxsVariable] = Field(default_factory=list)


class GarbageCollect(Schema):
    Blocking: Optional[bool] = Field(default=None)
    Compacting: Optional[bool] = Field(default=None)
    Generation: Optional[int] = Field(default=None)
    Mode: Optional[GCCollectionMode] = Field(default=None)


class GatewayParameter(Schema):
    CanHaveDID: Optional[bool] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    InboundPossibleValues: list[str] = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    OutboundPossibleValues: list[str] = Field(default_factory=list)
    SourceIDPossibleValues: list[str] = Field(default_factory=list)


class GatewayParameterBinding(Schema):
    Custom: Optional[str] = Field(default=None)
    ParamId: int = Field(default_factory=list)
    ValueId: int = Field(default_factory=list)


class Gateway(Schema):
    Codecs: list[str] = Field(default_factory=list)
    DeliverAudio: Optional[bool] = Field(default=None)
    DestNumberInRemotePartyIDCalled: Optional[bool] = Field(default=None)
    DestNumberInRequestLineURI: Optional[bool] = Field(default=None)
    DestNumberInTo: Optional[bool] = Field(default=None)
    Host: Optional[str] = Field(default=None)
    Id: Optional[int] = Field(default=None)
    InboundParams: list[GatewayParameterBinding] = Field(default_factory=list)
    Internal: Optional[bool] = Field(default=None)
    IPInRegistrationContact: Optional[IPInRegistrationContactType] = Field(default=None)
    Lines: Optional[int] = Field(default=None)
    MatchingStrategy: Optional[MatchingStrategyType] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    OutboundCallerID: Optional[str] = Field(default=None)
    OutboundParams: list[GatewayParameterBinding] = Field(default_factory=list)
    Port: Optional[int] = Field(default=None)
    ProxyHost: Optional[str] = Field(default=None)
    ProxyPort: Optional[int] = Field(default=None)
    RequireRegistrationFor: Optional[RequireRegistrationForType] = Field(default=None)
    SourceIdentification: list[GatewayParameterBinding] = Field(default_factory=list)
    SpecifiedIPForRegistrationContact: Optional[str] = Field(default=None)
    SRTPMode: Optional[SRTPModeType] = Field(default=None)
    SupportReinvite: Optional[bool] = Field(default=None)
    SupportReplaces: Optional[bool] = Field(default=None)
    TemplateFilename: Optional[str] = Field(default=None)
    TimeBetweenReg: Optional[int] = Field(default=None)
    Type: GatewayType = Field(...)
    UseIPInContact: Optional[bool] = Field(default=None)
    VariableChoices: list[Choice] = Field(default_factory=list)


class GatewayParameterBindingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[GatewayParameterBinding] = Field(default_factory=list)


class GatewayParameterCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[GatewayParameter] = Field(default_factory=list)


class GatewayParameterValue(Schema):
    Description: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)


class GatewayParameterValueCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[GatewayParameterValue] = Field(default_factory=list)


class GeneralLiveChatSettings(Schema):
    AllowSoundNotifications: Optional[bool] = Field(default=None)
    authentication: Optional[Authentication] = Field(default=None, alias="Authentication")
    DisableOfflineMessages: Optional[bool] = Field(default=None)
    EnableGA: Optional[bool] = Field(default=None)
    EnableOnMobile: Optional[bool] = Field(default=None)
    GdprEnabled: Optional[bool] = Field(default=None)
    Greeting: Optional[LiveChatGreeting] = Field(default=None)


class GeneralSettingsForApps(Schema):
    AllowChangePassword: Optional[bool] = Field(default=None)
    auto_scheduler_settings: Optional[AutoSchedulerSettings] = Field(default=None, alias="AutoSchedulerSettings")
    avatar_style: Optional[AvatarStyle] = Field(default=None, alias="AvatarStyle")
    BrandLogoImage: Optional[str] = Field(default=None)
    BrandMainImage: Optional[str] = Field(default=None)
    BrandUrl: Optional[str] = Field(default=None)
    EnableChat: Optional[bool] = Field(default=None)
    HideAbandonedQueueCalls: Optional[bool] = Field(default=None)
    HideCRMContacts: Optional[bool] = Field(default=None)
    HideInteractionHistory: Optional[bool] = Field(default=None)
    HideSystemExtensions: Optional[bool] = Field(default=None)
    NameOfCustomAvailableStatus: Optional[str] = Field(default=None)
    NameOfCustomOutOfOfficeStatus: Optional[str] = Field(default=None)


class GeneralSettingsForPbx(Schema):
    AllowFwdToExternal: Optional[bool] = Field(default=None)
    BusyMonitor: Optional[bool] = Field(default=None)
    BusyMonitorTimeout: Optional[int] = Field(default=None)
    DisableOutboundCallsOutOfficeHours: Optional[bool] = Field(default=None)
    EnableVMenuOutboundCalls: Optional[bool] = Field(default=None)
    HDAutoLogoutEnabled: Optional[bool] = Field(default=None)
    HDAutoLogoutTime: Optional[str] = Field(default=None)
    LimitCallPickup: Optional[bool] = Field(default=None)
    OperatorExtension: Optional[str] = Field(default=None)
    PlayBusy: Optional[bool] = Field(default=None)
    ScheduledReportGenerationTime: Optional[str] = Field(default=None)


class GoogleUserSync(Schema):
    IsEnabled: Optional[bool] = Field(default=None)
    IsSyncDepartments: Optional[bool] = Field(default=None)
    IsSyncPersonalContacts: Optional[bool] = Field(default=None)
    IsSyncPhoto: Optional[bool] = Field(default=None)
    SelectedUsers: list[str] = Field(default_factory=list)
    StartingExtensionNumber: Optional[str] = Field(default=None)
    SyncType: Optional[IntegrationSyncType] = Field(default=None)
    UseCalendarEventsAsPresence: Optional[bool] = Field(default=None)


class GoogleSettings(Schema):
    ClientId: Optional[str] = Field(default=None)
    ClientSecret: Optional[ConcealedPassword] = Field(default=None)
    Id: str = Field(default_factory=list)
    IsExtensionSignInEnabled: Optional[bool] = Field(default=None)
    ProjectId: Optional[str] = Field(default=None)
    ProvisionUrl: Optional[str] = Field(default=None)
    ReCaptchaEnabled: Optional[bool] = Field(default=None)
    UserSync: Optional[GoogleUserSync] = Field(default=None)


class Greeting(Schema):
    DisplayName: Optional[str] = Field(default=None)
    Filename: Optional[str] = Field(default=None)
    Type: ProfileType = Field(...)


class GreetingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Greeting] = Field(default_factory=list)


class GreetingFile(Schema):
    DisplayName: Optional[str] = Field(default=None)
    Filename: str = Field(default_factory=list)


class GroupProps(Schema):
    DectMaxCount: Optional[int] = Field(default=None)
    Fqdn: Optional[str] = Field(default=None)
    LiveChatMaxCount: Optional[int] = Field(default=None)
    OutboundRulesMaxCount: Optional[int] = Field(default=None)
    PersonalContactsMaxCount: Optional[int] = Field(default=None)
    PromptsMaxCount: Optional[int] = Field(default=None)
    ResellerId: Optional[str] = Field(default=None)
    ResellerName: Optional[str] = Field(default=None)
    SbcMaxCount: Optional[int] = Field(default=None)
    startup_license: Optional[StartupLicense] = Field(default=None, alias="StartupLicense")
    StartupOwnerEmail: Optional[str] = Field(default=None)
    SubcriptionExpireDate: Optional[datetime] = Field(default=None)
    Subscription: Optional[str] = Field(default=None)
    SubscriptionType: Optional[str] = Field(default=None)
    SystemNumberFrom: Optional[str] = Field(default=None)
    SystemNumberTo: Optional[str] = Field(default=None)
    TrunkNumberFrom: Optional[str] = Field(default=None)
    TrunkNumberTo: Optional[str] = Field(default=None)
    TrunksMaxCount: Optional[int] = Field(default=None)
    UserNumberFrom: Optional[str] = Field(default=None)
    UserNumberTo: Optional[str] = Field(default=None)


class Holiday(Schema):
    Day: int = Field(default_factory=list)
    DayEnd: int = Field(default_factory=list)
    HolidayPrompt: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    IsRecurrent: Optional[bool] = Field(default=None)
    Month: int = Field(default_factory=list)
    MonthEnd: int = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    TimeOfEndDate: str = Field(default_factory=list)
    TimeOfStartDate: str = Field(default_factory=list)
    Year: int = Field(default_factory=list)
    YearEnd: int = Field(default_factory=list)


class HolidayCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Holiday] = Field(default_factory=list)


class HotelServices(Schema):
    Enabled: Optional[bool] = Field(default=None)
    HotelGroups: list[str] = Field(default_factory=list)
    IntegrationType: Optional[PmsIntegrationType] = Field(default=None)
    IpAddress: Optional[str] = Field(default=None)
    NoAnswerDestination: Optional[Destination] = Field(default=None)
    NoAnswerTimeout: Optional[int] = Field(default=None)
    Port: Optional[int] = Field(default=None)


class IActionResult(Schema):
    pass


class InboundCall(Schema):
    CallDuration: str = Field(default_factory=list)
    CallHistoryId: Optional[str] = Field(default=None)
    CdrId: str = Field(default_factory=list)
    DestinationCallerId: Optional[str] = Field(default=None)
    DestinationDisplayName: Optional[str] = Field(default=None)
    DestinationDn: Optional[str] = Field(default=None)
    Did: Optional[str] = Field(default=None)
    QualityReport: Optional[bool] = Field(default=None)
    RecordingId: Optional[int] = Field(default=None)
    RecordingUrl: Optional[str] = Field(default=None)
    RingingDuration: str = Field(default_factory=list)
    RuleName: Optional[str] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)
    SourceCallerId: Optional[str] = Field(default=None)
    SourceDisplayName: Optional[str] = Field(default=None)
    SourceDn: Optional[str] = Field(default=None)
    StartTime: datetime = Field(default_factory=list)
    Status: Optional[str] = Field(default=None)
    Summary: Optional[str] = Field(default=None)
    TalkingDuration: str = Field(default_factory=list)
    Transcription: Optional[str] = Field(default=None)
    TrunkName: Optional[str] = Field(default=None)
    TrunkNumber: Optional[str] = Field(default=None)


class InboundCallCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[InboundCall] = Field(default_factory=list)


class InboundRuleReport(Schema):
    DID: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    InOfficeRouting: Optional[Destination] = Field(default=None)
    OutOfficeRouting: Optional[Destination] = Field(default=None)
    RuleName: Optional[str] = Field(default=None)
    Trunk: Optional[str] = Field(default=None)


class InboundRuleReportCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[InboundRuleReport] = Field(default_factory=list)


class InstallUpdates(Schema):
    Entries: list[UUID] = Field(default_factory=list)
    Key: UUID = Field(default_factory=list)


class KeyValuePair_2OfString_OnBoardConnectedParticipant(Schema):
    pass


class KeyValuePair_2OfString_OnBoardConnectedParticipantCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[KeyValuePair_2OfString_OnBoardConnectedParticipant] = Field(default_factory=list)


class LanguageItem(Schema):
    Code: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)


class LastCdrAndChatMessageTimestamp(Schema):
    LastCdrStartedAt: datetime = Field(default_factory=list)
    LastChatMessageTimeSent: datetime = Field(default_factory=list)


class LastCdrAndChatMessageTimestampCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[LastCdrAndChatMessageTimestamp] = Field(default_factory=list)


class License(Schema):
    CountryCode: Optional[str] = Field(default=None)
    IsMaintainceExpired: Optional[bool] = Field(default=None)
    ProductCode: Optional[str] = Field(default=None)


class LicenseStatus(Schema):
    Activated: Optional[bool] = Field(default=None)
    ActiveModules: list[str] = Field(default_factory=list)
    AdminEMail: Optional[str] = Field(default=None)
    CompanyName: Optional[str] = Field(default=None)
    ContactName: Optional[str] = Field(default=None)
    CountryCode: Optional[str] = Field(default=None)
    CountryName: Optional[str] = Field(default=None)
    EMail: Optional[str] = Field(default=None)
    ExpirationDate: Optional[datetime] = Field(default=None)
    LicenseActive: Optional[bool] = Field(default=None)
    LicenseKey: str = Field(default_factory=list)
    MaintenanceExpiresAt: Optional[datetime] = Field(default=None)
    MaxSimCalls: Optional[int] = Field(default=None)
    ProductCode: Optional[str] = Field(default=None)
    ResellerName: Optional[str] = Field(default=None)
    SimMeetingParticipants: Optional[int] = Field(default=None)
    Support: Optional[bool] = Field(default=None)
    Telephone: Optional[str] = Field(default=None)
    Version: Optional[str] = Field(default=None)


class LinkMyGroupPartnerRequestBody(Schema):
    resellerId: str = Field(default_factory=list)


class LiveChatAdvancedSettings(Schema):
    CallTitle: Optional[str] = Field(default=None)
    CommunicationOptions: Optional[LiveChatCommunication] = Field(default=None)
    EnableDirectCall: Optional[bool] = Field(default=None)
    IgnoreQueueOwnership: Optional[bool] = Field(default=None)


class LiveChatBox(Schema):
    button_icon_type: Optional[ButtonIconType] = Field(default=None, alias="ButtonIconType")
    ButtonIconUrl: Optional[str] = Field(default=None)
    ChatDelay: Optional[int] = Field(default=None)
    Height: Optional[str] = Field(default=None)
    live_chat_language: Optional[LiveChatLanguage] = Field(default=None, alias="LiveChatLanguage")
    live_message_userinfo_format: Optional[LiveMessageUserinfoFormat] = Field(default=None, alias="LiveMessageUserinfoFormat")
    MessageDateformat: Optional[LiveChatMessageDateformat] = Field(default=None)
    MinimizedStyle: Optional[LiveChatMinimizedStyle] = Field(default=None)
    OperatorIcon: Optional[str] = Field(default=None)
    OperatorName: Optional[str] = Field(default=None)
    ShowOperatorActualName: Optional[bool] = Field(default=None)
    WindowIcon: Optional[str] = Field(default=None)


class LiveChatStyling(Schema):
    Animation: Optional[AnimationStyle] = Field(default=None)
    Minimized: Optional[bool] = Field(default=None)
    Style: Optional[str] = Field(default=None)
    UseRubik: Optional[bool] = Field(default=None)


class LocationSettings(Schema):
    file_system_type: Optional[FileSystemType] = Field(default=None, alias="FileSystemType")
    FtpPassword: Optional[ConcealedPassword] = Field(default=None)
    FtpPath: Optional[str] = Field(default=None)
    FtpUser: Optional[str] = Field(default=None)
    FtpValidateCertificate: Optional[bool] = Field(default=None)
    GbJson: Optional[ConcealedDataFile] = Field(default=None)
    GbPath: Optional[str] = Field(default=None)
    LocalPath: Optional[str] = Field(default=None)
    NsDomain: Optional[str] = Field(default=None)
    NsPassword: Optional[ConcealedPassword] = Field(default=None)
    NsPath: Optional[str] = Field(default=None)
    NsUser: Optional[str] = Field(default=None)
    SftpPassword: Optional[ConcealedPassword] = Field(default=None)
    SftpPath: Optional[str] = Field(default=None)
    SftpPrivateKey: Optional[ConcealedDataFile] = Field(default=None)
    SftpUser: Optional[str] = Field(default=None)
    SharePointPath: Optional[str] = Field(default=None)


class BackupRepositorySettings(Schema):
    Location: Optional[LocationSettings] = Field(default=None)


class LogEntry(Schema):
    Text: str = Field(default_factory=list)
    TimeStamp: datetime = Field(default_factory=list)


class LogEntryCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[LogEntry] = Field(default_factory=list)


class LoggingSettings(Schema):
    KeepLogs: Optional[bool] = Field(default=None)
    KeepLogsDays: Optional[int] = Field(default=None)
    LoggingLevel: Optional[int] = Field(default=None)


class M365ToPbxBinding(Schema):
    From: Optional[SynchronizedM365Profile] = Field(default=None)
    To: Optional[SynchronizedPbxProfile] = Field(default=None)


class M365ToPbxBindingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[M365ToPbxBinding] = Field(default_factory=list)


class MCURequestStatus(Schema):
    ErrorMessage: Optional[str] = Field(default=None)
    McuId: Optional[str] = Field(default=None)
    Operation: Optional[McuOperation] = Field(default=None)
    RequestExpiration: Optional[datetime] = Field(default=None)
    State: Optional[McuReqState] = Field(default=None)


class MakeCallUserRecordGreetingRequestBody(Schema):
    dn: str = Field(default_factory=list)
    filename: str = Field(default_factory=list)


class MeetingParams(Schema):
    bitrate_data: int = Field(default_factory=list)
    bitrate_video: int = Field(default_factory=list)
    canchangemedia: Optional[int] = Field(default=None)
    clicktocall: Optional[int] = Field(default=None)
    forcemoderator: Optional[int] = Field(default=None)
    hideparticipants: Optional[int] = Field(default=None)
    mcu: str = Field(default_factory=list)
    meetingduration: int = Field(default_factory=list)
    meetingtitle: str = Field(default_factory=list)
    moderateparticipants: Optional[int] = Field(default=None)
    needorganizer: Optional[int] = Field(default=None)
    note: str = Field(default_factory=list)
    org_properties: Optional[str] = Field(default=None)
    part_properties: Optional[str] = Field(default=None)
    privaterooms: Optional[int] = Field(default=None)
    quickmeeting: int = Field(default_factory=list)


class Microsoft365Status(Schema):
    ApplicationId: Optional[str] = Field(default=None)
    ExceptionMessage: Optional[str] = Field(default=None)
    ProvisionUrl: Optional[str] = Field(default=None)


class Microsoft365SubscriptionTestResult(Schema):
    ExceptionMessage: Optional[str] = Field(default=None)
    Fqdn: Optional[str] = Field(default=None)
    IsSubscriptionAvailable: Optional[bool] = Field(default=None)


class Microsoft365TeamsIntegration(Schema):
    AreaCode: Optional[str] = Field(default=None)
    DialPlanCode: Optional[str] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    Id: int = Field(default_factory=list)
    IsDynamicIP: Optional[bool] = Field(default=None)
    IsNativeFQDN: Optional[bool] = Field(default=None)
    SbcCertificate: Optional[ConcealedDataFile] = Field(default=None)
    SbcCertificateExpirationDate: Optional[str] = Field(default=None)
    SbcFQDN: Optional[str] = Field(default=None)
    SbcPrivateKey: Optional[ConcealedDataFile] = Field(default=None)
    SecureSipEnabled: Optional[bool] = Field(default=None)
    SipDomain: Optional[str] = Field(default=None)
    TlsPortForNativeFQDN: Optional[int] = Field(default=None)
    TlsPortForNonNativeFQDN: Optional[int] = Field(default=None)


class MonitoringState(Schema):
    DN: str = Field(default_factory=list)
    Expiration: int = Field(default_factory=list)


class MusicOnHoldSettings(Schema):
    Id: int = Field(default_factory=list)
    MusicOnHold: Optional[str] = Field(default=None)
    MusicOnHold1: Optional[str] = Field(default=None)
    MusicOnHold2: Optional[str] = Field(default=None)
    MusicOnHold3: Optional[str] = Field(default=None)
    MusicOnHold4: Optional[str] = Field(default=None)
    MusicOnHold5: Optional[str] = Field(default=None)
    MusicOnHold6: Optional[str] = Field(default=None)
    MusicOnHold7: Optional[str] = Field(default=None)
    MusicOnHold8: Optional[str] = Field(default=None)
    MusicOnHold9: Optional[str] = Field(default=None)
    MusicOnHoldRandomize: Optional[bool] = Field(default=None)
    MusicOnHoldRandomizePerCall: Optional[bool] = Field(default=None)


class NetworkInterface(Schema):
    Id: str = Field(default_factory=list)


class NetworkInterfaceCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[NetworkInterface] = Field(default_factory=list)


class NetworkSettings(Schema):
    AllowSourceAsOutbound: Optional[bool] = Field(default=None)
    DirectSIPAllowExternal: Optional[bool] = Field(default=None)
    DirectSIPLocalDomain: Optional[str] = Field(default=None)
    FirewallKeepAlive: Optional[bool] = Field(default=None)
    FirewallKeepAliveInterval: Optional[int] = Field(default=None)
    Id: str = Field(default_factory=list)
    IpV6BindingEnabled: Optional[bool] = Field(default=None)
    PbxPublicFQDN: Optional[str] = Field(default=None)
    PublicInterface: Optional[str] = Field(default=None)
    PublicStaticIP: Optional[str] = Field(default=None)
    SipPort: Optional[int] = Field(default=None)
    StunDisabled: Optional[bool] = Field(default=None)
    StunPrimaryHost: Optional[str] = Field(default=None)
    StunPrimaryPort: Optional[int] = Field(default=None)
    StunQuery: Optional[int] = Field(default=None)
    StunSecondaryHost: Optional[str] = Field(default=None)
    StunSecondaryPort: Optional[int] = Field(default=None)
    StunThirdHost: Optional[str] = Field(default=None)
    StunThirdPort: Optional[int] = Field(default=None)
    TunnelPort: Optional[int] = Field(default=None)


class NotificationSettings(Schema):
    CanEditEmailAddresses: Optional[bool] = Field(default=None)
    CanEditMailServerType: Optional[bool] = Field(default=None)
    EmailAddresses: Optional[str] = Field(default=None)
    FakeId: str = Field(default_factory=list)
    MailAddress: Optional[str] = Field(default=None)
    MailPassword: Optional[ConcealedPassword] = Field(default=None)
    MailServer: Optional[str] = Field(default=None)
    mail_server_type: Optional[MailServerType] = Field(default=None, alias="MailServerType")
    MailSslEnabled: Optional[bool] = Field(default=None)
    MailUser: Optional[str] = Field(default=None)
    NotifyCallDenied: Optional[bool] = Field(default=None)
    NotifyEmergencyNumberDialed: Optional[bool] = Field(default=None)
    NotifyExtensionAdded: Optional[bool] = Field(default=None)
    NotifyIPBlocked: Optional[bool] = Field(default=None)
    NotifyLicenseLimit: Optional[bool] = Field(default=None)
    NotifyNetworkError: Optional[bool] = Field(default=None)
    NotifyRequestAntiHacked: Optional[bool] = Field(default=None)
    NotifyServiceStopped: Optional[bool] = Field(default=None)
    NotifyStorageLimit: Optional[bool] = Field(default=None)
    NotifySTUNError: Optional[bool] = Field(default=None)
    NotifySuccessScheduledBackups: Optional[bool] = Field(default=None)
    NotifySystemOwners: Optional[bool] = Field(default=None)
    NotifyTrunkError: Optional[bool] = Field(default=None)
    NotifyTrunkFailover: Optional[bool] = Field(default=None)
    NotifyTrunkStatusChanged: Optional[bool] = Field(default=None)
    NotifyUpdatesAvailable: Optional[bool] = Field(default=None)
    NotifyWhenRecordingsQuotaReached: Optional[bool] = Field(default=None)
    NotifyWhenVoicemailQuotaReached: Optional[bool] = Field(default=None)
    RecordingsQuotaPercentage: Optional[int] = Field(default=None)
    VoicemailQuotaPercentage: Optional[int] = Field(default=None)


class OauthState(Schema):
    CodeChallenge: Optional[str] = Field(default=None)
    State: Optional[str] = Field(default=None)


class OauthStateParam(Schema):
    PKCECodeVerifier: Optional[str] = Field(default=None)
    RedirectUri: str = Field(default_factory=list)
    Variable: str = Field(default_factory=list)


class OnBoardMcuDataDetail(Schema):
    Active: bool = Field(default_factory=list)
    Cloud: bool = Field(default_factory=list)
    Enabled: bool = Field(default_factory=list)
    Guid: str = Field(default_factory=list)
    Host: str = Field(default_factory=list)
    Ip: str = Field(default_factory=list)
    Port: int = Field(default_factory=list)
    Version: str = Field(default_factory=list)


class OnBoardMcuData(Schema):
    Attempts: int = Field(default_factory=list)
    AttendeeCount: int = Field(default_factory=list)
    ClockSkew: int = Field(default_factory=list)
    Connected: bool = Field(default_factory=list)
    Cpu: int = Field(default_factory=list)
    Delay: int = Field(default_factory=list)
    Fqdn: str = Field(default_factory=list)
    FreeDiskSpace: int = Field(default_factory=list)
    Mcu: OnBoardMcuDataDetail = Field(...)
    MeetingCount: int = Field(default_factory=list)
    Memory: int = Field(default_factory=list)
    NetIn: int = Field(default_factory=list)
    NetOut: int = Field(default_factory=list)
    RestartTime: str = Field(default_factory=list)
    StartTime: str = Field(default_factory=list)
    Ts: datetime = Field(default_factory=list)
    UpdateInterval: int = Field(default_factory=list)


class OnBoardMcuRow(Schema):
    Active: bool = Field(default_factory=list)
    BandCap: int = Field(default_factory=list)
    CityName: str = Field(default_factory=list)
    Cloud: bool = Field(default_factory=list)
    country: str = Field(default_factory=list, alias="Country")
    CountryName: str = Field(default_factory=list)
    Enabled: bool = Field(default_factory=list)
    Guid: str = Field(default_factory=list)
    Host: str = Field(default_factory=list)
    InstallScript: str = Field(default_factory=list)
    Ip: str = Field(default_factory=list)
    Latitude: Optional[float | str | ReferenceNumeric] = Field(default=None)
    Longitude: Optional[float | str | ReferenceNumeric] = Field(default=None)
    ManualGeo: bool = Field(default_factory=list)
    PartsCap: int = Field(default_factory=list)
    Port: int = Field(default_factory=list)
    Secret: str = Field(default_factory=list)
    ServerOS: OnBoardMcuServerOS = Field(...)
    ServerStatus: int = Field(default_factory=list)
    TsActivated: datetime = Field(default_factory=list)
    TsCreated: datetime = Field(default_factory=list)
    Version: str = Field(default_factory=list)
    Zone: str = Field(default_factory=list)


class OutboundCall(Schema):
    Answered: bool = Field(default_factory=list)
    CallCost: Optional[Decimal] = Field(default=None)
    CallDuration: str = Field(default_factory=list)
    CallHistoryId: Optional[str] = Field(default=None)
    CdrId: str = Field(default_factory=list)
    DestinationCalleeId: Optional[str] = Field(default=None)
    DestinationDisplayName: Optional[str] = Field(default=None)
    DestinationDn: Optional[str] = Field(default=None)
    QualityReport: Optional[bool] = Field(default=None)
    RecordingId: Optional[int] = Field(default=None)
    RecordingUrl: Optional[str] = Field(default=None)
    RingingDuration: str = Field(default_factory=list)
    RuleName: Optional[str] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)
    SourceCallerId: Optional[str] = Field(default=None)
    SourceDisplayName: Optional[str] = Field(default=None)
    SourceDn: Optional[str] = Field(default=None)
    StartTime: datetime = Field(default_factory=list)
    Status: Optional[str] = Field(default=None)
    Summary: Optional[str] = Field(default=None)
    TalkingDuration: str = Field(default_factory=list)
    Transcription: Optional[str] = Field(default=None)
    TrunkName: Optional[str] = Field(default=None)
    TrunkNumber: Optional[str] = Field(default=None)


class OutboundCallCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[OutboundCall] = Field(default_factory=list)


class OutboundRoute(Schema):
    Append: Optional[str] = Field(default=None)
    CallerID: Optional[str] = Field(default=None)
    Prepend: Optional[str] = Field(default=None)
    StripDigits: Optional[int] = Field(default=None)
    TrunkId: Optional[int] = Field(default=None)
    TrunkName: Optional[str] = Field(default=None)


class OutboundRouteCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[OutboundRoute] = Field(default_factory=list)


class OutboundRule(Schema):
    DNRanges: list[DNRange] = Field(default_factory=list)
    EmergencyRule: Optional[bool] = Field(default=None)
    GroupIds: list[int] = Field(default_factory=list)
    GroupNames: list[str] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    NumberLengthRanges: Optional[str] = Field(default=None)
    Prefix: Optional[str] = Field(default=None)
    Priority: Optional[int] = Field(default=None)
    Routes: list[OutboundRoute] = Field(default_factory=list)


class OutboundRuleCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[OutboundRule] = Field(default_factory=list)


class Parameter(Schema):
    Description: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    Value: Optional[str] = Field(default=None)


class ParameterCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Parameter] = Field(default_factory=list)


class ParticipantDetails(Schema):
    email: str = Field(default_factory=list)
    key: str = Field(default_factory=list)
    moderator: Optional[int] = Field(default=None)
    name: str = Field(default_factory=list)
    pbx_extension: Optional[str] = Field(default=None)


class MeetingObj(Schema):
    documentlist: Optional[str] = Field(default=None)
    friendlyname: Optional[str] = Field(default=None)
    logo: str = Field(default_factory=list)
    meetingid: str = Field(default_factory=list)
    meetingprofile: Optional[str] = Field(default=None)
    openlink: str = Field(default_factory=list)
    organizer: ParticipantDetails = Field(...)
    params: MeetingParams = Field(...)
    participants: list[ParticipantDetails] = Field(default_factory=list)
    theme: str = Field(default_factory=list)


class OnBoardMeeting(Schema):
    McuFqdn: str = Field(default_factory=list)
    Meeting: MeetingObj = Field(...)
    MeetingId: str = Field(default_factory=list)
    Parts: list[KeyValuePair_2OfString_OnBoardConnectedParticipant] = Field(default_factory=list)
    Profile: str = Field(default_factory=list)
    Recorded: bool = Field(default_factory=list)
    Sessionid: str = Field(default_factory=list)
    Start: datetime = Field(default_factory=list)


class ParticipantDetailsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ParticipantDetails] = Field(default_factory=list)


class PbxToM365Binding(Schema):
    From: Optional[SynchronizedPbxProfile] = Field(default=None)
    To: Optional[SynchronizedM365Profile] = Field(default=None)


class PbxToM365BindingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PbxToM365Binding] = Field(default_factory=list)


class PeerGroup(Schema):
    GroupID: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    RoleName: Optional[str] = Field(default=None)


class Peer(Schema):
    Hidden: Optional[bool] = Field(default=None)
    Id: int = Field(default_factory=list)
    MemberOf: list[PeerGroup] = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    Tags: list[UserTag] = Field(default_factory=list)
    Type: Optional[PeerType] = Field(default=None)


class EmergencyNotificationsSettings(Schema):
    ChatRecipients: Optional[ChatRecipientsType] = Field(default=None)
    EmergencyDNPrompt: Optional[Peer] = Field(default=None)
    EmergencyPlayPrompt: Optional[str] = Field(default=None)
    SpecifiedList: Optional[str] = Field(default=None)


class PeerCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Peer] = Field(default_factory=list)


class PeerGroupCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PeerGroup] = Field(default_factory=list)


class Period(Schema):
    day_of_week: Optional[DayOfWeek] = Field(default=None, alias="DayOfWeek")
    Start: Optional[str] = Field(default=None)
    Stop: Optional[str] = Field(default=None)


class PeriodCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Period] = Field(default_factory=list)


class PhoneBookSettings(Schema):
    PhoneBookAddQueueName: Optional[TypeOfPhoneBookAddQueueName] = Field(default=None)
    PhoneBookDisplay: Optional[TypeOfPhoneBookDisplay] = Field(default=None)
    ResolvingLength: Optional[int] = Field(default=None)
    ResolvingType: Optional[TypeOfPhoneBookResolving] = Field(default=None)


class PhoneDeviceVlanInfo(Schema):
    Configurable: Optional[bool] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    Priority: Optional[int] = Field(default=None)
    PriorityConfigurable: Optional[bool] = Field(default=None)
    PriorityMax: Optional[int] = Field(default=None)
    PriorityMin: Optional[int] = Field(default=None)
    Type: Optional[PhoneDeviceVlanType] = Field(default=None)
    VlanId: Optional[int] = Field(default=None)
    VlanIdMax: Optional[int] = Field(default=None)
    VlanIdMin: Optional[int] = Field(default=None)


class PhoneDeviceVlanInfoCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PhoneDeviceVlanInfo] = Field(default_factory=list)


class PhoneLldpInfo(Schema):
    Configurable: Optional[bool] = Field(default=None)
    Value: Optional[bool] = Field(default=None)


class PhoneLogo(Schema):
    DisplayName: Optional[str] = Field(default=None)
    Filename: str = Field(default_factory=list)


class PhoneLogoCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PhoneLogo] = Field(default_factory=list)


class PhoneModel(Schema):
    AddAllowed: Optional[bool] = Field(default=None)
    CanBeSBC: Optional[bool] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    URL: Optional[str] = Field(default=None)
    UserAgent: Optional[str] = Field(default=None)


class PhoneModelCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PhoneModel] = Field(default_factory=list)


class PhoneRegistrar(Schema):
    Capabilities: Optional[int] = Field(default=None)
    FirmwareAvailable: Optional[str] = Field(default=None)
    FirmwareVersion: Optional[str] = Field(default=None)
    InterfaceLink: Optional[str] = Field(default=None)
    IpAddress: Optional[str] = Field(default=None)
    MAC: Optional[str] = Field(default=None)
    Model: Optional[str] = Field(default=None)
    UserAgent: Optional[str] = Field(default=None)
    Vendor: Optional[str] = Field(default=None)


class PhoneSettings(Schema):
    AllowCustomQueueRingtones: Optional[bool] = Field(default=None)
    Backlight: Optional[str] = Field(default=None)
    Codecs: list[str] = Field(default_factory=list)
    CustomLogo: Optional[str] = Field(default=None)
    CustomQueueRingtones: list[CustomQueueRingtone] = Field(default_factory=list)
    DateFormat: Optional[str] = Field(default=None)
    firmware: Optional[str] = Field(default=None, alias="Firmware")
    FirmwareLang: Optional[str] = Field(default=None)
    IsLogoCustomizable: Optional[bool] = Field(default=None)
    IsSBC: Optional[bool] = Field(default=None)
    LlDpInfo: Optional[PhoneLldpInfo] = Field(default=None)
    LocalRTPPortEnd: Optional[int] = Field(default=None)
    LocalRTPPortStart: Optional[int] = Field(default=None)
    LocalSipPort: Optional[int] = Field(default=None)
    LogoDescription: Optional[str] = Field(default=None)
    LogoFileExtensionAllowed: list[str] = Field(default_factory=list)
    OwnBlfs: Optional[bool] = Field(default=None)
    PhoneLanguage: Optional[str] = Field(default=None)
    PowerLed: Optional[str] = Field(default=None)
    ProvisionExtendedData: Optional[str] = Field(default=None)
    ProvisionType: Optional[ProvType] = Field(default=None)
    QueueRingTone: Optional[str] = Field(default=None)
    RemoteSpmHost: Optional[str] = Field(default=None)
    RemoteSpmPort: Optional[int] = Field(default=None)
    RingTone: Optional[str] = Field(default=None)
    SbcName: Optional[str] = Field(default=None)
    ScreenSaver: Optional[str] = Field(default=None)
    Secret: Optional[str] = Field(default=None)
    Srtp: Optional[str] = Field(default=None)
    TimeFormat: Optional[str] = Field(default=None)
    TimeZone: Optional[str] = Field(default=None)
    VlanInfos: list[PhoneDeviceVlanInfo] = Field(default_factory=list)
    XferType: Optional[XferTypeEnum] = Field(default=None)


class Phone(Schema):
    Id: int = Field(default_factory=list)
    Interface: Optional[str] = Field(default=None)
    MacAddress: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    ProvisioningLinkExt: Optional[str] = Field(default=None)
    ProvisioningLinkLocal: Optional[str] = Field(default=None)
    Settings: Optional[PhoneSettings] = Field(default=None)
    TemplateName: Optional[str] = Field(default=None)


class PhoneCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Phone] = Field(default_factory=list)


class PhoneTemplate(Schema):
    AddAllowed: Optional[bool] = Field(default=None)
    AllowedNetConfigs: list[str] = Field(default_factory=list)
    AllowSSLProvisioning: Optional[bool] = Field(default=None)
    BacklightTimeouts: list[str] = Field(default_factory=list)
    Codecs: list[str] = Field(default_factory=list)
    Content: Optional[str] = Field(default=None)
    DateFormats: list[str] = Field(default_factory=list)
    DefaultQueueRingTone: Optional[str] = Field(default=None)
    HotdeskingAllowed: Optional[bool] = Field(default=None)
    Id: str = Field(default_factory=list)
    IsCustom: Optional[bool] = Field(default=None)
    Languages: list[str] = Field(default_factory=list)
    MaxQueueCustomRingtones: Optional[int] = Field(default=None)
    Models: list[PhoneModel] = Field(default_factory=list)
    PowerLedSettings: list[str] = Field(default_factory=list)
    QueueRingTones: list[str] = Field(default_factory=list)
    RingTones: list[str] = Field(default_factory=list)
    RpsEnabled: Optional[bool] = Field(default=None)
    ScreenSaverTimeouts: list[str] = Field(default_factory=list)
    template_type: Optional[TemplateType] = Field(default=None, alias="TemplateType")
    TimeFormats: list[str] = Field(default_factory=list)
    TimeZones: list[str] = Field(default_factory=list)
    URL: Optional[str] = Field(default=None)
    XferTypeEnabled: Optional[bool] = Field(default=None)


class PhoneTemplateCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PhoneTemplate] = Field(default_factory=list)


class PhonesSettings(Schema):
    AllowMultiQueueRingtones: Optional[bool] = Field(default=None)
    AutoCleanupFirmware: Optional[bool] = Field(default=None)
    CustomDNDProfile: Optional[str] = Field(default=None)
    FanvilUpdateInterval: Optional[int] = Field(default=None)
    GrandstreamUpdateInterval: Optional[int] = Field(default=None)
    PhoneAllowMultiFirmwares: Optional[bool] = Field(default=None)
    SnomUpdateInterval: Optional[int] = Field(default=None)
    UseProvisioningSecret: Optional[bool] = Field(default=None)
    UseRpcForLocalPhones: Optional[bool] = Field(default=None)
    YealinkUpdateInterval: Optional[int] = Field(default=None)


class Playlist(Schema):
    AutoGain: Optional[bool] = Field(default=None)
    Files: list[str] = Field(default_factory=list)
    MaxVolumePercent: Optional[int] = Field(default=None)
    Name: str = Field(default_factory=list)
    PromptName: Optional[str] = Field(default=None)
    RepositoryPath: Optional[str] = Field(default=None)
    Shuffle: Optional[bool] = Field(default=None)


class PlaylistCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Playlist] = Field(default_factory=list)


class Prompt(Schema):
    Filename: Optional[str] = Field(default=None)
    Id: str = Field(default_factory=list)
    Transcription: Optional[str] = Field(default=None)


class PromptCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Prompt] = Field(default_factory=list)


class PromptSet(Schema):
    CultureCode: Optional[str] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    Folder: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    LanguageCode: Optional[str] = Field(default=None)
    Prompts: list[Prompt] = Field(default_factory=list)
    PromptSetName: Optional[str] = Field(default=None)
    prompt_set_type: Optional[PromptSetType] = Field(default=None, alias="PromptSetType")
    UseAlternateNumberPronunciation: Optional[bool] = Field(default=None)
    Version: Optional[str] = Field(default=None)


class PromptSetCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[PromptSet] = Field(default_factory=list)


class Property(Schema):
    Description: Optional[str] = Field(default=None)
    Name: str = Field(default_factory=list)
    Value: str = Field(default_factory=list)


class PropertyCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Property] = Field(default_factory=list)


class PurgeSettings(Schema):
    All: bool = Field(default_factory=list)
    Start: Optional[datetime] = Field(default=None)
    Stop: Optional[datetime] = Field(default=None)


class QualityParty(Schema):
    AddressStr: Optional[str] = Field(default=None)
    Burst: Optional[int] = Field(default=None)
    codec: Optional[str] = Field(default=None, alias="Codec")
    Duration: Optional[int] = Field(default=None)
    GlobalPort: Optional[int] = Field(default=None)
    Inbound: Optional[bool] = Field(default=None)
    LocalPort: Optional[int] = Field(default=None)
    Location: Optional[str] = Field(default=None)
    MOSFromPBX: Optional[float | str | ReferenceNumeric] = Field(default=None)
    MOSToPBX: Optional[float | str | ReferenceNumeric] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    RTT: Optional[float | str | ReferenceNumeric] = Field(default=None)
    RxJitter: Optional[float | str | ReferenceNumeric] = Field(default=None)
    RxLost: Optional[float | str | ReferenceNumeric] = Field(default=None)
    RxPackets: Optional[int] = Field(default=None)
    TunAddressStr: Optional[str] = Field(default=None)
    TxBursts: Optional[int] = Field(default=None)
    TxJitter: Optional[float | str | ReferenceNumeric] = Field(default=None)
    TxLost: Optional[float | str | ReferenceNumeric] = Field(default=None)
    TxPackets: Optional[int] = Field(default=None)
    UserAgent: Optional[str] = Field(default=None)


class QualityReport(Schema):
    MOS: Optional[float | str | ReferenceNumeric] = Field(default=None)
    OverallScore: Optional[int] = Field(default=None)
    Party1: Optional[QualityParty] = Field(default=None)
    Party2: Optional[QualityParty] = Field(default=None)
    Reason: Optional[str] = Field(default=None)
    Summary: Optional[int] = Field(default=None)
    Transcoding: Optional[bool] = Field(default=None)


class QueueAgent(Schema):
    Id: Optional[int] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: str = Field(default_factory=list)
    SkillGroup: Optional[str] = Field(default=None)


class QueueAgentCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueAgent] = Field(default_factory=list)


class QueueAgentsChatStatistics(Schema):
    AnsweredCount: Optional[int] = Field(default=None)
    DealtWithCount: Optional[int] = Field(default=None)
    Dn: str = Field(default_factory=list)
    DnDisplayName: Optional[str] = Field(default=None)
    Queue: str = Field(default_factory=list)
    QueueDisplayName: Optional[str] = Field(default=None)
    SortOrder: Optional[int] = Field(default=None)


class QueueAgentsChatStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueAgentsChatStatistics] = Field(default_factory=list)


class QueueAgentsChatStatisticsTotals(Schema):
    AnsweredCount: Optional[int] = Field(default=None)
    DealtWithCount: Optional[int] = Field(default=None)
    Queue: str = Field(default_factory=list)
    QueueDisplayName: Optional[str] = Field(default=None)


class QueueAgentsChatStatisticsTotalsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueAgentsChatStatisticsTotals] = Field(default_factory=list)


class QueueAnsweredCallsByWaitTime(Schema):
    AnsweredTime: datetime = Field(default_factory=list)
    CallTime: datetime = Field(default_factory=list)
    destination: str = Field(default_factory=list, alias="Destination")
    Dn: str = Field(default_factory=list)
    DnNumber: Optional[str] = Field(default=None)
    RingTime: Optional[str] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)
    Source: str = Field(default_factory=list)


class QueueAnsweredCallsByWaitTimeCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueAnsweredCallsByWaitTime] = Field(default_factory=list)


class QueueCallbacks(Schema):
    CallbacksCount: Optional[int] = Field(default=None)
    Dn: Optional[str] = Field(default=None)
    FailCallbacksCount: Optional[int] = Field(default=None)
    QueueDnNumber: str = Field(default_factory=list)
    ReceivedCount: Optional[int] = Field(default=None)


class QueueCallbacksCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueCallbacks] = Field(default_factory=list)


class QueueChatPerformance(Schema):
    AbandonedCount: Optional[int] = Field(default=None)
    AnsweredCount: Optional[int] = Field(default=None)
    IncomingCount: Optional[int] = Field(default=None)
    QuantityAgents: Optional[int] = Field(default=None)
    Queue: str = Field(default_factory=list)
    QueueDisplayName: Optional[str] = Field(default=None)


class QueueChatPerformanceCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueChatPerformance] = Field(default_factory=list)


class QueueFailedCallbacks(Schema):
    CallbackNo: str = Field(default_factory=list)
    CallTime: datetime = Field(default_factory=list)
    Dn: str = Field(default_factory=list)
    QueueDnNumber: Optional[str] = Field(default=None)
    RingTime: Optional[str] = Field(default=None)


class QueueFailedCallbacksCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueFailedCallbacks] = Field(default_factory=list)


class QueueManager(Schema):
    Id: Optional[int] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: str = Field(default_factory=list)


class QueueManagerCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueueManager] = Field(default_factory=list)


class QueuePerformanceOverview(Schema):
    ExtensionAnsweredCount: Optional[int] = Field(default=None)
    ExtensionDisplayName: Optional[str] = Field(default=None)
    ExtensionDn: str = Field(default_factory=list)
    ExtensionDroppedCount: Optional[int] = Field(default=None)
    QueueAnsweredCount: Optional[int] = Field(default=None)
    QueueDisplayName: str = Field(default_factory=list)
    QueueDn: Optional[str] = Field(default=None)
    QueueReceivedCount: Optional[int] = Field(default=None)
    SortOrder: Optional[int] = Field(default=None)
    TalkTime: Optional[str] = Field(default=None)


class QueuePerformanceOverviewCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueuePerformanceOverview] = Field(default_factory=list)


class QueuePerformanceTotals(Schema):
    ExtensionAnsweredCount: Optional[int] = Field(default=None)
    ExtensionDroppedCount: Optional[int] = Field(default=None)
    QueueDisplayName: Optional[str] = Field(default=None)
    QueueDn: str = Field(default_factory=list)
    QueueReceivedCount: Optional[int] = Field(default=None)


class QueuePerformanceTotalsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[QueuePerformanceTotals] = Field(default_factory=list)


class ReceptionistForward(Schema):
    CustomData: Optional[str] = Field(default=None)
    ForwardDN: Optional[str] = Field(default=None)
    ForwardType: IVRForwardType = Field(...)
    Id: int = Field(default_factory=list)
    Input: Optional[str] = Field(default=None)
    peer_type: Optional[PeerType] = Field(default=None, alias="PeerType")


class ReceptionistForwardCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ReceptionistForward] = Field(default_factory=list)


class Recording(Schema):
    ArchivedUrl: Optional[str] = Field(default=None)
    CallType: Optional[RecordingCallType] = Field(default=None)
    EndTime: Optional[datetime] = Field(default=None)
    FromCallerNumber: Optional[str] = Field(default=None)
    FromCrmContact: Optional[str] = Field(default=None)
    FromDidNumber: Optional[str] = Field(default=None)
    FromDisplayName: Optional[str] = Field(default=None)
    FromDn: Optional[str] = Field(default=None)
    FromDnType: Optional[int] = Field(default=None)
    FromIdParticipant: Optional[int] = Field(default=None)
    Id: int = Field(default_factory=list)
    IsArchived: Optional[bool] = Field(default=None)
    RecordingUrl: Optional[str] = Field(default=None)
    RefParticipantId: Optional[int] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)
    StartTime: Optional[datetime] = Field(default=None)
    Summary: Optional[str] = Field(default=None)
    ToCallerNumber: Optional[str] = Field(default=None)
    ToCrmContact: Optional[str] = Field(default=None)
    ToDidNumber: Optional[str] = Field(default=None)
    ToDisplayName: Optional[str] = Field(default=None)
    ToDn: Optional[str] = Field(default=None)
    ToDnType: Optional[int] = Field(default=None)
    ToIdParticipant: Optional[int] = Field(default=None)
    Transcription: Optional[str] = Field(default=None)


class RecordingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Recording] = Field(default_factory=list)


class RecordingRepositorySettings(Schema):
    AutoDeleteRecordingDays: Optional[int] = Field(default=None)
    AutoDeleteRecordingEnabled: Optional[bool] = Field(default=None)
    IsRecordingArchiveEnabled: Optional[bool] = Field(default=None)
    RecordingDiskSpace: Optional[int] = Field(default=None)
    RecordingPath: Optional[str] = Field(default=None)
    RecordingsQuota: Optional[int] = Field(default=None)
    RecordingUsedSpace: Optional[int] = Field(default=None)


class ReferenceCreate(Schema):
    id: str = Field(default_factory=list, alias="@odata.id")


class ReferenceUpdate(Schema):
    id: str = Field(default_factory=list, alias="@odata.id")
    type: Optional[str] = Field(default=None, alias="@odata.type")


class RefreshToken(Schema):
    Created: datetime = Field(default_factory=list)
    CreatedByIp: str = Field(default_factory=list)
    CreatedByUserAgent: str = Field(default_factory=list)
    DisplayName: Optional[str] = Field(default=None)
    Expires: datetime = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    login_type: LoginType = Field(..., alias="LoginType")
    ReasonRevoked: Optional[RevokeReason] = Field(default=None)
    Revoked: Optional[datetime] = Field(default=None)
    RevokedByIp: Optional[str] = Field(default=None)
    SlidingExpiration: bool = Field(default_factory=list)
    Token: str = Field(default_factory=list)
    Used: datetime = Field(default_factory=list)
    UsedByIp: str = Field(default_factory=list)
    UsedByUserAgent: str = Field(default_factory=list)
    Username: str = Field(default_factory=list)


class RefreshTokenCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[RefreshToken] = Field(default_factory=list)


class RegenerateOptions(Schema):
    ConfigurationLink: bool = Field(default_factory=list)
    DeskphonePassword: bool = Field(default_factory=list)
    RpsKey: bool = Field(default_factory=list)
    SendWelcomeEmail: bool = Field(default_factory=list)
    SipAuth: bool = Field(default_factory=list)
    VoicemailPIN: bool = Field(default_factory=list)
    WebclientPassword: bool = Field(default_factory=list)


class RegenerateRequestBody(Schema):
    opts: RegenerateOptions = Field(...)


class RegistrarFxs(Schema):
    InterfaceLink: str = Field(default_factory=list)
    MacAddress: str = Field(default_factory=list)


class RegistrarFxsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[RegistrarFxs] = Field(default_factory=list)


class RemoteArchivingSettings(Schema):
    backups: Optional[ArchiveSubsystem] = Field(default=None, alias="Backups")
    Chats: Optional[ArchiveSubsystem] = Field(default=None)
    Faxes: Optional[ArchiveSubsystem] = Field(default=None)
    Id: int = Field(default_factory=list)
    Location: Optional[LocationSettings] = Field(default=None)
    Recordings: Optional[ArchiveSubsystem] = Field(default=None)
    Voicemails: Optional[ArchiveSubsystem] = Field(default=None)


class RemotePostgreConfig(Schema):
    authenticate_mode: Optional[AuthenticateMode] = Field(default=None, alias="AuthenticateMode")
    CACertificate: Optional[ConcealedDataFile] = Field(default=None)
    ClientCertificate: Optional[ConcealedDataFile] = Field(default=None)
    Database: Optional[str] = Field(default=None)
    Host: Optional[str] = Field(default=None)
    Password: Optional[ConcealedPassword] = Field(default=None)
    Port: Optional[int] = Field(default=None)
    server_trust_mode: Optional[ServerTrustMode] = Field(default=None, alias="ServerTrustMode")
    Username: Optional[str] = Field(default=None)


class DataConnectorSettings(Schema):
    IsBigQueryEnabled: Optional[bool] = Field(default=None)
    offload_destination: Optional[OffloadDestination] = Field(default=None, alias="OffloadDestination")
    PurgeAfterSync: Optional[bool] = Field(default=None)
    remote_postgre_config: Optional[RemotePostgreConfig] = Field(default=None, alias="RemotePostgreConfig")
    Schedule: Optional[BackupSchedule] = Field(default=None)


class ReplaceMyGroupLicenseKeyRequestBody(Schema):
    licenseKey: str = Field(default_factory=list)


class ReportExtensionStatisticsByGroup(Schema):
    DisplayName: Optional[str] = Field(default=None)
    Dn: str = Field(default_factory=list)
    InboundAnsweredCount: Optional[int] = Field(default=None)
    InboundAnsweredTalkingDur: Optional[str] = Field(default=None)
    InboundUnansweredCount: Optional[int] = Field(default=None)
    OutboundAnsweredCount: Optional[int] = Field(default=None)
    OutboundAnsweredTalkingDur: Optional[str] = Field(default=None)
    OutboundUnansweredCount: Optional[int] = Field(default=None)
    SentimentScore: Optional[int] = Field(default=None)


class ReportExtensionStatisticsByGroupCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ReportExtensionStatisticsByGroup] = Field(default_factory=list)


class RequestHelp(Schema):
    GrantPeriodDays: Optional[int] = Field(default=None)
    IssueDescription: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    PhoneNumber: Optional[str] = Field(default=None)
    ReplyEmail: str = Field(default_factory=list)


class ResellerInfo(Schema):
    Id: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)


class ResetQueueStatisticsSchedule(Schema):
    Day: Optional[DayOfWeek] = Field(default=None)
    Frequency: Optional[ResetQueueStatisticsFrequency] = Field(default=None)
    Time: Optional[str] = Field(default=None)


class RestoreSettings(Schema):
    EncryptBackup: Optional[bool] = Field(default=None)
    EncryptBackupPassword: Optional[ConcealedPassword] = Field(default=None)
    Schedule: Optional[BackupSchedule] = Field(default=None)
    ScheduleEnabled: Optional[bool] = Field(default=None)


class Restrictions(Schema):
    Dects: Optional[EntityRestrictions] = Field(default=None)
    LiveChats: Optional[EntityRestrictions] = Field(default=None)
    MaxPrompts: Optional[int] = Field(default=None)
    Sbcs: Optional[EntityRestrictions] = Field(default=None)
    System: Optional[EntityRestrictions] = Field(default=None)
    Trunks: Optional[EntityRestrictions] = Field(default=None)
    Users: Optional[EntityRestrictions] = Field(default=None)


class RetreivePeersRequest(Schema):
    DnNumbers: list[str] = Field(default_factory=list)
    IsReportPeers: bool = Field(default_factory=list)


class Rights(Schema):
    AllowIVR: Optional[bool] = Field(default=None)
    AllowParking: Optional[bool] = Field(default=None)
    AllowToChangePresence: Optional[bool] = Field(default=None)
    AllowToManageCompanyBook: Optional[bool] = Field(default=None)
    AssignClearOperations: Optional[bool] = Field(default=None)
    CanBargeIn: Optional[bool] = Field(default=None)
    CanIntercom: Optional[bool] = Field(default=None)
    CanSeeGroupCalls: Optional[bool] = Field(default=None)
    CanSeeGroupMembers: Optional[bool] = Field(default=None)
    CanSeeGroupRecordings: Optional[bool] = Field(default=None)
    Invalid: Optional[bool] = Field(default=None)
    PerformOperations: Optional[bool] = Field(default=None)
    RoleName: str = Field(default_factory=list)
    ShowMyCalls: Optional[bool] = Field(default=None)
    ShowMyPresence: Optional[bool] = Field(default=None)
    ShowMyPresenceOutside: Optional[bool] = Field(default=None)


class RightsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Rights] = Field(default_factory=list)


class RingGroupMember(Schema):
    Id: int = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)


class RingGroupMemberCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[RingGroupMember] = Field(default_factory=list)


class RingGroupStatistics(Schema):
    RingGroupAnsweredCount: Optional[int] = Field(default=None)
    RingGroupDisplayName: Optional[str] = Field(default=None)
    RingGroupDn: str = Field(default_factory=list)
    RingGroupReceivedCount: Optional[int] = Field(default=None)
    RingGroupSentimentScore: Optional[int] = Field(default=None)


class RingGroupStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[RingGroupStatistics] = Field(default_factory=list)


class Route(Schema):
    IsPromptEnabled: Optional[bool] = Field(default=None)
    prompt: Optional[str] = Field(default=None, alias="Prompt")
    route: Optional[Destination] = Field(default=None, alias="Route")


class Sbc(Schema):
    DisplayName: str = Field(default_factory=list)
    Group: Optional[str] = Field(default=None)
    HasConnection: Optional[bool] = Field(default=None)
    LocalIPv4: Optional[str] = Field(default=None)
    Name: str = Field(default_factory=list)
    Password: str = Field(default_factory=list)
    PhoneMAC: Optional[str] = Field(default=None)
    PhoneUserId: Optional[int] = Field(default=None)
    ProvisionLink: Optional[str] = Field(default=None)
    PublicIP: Optional[str] = Field(default=None)
    Version: Optional[str] = Field(default=None)


class SbcCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Sbc] = Field(default_factory=list)


class Schedule(Schema):
    IgnoreHolidays: Optional[bool] = Field(default=None)
    Periods: list[Period] = Field(default_factory=list)
    Type: RuleHoursType = Field(...)


class ExtensionRule(Schema):
    CallerId: Optional[str] = Field(default=None)
    destination: Optional[Destination] = Field(default=None, alias="Destination")
    Hours: Optional[Schedule] = Field(default=None)
    Id: int = Field(default_factory=list)


class ExtensionRuleCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ExtensionRule] = Field(default_factory=list)


class InboundRule(Schema):
    AlterDestinationDuringHolidays: Optional[bool] = Field(default=None)
    AlterDestinationDuringOutOfOfficeHours: Optional[bool] = Field(default=None)
    CallType: Optional[RuleCallTypeType] = Field(default=None)
    Condition: Optional[RuleConditionType] = Field(default=None)
    CustomData: Optional[str] = Field(default=None)
    Data: Optional[str] = Field(default=None)
    HolidaysDestination: Optional[Destination] = Field(default=None)
    Hours: Optional[Schedule] = Field(default=None)
    Id: int = Field(default_factory=list)
    OfficeHoursDestination: Optional[Destination] = Field(default=None)
    OutOfOfficeHoursDestination: Optional[Destination] = Field(default=None)
    RuleName: Optional[str] = Field(default=None)
    TrunkDN: Optional[Peer] = Field(default=None)


class DidNumber(Schema):
    Number: str = Field(default_factory=list)
    RoutingRule: Optional[InboundRule] = Field(default=None)
    TemplateFileName: Optional[str] = Field(default=None)
    TrunkId: int = Field(default_factory=list)


class DidNumberCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[DidNumber] = Field(default_factory=list)


class InboundRuleCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[InboundRule] = Field(default_factory=list)


class OfficeHours(Schema):
    BreakTime: Optional[Schedule] = Field(default=None)
    Hours: Optional[Schedule] = Field(default=None)
    OfficeHolidays: list[Holiday] = Field(default_factory=list)
    SystemLanguage: Optional[str] = Field(default=None)
    TimeZoneId: Optional[str] = Field(default=None)


class ScheduledReport(Schema):
    DN: str = Field(default_factory=list)
    EmailAddresses: str = Field(default_factory=list)
    FilterDescription: str = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    ReportLink: str = Field(default_factory=list)
    ReportParams: str = Field(default_factory=list)
    ReportType: ScheduledReportType = Field(...)
    schedule_type: ReportScheduleType = Field(..., alias="ScheduleType")


class ScheduledReportCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ScheduledReport] = Field(default_factory=list)


class SecureSipSettings(Schema):
    Certificate: Optional[ConcealedDataFile] = Field(default=None)
    PrivateKey: Optional[ConcealedDataFile] = Field(default=None)


class ServiceInfo(Schema):
    CpuUsage: Optional[int] = Field(default=None)
    DisplayName: Optional[str] = Field(default=None)
    HandleCount: Optional[int] = Field(default=None)
    MemoryUsed: Optional[int] = Field(default=None)
    Name: str = Field(default_factory=list)
    RestartEnabled: Optional[bool] = Field(default=None)
    StartStopEnabled: Optional[bool] = Field(default=None)
    Status: Optional[ServiceStatus] = Field(default=None)
    ThreadCount: Optional[int] = Field(default=None)


class ServiceInfoCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ServiceInfo] = Field(default_factory=list)


class SetMonitorStatusRequestBody(Schema):
    days: int = Field(default_factory=list)


class SetRoute(Schema):
    DID: str = Field(default_factory=list)
    DisplayName: Optional[str] = Field(default=None)
    TrunkId: int = Field(default_factory=list)


class SetRouteCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[SetRoute] = Field(default_factory=list)


class SetRouteRequest(Schema):
    Id: int = Field(default_factory=list)
    Routes: list[SetRoute] = Field(default_factory=list)


class SipDevice(Schema):
    DN: Optional[Peer] = Field(default=None)
    Id: int = Field(default_factory=list)
    PhoneWebPassword: Optional[str] = Field(default=None)
    ProvLink: Optional[str] = Field(default=None)
    Registrar: Optional[PhoneRegistrar] = Field(default=None)


class SipDeviceCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[SipDevice] = Field(default_factory=list)


class StatisticSla(Schema):
    BadSlaCallsCount: Optional[int] = Field(default=None)
    Dn: Optional[str] = Field(default=None)
    QueueDnNumber: str = Field(default_factory=list)
    ReceivedCount: Optional[int] = Field(default=None)


class StatisticSlaCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[StatisticSla] = Field(default_factory=list)


class StatusSyncConfiguration(Schema):
    M365ToPbxBindings: list[M365ToPbxBinding] = Field(default_factory=list)
    PBXToM365Bindings: list[PbxToM365Binding] = Field(default_factory=list)
    PBXToM365Busy: Optional[bool] = Field(default=None)


class ADUsersSyncConfiguration(Schema):
    EnableSSO: Optional[bool] = Field(default=None)
    IsEnabled: Optional[bool] = Field(default=None)
    IsSyncDepartments: Optional[bool] = Field(default=None)
    IsSyncDetails: Optional[bool] = Field(default=None)
    IsSyncOfficePhone: Optional[bool] = Field(default=None)
    IsSyncPhoto: Optional[bool] = Field(default=None)
    SelectedUsers: list[str] = Field(default_factory=list)
    SetTeamsPresence: Optional[bool] = Field(default=None)
    StartingExtensionNumber: str = Field(default_factory=list)
    status_sync_configuration: Optional[StatusSyncConfiguration] = Field(default=None, alias="StatusSyncConfiguration")
    SyncEvents: Optional[bool] = Field(default=None)
    SyncGuestUsers: Optional[bool] = Field(default=None)
    SyncPersonalContacts: Optional[bool] = Field(default=None)
    SyncType: Optional[IntegrationSyncType] = Field(default=None)


class StringCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[str] = Field(default_factory=list)


class SystemDatabaseInformation(Schema):
    CallsUsedSpace: Optional[int] = Field(default=None)
    ChatFilesCount: Optional[int] = Field(default=None)
    ChatsUsedSpace: Optional[int] = Field(default=None)
    EventLogUsedSpace: Optional[int] = Field(default=None)
    Id: Optional[int] = Field(default=None)


class SystemDirectory(Schema):
    Dirs: list[str] = Field(default_factory=list)
    Path: Optional[str] = Field(default=None)


class SystemExtensionStatus(Schema):
    IsRegistered: Optional[bool] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    Type: Optional[str] = Field(default=None)


class SystemHealthStatus(Schema):
    CustomTemplatesCount: Optional[int] = Field(default=None)
    Firewall: Optional[bool] = Field(default=None)
    Id: Optional[int] = Field(default=None)
    Phones: Optional[bool] = Field(default=None)
    Trunks: Optional[bool] = Field(default=None)
    UnsupportedFirmwaresCount: Optional[int] = Field(default=None)


class SystemParameters(Schema):
    Custom1Name: Optional[str] = Field(default=None)
    Custom2Name: Optional[str] = Field(default=None)
    EmRuleCreationAllowed: Optional[bool] = Field(default=None)
    ENL: Optional[int] = Field(default=None)
    FirstExternalPort: Optional[int] = Field(default=None)
    FQDN: Optional[str] = Field(default=None)
    GlobalACPRMSET: Optional[str] = Field(default=None)
    GlobalLanguage: Optional[str] = Field(default=None)
    HttpPort: Optional[int] = Field(default=None)
    HttpsPort: Optional[int] = Field(default=None)
    IpV6: Optional[str] = Field(default=None)
    Is3CXFQDN: Optional[bool] = Field(default=None)
    IsChatLogEnabled: Optional[bool] = Field(default=None)
    IsHosted: Optional[bool] = Field(default=None)
    IsHosted3CX: Optional[bool] = Field(default=None)
    IsMulticompanyMode: Optional[bool] = Field(default=None)
    IsRemoteBackup: Optional[bool] = Field(default=None)
    IsStaticIp: Optional[bool] = Field(default=None)
    IsTranscriptionEnabled: Optional[bool] = Field(default=None)
    license: Optional[License] = Field(default=None, alias="License")
    MaxDIDPerTrunk: Optional[int] = Field(default=None)
    PbxExternalHost: Optional[str] = Field(default=None)
    RpsEnabled: Optional[bool] = Field(default=None)
    SipPort: Optional[int] = Field(default=None)
    SipsPort: Optional[int] = Field(default=None)
    StaticIp: Optional[str] = Field(default=None)
    StunIp: Optional[str] = Field(default=None)
    TunnnelPort: Optional[int] = Field(default=None)
    Version: Optional[str] = Field(default=None)
    WebrtcLastPort: Optional[int] = Field(default=None)


class SystemStatus(Schema):
    Activated: Optional[bool] = Field(default=None)
    AutoUpdateEnabled: Optional[bool] = Field(default=None)
    AvailableLocalIps: Optional[str] = Field(default=None)
    BackupScheduled: Optional[bool] = Field(default=None)
    CallsActive: Optional[int] = Field(default=None)
    ChatUsedSpace: Optional[int] = Field(default=None)
    CurrentLocalIp: Optional[str] = Field(default=None)
    DBMaintenanceInProgress: Optional[bool] = Field(default=None)
    DiskUsage: Optional[int] = Field(default=None)
    ExpirationDate: Optional[datetime] = Field(default=None)
    ExtensionsRegistered: Optional[int] = Field(default=None)
    ExtensionsTotal: Optional[int] = Field(default=None)
    FQDN: Optional[str] = Field(default=None)
    FreeDiskSpace: Optional[int] = Field(default=None)
    HasNotRunningServices: Optional[bool] = Field(default=None)
    HasUnregisteredSystemExtensions: Optional[bool] = Field(default=None)
    Id: int = Field(default_factory=list)
    Ip: Optional[str] = Field(default=None)
    IpV4: Optional[str] = Field(default=None)
    IpV6: Optional[str] = Field(default=None)
    IsAuditLogEnabled: Optional[bool] = Field(default=None)
    IsChatLogEnabled: Optional[bool] = Field(default=None)
    IsRecordingArchiveEnabled: Optional[bool] = Field(default=None)
    LastBackupDateTime: Optional[datetime] = Field(default=None)
    LastCheckForUpdates: Optional[datetime] = Field(default=None)
    LastSuccessfulUpdate: Optional[datetime] = Field(default=None)
    LicenseActive: Optional[bool] = Field(default=None)
    LicenseKey: Optional[str] = Field(default=None)
    LocalIpValid: Optional[bool] = Field(default=None)
    LogUsedSpace: Optional[int] = Field(default=None)
    MaintenanceExpiresAt: Optional[datetime] = Field(default=None)
    MaxSimCalls: Optional[int] = Field(default=None)
    OS: Optional[XOperatingSystemType] = Field(default=None)
    OutboundRules: Optional[int] = Field(default=None)
    ProductCode: Optional[str] = Field(default=None)
    RecordingQuota: Optional[int] = Field(default=None)
    RecordingQuotaReached: Optional[bool] = Field(default=None)
    RecordingStopped: Optional[bool] = Field(default=None)
    RecordingUsedSpace: Optional[int] = Field(default=None)
    RemoteConfigurationRequired: Optional[bool] = Field(default=None)
    RemoteStorageEnabled: Optional[bool] = Field(default=None)
    ResellerName: Optional[str] = Field(default=None)
    Support: Optional[bool] = Field(default=None)
    TotalDiskSpace: Optional[int] = Field(default=None)
    TrunksRegistered: Optional[int] = Field(default=None)
    TrunksTotal: Optional[int] = Field(default=None)
    Version: Optional[str] = Field(default=None)
    VoicemailQuotaReached: Optional[bool] = Field(default=None)
    VoicemailStopped: Optional[bool] = Field(default=None)


class TeamQueueGeneralStatistics(Schema):
    AgentsInQueueCount: Optional[int] = Field(default=None)
    AnsweredCount: Optional[int] = Field(default=None)
    AvgTalkTime: Optional[str] = Field(default=None)
    Dn: Optional[str] = Field(default=None)
    QueueDnNumber: str = Field(default_factory=list)
    ReceivedCount: Optional[int] = Field(default=None)
    TotalTalkTime: Optional[str] = Field(default=None)


class TeamQueueGeneralStatisticsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[TeamQueueGeneralStatistics] = Field(default_factory=list)


class TestCallLog(Schema):
    Entries: list[LogEntry] = Field(default_factory=list)


class TestResult(Schema):
    Error: Optional[str] = Field(default=None)
    Parameters: list[str] = Field(default_factory=list)
    Success: Optional[bool] = Field(default=None)


class TimeReportData(Schema):
    XValue: datetime = Field(default_factory=list)
    YValue1: Optional[int] = Field(default=None)
    YValue2: Optional[int] = Field(default=None)


class TimeReportDataCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[TimeReportData] = Field(default_factory=list)


class TimeZone(Schema):
    IanaName: str = Field(default_factory=list)
    Id: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    WindowsName: str = Field(default_factory=list)


class Defs(Schema):
    Codecs: list[Codec] = Field(default_factory=list)
    GatewayParameters: list[GatewayParameter] = Field(default_factory=list)
    GatewayParameterValues: list[GatewayParameterValue] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    TimeZones: list[TimeZone] = Field(default_factory=list)


class TimeZoneCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[TimeZone] = Field(default_factory=list)


class TrunkMessaging(Schema):
    Enabled: Optional[bool] = Field(default=None)
    NumberLength: Optional[int] = Field(default=None)
    NumberLengthEnabled: Optional[bool] = Field(default=None)
    Provider: Optional[str] = Field(default=None)
    Webhook: Optional[str] = Field(default=None)


class TrunkVariable(Schema):
    DefaultValue: Optional[str] = Field(default=None)
    MaxLength: Optional[int] = Field(default=None)
    MinLength: Optional[int] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Option: Optional[str] = Field(default=None)
    OptionType: Optional[TrunkVariableType] = Field(default=None)
    Pattern: Optional[str] = Field(default=None)
    prompt: Optional[str] = Field(default=None, alias="Prompt")
    Required: Optional[bool] = Field(default=None)
    Title: Optional[str] = Field(default=None)
    Validation: Optional[str] = Field(default=None)


class TrunkMessagingTemplate(Schema):
    MessagingVariables: list[TrunkVariable] = Field(default_factory=list)
    optional: Optional[bool] = Field(default=None, alias="Optional")
    Outbound: Optional[bool] = Field(default=None)
    Provider: Optional[str] = Field(default=None)
    Type: Optional[str] = Field(default=None)


class TrunkTemplate(Schema):
    AddAllowed: Optional[bool] = Field(default=None)
    Content: Optional[str] = Field(default=None)
    Countries: list[str] = Field(default_factory=list)
    DefaultProxyPort: Optional[int] = Field(default=None)
    DefaultRegistrarPort: Optional[int] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    Editors: list[TrunkEditorType] = Field(default_factory=list)
    Id: str = Field(default_factory=list)
    MessagingTemplate: Optional[TrunkMessagingTemplate] = Field(default=None)
    Name: str = Field(default_factory=list)
    Tags: list[str] = Field(default_factory=list)
    template_type: TemplateType = Field(..., alias="TemplateType")
    Url: Optional[str] = Field(default=None)


class TrunkTemplateCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[TrunkTemplate] = Field(default_factory=list)


class TrunkVariableCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[TrunkVariable] = Field(default_factory=list)


class TwilioPhoneNumber(Schema):
    FriendlyName: Optional[str] = Field(default=None)
    IsInTrunk: Optional[bool] = Field(default=None)
    IsMessagingEnabled: Optional[bool] = Field(default=None)
    PhoneNumber: Optional[str] = Field(default=None)
    Sid: str = Field(default_factory=list)


class AutoProvisionTrunk(Schema):
    AvailableNumbers: list[TwilioPhoneNumber] = Field(default_factory=list)


class TwilioPhoneNumberCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[TwilioPhoneNumber] = Field(default_factory=list)


class UpdateItem(Schema):
    Category: str = Field(default_factory=list)
    Description: str = Field(default_factory=list)
    DescriptionLink: str = Field(default_factory=list)
    Guid: Optional[UUID] = Field(default=None)
    Ignore: Optional[bool] = Field(default=None)
    Image: str = Field(default_factory=list)
    LocalVersion: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    OutOfDate: Optional[bool] = Field(default=None)
    ServerVersion: str = Field(default_factory=list)
    update_type: Optional[UpdateType] = Field(default=None, alias="UpdateType")


class UpdateItemCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[UpdateItem] = Field(default_factory=list)


class UpdateList(Schema):
    Entries: list[UpdateItem] = Field(default_factory=list)
    IsMaintananceExpired: Optional[bool] = Field(default=None)
    Key: Optional[UUID] = Field(default=None)
    LastSuccessfulUpdate: Optional[datetime] = Field(default=None)


class UpdateSettings(Schema):
    AutoUpdateEnabled: Optional[bool] = Field(default=None)
    schedule: Optional[BackupSchedule] = Field(default=None, alias="Schedule")


class UpdatesStats(Schema):
    PerPage: list[CategoryUpdate] = Field(default_factory=list)
    TcxUpdate: list[CategoryUpdate] = Field(default_factory=list)


class UserActivity(Schema):
    AnsweredCount: int = Field(default_factory=list)
    DateTimeInterval: datetime = Field(default_factory=list)
    UnansweredCount: int = Field(default_factory=list)


class UserActivityCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[UserActivity] = Field(default_factory=list)


class UserDeleteError(Schema):
    Error: Optional[str] = Field(default=None)
    ExtensionNumber: Optional[str] = Field(default=None)


class UserGroup(Schema):
    CanDelete: Optional[bool] = Field(default=None)
    GroupId: Optional[int] = Field(default=None)
    GroupRights: Optional[Rights] = Field(default=None)
    Id: Optional[int] = Field(default=None)
    MemberName: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    rights: Optional[Rights] = Field(default=None, alias="Rights")
    Tags: list[UserTag] = Field(default_factory=list)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    Type: Optional[PeerType] = Field(default=None)


class CreateTrunk(Schema):
    AccountSid: Optional[str] = Field(default=None)
    ApiKey: Optional[str] = Field(default=None)
    DefaultRule: Optional[InboundRule] = Field(default=None)
    Groups: list[UserGroup] = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    PhoneNumbers: list[TwilioPhoneNumber] = Field(default_factory=list)
    Type: Optional[TrunkType] = Field(default=None)


class Fax(Schema):
    AuthID: Optional[str] = Field(default=None)
    AuthPassword: Optional[str] = Field(default=None)
    FaxServer: Optional[bool] = Field(default=None)
    Groups: list[UserGroup] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    Number: Optional[str] = Field(default=None)
    OutboundCallerId: Optional[str] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)


class FaxCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Fax] = Field(default_factory=list)


class Group(Schema):
    AllowCallService: Optional[bool] = Field(default=None)
    AnswerAfter: Optional[int] = Field(default=None)
    BreakRoute: Optional[Route] = Field(default=None)
    BreakTime: Optional[Schedule] = Field(default=None)
    CallHandlingMode: list[CallHandlingFlags] = Field(default_factory=list)
    CallUsEnableChat: Optional[bool] = Field(default=None)
    CallUsEnablePhone: Optional[bool] = Field(default=None)
    CallUsEnableVideo: Optional[bool] = Field(default=None)
    CallUsRequirement: Optional[Authentication] = Field(default=None)
    ClickToCallId: Optional[str] = Field(default=None)
    CurrentGroupHours: Optional[GroupHoursMode] = Field(default=None)
    CustomOperator: Optional[Destination] = Field(default=None)
    custom_prompt: Optional[str] = Field(default=None, alias="CustomPrompt")
    DisableCustomPrompt: Optional[bool] = Field(default=None)
    GloballyVisible: Optional[bool] = Field(default=None)
    Groups: list[UserGroup] = Field(default_factory=list)
    HasMembers: Optional[bool] = Field(default=None)
    HolidaysRoute: Optional[Route] = Field(default=None)
    Hours: Optional[Schedule] = Field(default=None)
    Id: int = Field(default_factory=list)
    IsDefault: Optional[bool] = Field(default=None)
    Language: Optional[str] = Field(default=None)
    LastLoginTime: Optional[datetime] = Field(default=None)
    Members: list[UserGroup] = Field(default_factory=list)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    OfficeHolidays: list[Holiday] = Field(default_factory=list)
    OfficeRoute: Optional[Route] = Field(default=None)
    OutOfOfficeRoute: Optional[Route] = Field(default=None)
    OverrideExpiresAt: Optional[datetime] = Field(default=None)
    OverrideHolidays: Optional[bool] = Field(default=None)
    prompt_set: Optional[str] = Field(default=None, alias="PromptSet")
    Props: Optional[GroupProps] = Field(default=None)
    rights: list[Rights] = Field(default_factory=list, alias="Rights")
    TimeZoneId: Optional[str] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)


class GroupCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Group] = Field(default_factory=list)


class MultiEditUserData(Schema):
    AllowLanOnly: Optional[bool] = Field(default=None)
    AllowOwnRecordings: Optional[bool] = Field(default=None)
    Blfs: Optional[str] = Field(default=None)
    CallScreening: Optional[bool] = Field(default=None)
    CanMoveForwardingExceptions: Optional[bool] = Field(default=None)
    DisplayNumbers: Optional[str] = Field(default=None)
    EmergencyAdditionalInfo: Optional[str] = Field(default=None)
    EmergencyLocationId: Optional[str] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    EnableHotdesking: Optional[bool] = Field(default=None)
    ForwardingExceptions: list[ExtensionRule] = Field(default_factory=list)
    ForwardingProfiles: list[ForwardingProfile] = Field(default_factory=list)
    GoogleCalendarEnabled: Optional[bool] = Field(default=None)
    GoogleContactsEnabled: Optional[bool] = Field(default=None)
    GoogleSignInEnabled: Optional[bool] = Field(default=None)
    Greetings: list[Greeting] = Field(default_factory=list)
    Groups: list[UserGroup] = Field(default_factory=list)
    HideInPhonebook: Optional[bool] = Field(default=None)
    Internal: Optional[bool] = Field(default=None)
    Mobile: Optional[str] = Field(default=None)
    MS365CalendarEnabled: Optional[bool] = Field(default=None)
    MS365ContactsEnabled: Optional[bool] = Field(default=None)
    MS365SignInEnabled: Optional[bool] = Field(default=None)
    MS365TeamsEnabled: Optional[bool] = Field(default=None)
    MyPhoneAllowDeleteRecordings: Optional[bool] = Field(default=None)
    MyPhoneHideForwardings: Optional[bool] = Field(default=None)
    MyPhoneShowRecordings: Optional[bool] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    PbxDeliversAudio: Optional[bool] = Field(default=None)
    PinProtected: Optional[bool] = Field(default=None)
    PinProtectTimeout: Optional[int] = Field(default=None)
    prompt_set: Optional[str] = Field(default=None, alias="PromptSet")
    RecordCalls: Optional[bool] = Field(default=None)
    RecordEmailNotify: Optional[bool] = Field(default=None)
    RecordExternalCallsOnly: Optional[bool] = Field(default=None)
    SendEmailMissedCalls: Optional[bool] = Field(default=None)
    SRTPMode: Optional[SRTPModeType] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    VMDisablePinAuth: Optional[bool] = Field(default=None)
    VMEmailOptions: Optional[VMEmailOptionsType] = Field(default=None)
    VMEnabled: Optional[bool] = Field(default=None)
    VMPlayCallerID: Optional[bool] = Field(default=None)
    VMPlayMsgDateTime: Optional[VMPlayMsgDateTimeType] = Field(default=None)


class Parking(Schema):
    Groups: list[UserGroup] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    Number: Optional[str] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)


class ParkingCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Parking] = Field(default_factory=list)


class Queue(Schema):
    AgentAvailabilityMode: Optional[bool] = Field(default=None)
    Agents: list[QueueAgent] = Field(default_factory=list)
    AnnouncementInterval: Optional[int] = Field(default=None)
    AnnounceQueuePosition: Optional[bool] = Field(default=None)
    BreakRoute: Optional[Route] = Field(default=None)
    CallbackEnableTime: Optional[int] = Field(default=None)
    CallbackPrefix: Optional[str] = Field(default=None)
    CallUsEnableChat: Optional[bool] = Field(default=None)
    CallUsEnablePhone: Optional[bool] = Field(default=None)
    CallUsEnableVideo: Optional[bool] = Field(default=None)
    CallUsRequirement: Optional[Authentication] = Field(default=None)
    ClickToCallId: Optional[str] = Field(default=None)
    EnableIntro: Optional[bool] = Field(default=None)
    ForwardNoAnswer: Optional[Destination] = Field(default=None)
    greeting_file: Optional[str] = Field(default=None, alias="GreetingFile")
    Groups: list[UserGroup] = Field(default_factory=list)
    HolidaysRoute: Optional[Route] = Field(default=None)
    Id: int = Field(default_factory=list)
    IntroFile: Optional[str] = Field(default=None)
    IsRegistered: Optional[bool] = Field(default=None)
    Managers: list[QueueManager] = Field(default_factory=list)
    MasterTimeout: Optional[int] = Field(default=None)
    MaxCallersInQueue: Optional[int] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    NotifyCodes: list[QueueNotifyCode] = Field(default_factory=list)
    Number: Optional[str] = Field(default=None)
    OnHoldFile: Optional[str] = Field(default=None)
    OutOfOfficeRoute: Optional[Route] = Field(default=None)
    PlayFullPrompt: Optional[bool] = Field(default=None)
    PollingStrategy: Optional[PollingStrategyType] = Field(default=None)
    PriorityQueue: Optional[bool] = Field(default=None)
    prompt_set: Optional[str] = Field(default=None, alias="PromptSet")
    recording: Optional[QueueRecording] = Field(default=None, alias="Recording")
    reset_queue_statistics_schedule: Optional[ResetQueueStatisticsSchedule] = Field(default=None, alias="ResetQueueStatisticsSchedule")
    ResetStatisticsScheduleEnabled: Optional[bool] = Field(default=None)
    RingTimeout: Optional[int] = Field(default=None)
    SLATime: Optional[int] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    type_of_chat_ownership_type: Optional[TypeOfChatOwnershipType] = Field(default=None, alias="TypeOfChatOwnershipType")
    WrapUpTime: Optional[int] = Field(default=None)


class QueueCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Queue] = Field(default_factory=list)


class Receptionist(Schema):
    BreakRoute: Optional[Route] = Field(default=None)
    Forwards: list[ReceptionistForward] = Field(default_factory=list)
    ForwardSmsTo: Optional[str] = Field(default=None)
    Groups: list[UserGroup] = Field(default_factory=list)
    HolidaysRoute: Optional[Route] = Field(default=None)
    Id: int = Field(default_factory=list)
    InvalidKeyForwardDN: Optional[str] = Field(default=None)
    IsRegistered: Optional[bool] = Field(default=None)
    ivr_type: Optional[IVRType] = Field(default=None, alias="IVRType")
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    OutOfOfficeRoute: Optional[Route] = Field(default=None)
    PromptFilename: Optional[str] = Field(default=None)
    prompt_set: Optional[str] = Field(default=None, alias="PromptSet")
    Timeout: Optional[int] = Field(default=None)
    TimeoutForwardDN: Optional[str] = Field(default=None)
    TimeoutForwardPeerType: Optional[PeerType] = Field(default=None)
    TimeoutForwardType: Optional[IVRForwardType] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    UseMSExchange: Optional[bool] = Field(default=None)


class ReceptionistCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Receptionist] = Field(default_factory=list)


class RingGroup(Schema):
    BreakRoute: Optional[Route] = Field(default=None)
    CallUsEnableChat: Optional[bool] = Field(default=None)
    CallUsEnablePhone: Optional[bool] = Field(default=None)
    CallUsEnableVideo: Optional[bool] = Field(default=None)
    CallUsRequirement: Optional[Authentication] = Field(default=None)
    ClickToCallId: Optional[str] = Field(default=None)
    ForwardNoAnswer: Optional[Destination] = Field(default=None)
    greeting_file: Optional[str] = Field(default=None, alias="GreetingFile")
    Groups: list[UserGroup] = Field(default_factory=list)
    HolidaysRoute: Optional[Route] = Field(default=None)
    Id: int = Field(default_factory=list)
    IsRegistered: Optional[bool] = Field(default=None)
    Members: list[RingGroupMember] = Field(default_factory=list)
    MulticastAddress: Optional[str] = Field(default=None)
    MulticastCodec: Optional[str] = Field(default=None)
    MulticastPacketTime: Optional[int] = Field(default=None)
    MulticastPort: Optional[int] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    OutOfOfficeRoute: Optional[Route] = Field(default=None)
    RingStrategy: Optional[StrategyType] = Field(default=None)
    RingTime: Optional[int] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)


class RingGroupCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[RingGroup] = Field(default_factory=list)


class ServicePrincipal(Schema):
    CallControlEnabled: Optional[bool] = Field(default=None)
    Groups: list[UserGroup] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    LastUsed: Optional[datetime] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    Peers: list[Peer] = Field(default_factory=list)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    XAPIEnabled: Optional[bool] = Field(default=None)


class ServicePrincipalCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[ServicePrincipal] = Field(default_factory=list)


class User(Schema):
    AccessPassword: Optional[str] = Field(default=None)
    AllowLanOnly: Optional[bool] = Field(default=None)
    AllowOwnRecordings: Optional[bool] = Field(default=None)
    AuthID: Optional[str] = Field(default=None)
    AuthPassword: Optional[str] = Field(default=None)
    Blfs: Optional[str] = Field(default=None)
    BreakTime: Optional[Schedule] = Field(default=None)
    CallScreening: Optional[bool] = Field(default=None)
    CallUsEnableChat: Optional[bool] = Field(default=None)
    CallUsEnablePhone: Optional[bool] = Field(default=None)
    CallUsEnableVideo: Optional[bool] = Field(default=None)
    CallUsRequirement: Optional[Authentication] = Field(default=None)
    ClickToCallId: Optional[str] = Field(default=None)
    ContactImage: Optional[str] = Field(default=None)
    CurrentProfileName: Optional[str] = Field(default=None)
    DeskphonePassword: Optional[str] = Field(default=None)
    DisplayName: Optional[str] = Field(default=None)
    EmailAddress: Optional[str] = Field(default=None)
    EmergencyAdditionalInfo: Optional[str] = Field(default=None)
    EmergencyLocationId: Optional[str] = Field(default=None)
    Enable2FA: Optional[bool] = Field(default=None)
    Enabled: Optional[bool] = Field(default=None)
    EnableHotdesking: Optional[bool] = Field(default=None)
    FirstName: Optional[str] = Field(default=None)
    ForwardingExceptions: list[ExtensionRule] = Field(default_factory=list)
    ForwardingProfiles: list[ForwardingProfile] = Field(default_factory=list)
    GoogleCalendarEnabled: Optional[bool] = Field(default=None)
    GoogleContactsEnabled: Optional[bool] = Field(default=None)
    GoogleSignInEnabled: Optional[bool] = Field(default=None)
    Greetings: list[Greeting] = Field(default_factory=list)
    Groups: list[UserGroup] = Field(default_factory=list)
    HideInPhonebook: Optional[bool] = Field(default=None)
    HotdeskingAssignment: Optional[str] = Field(default=None)
    Hours: Optional[Schedule] = Field(default=None)
    Id: int = Field(default_factory=list)
    Internal: Optional[bool] = Field(default=None)
    IsRegistered: Optional[bool] = Field(default=None)
    Language: Optional[str] = Field(default=None)
    LastName: Optional[str] = Field(default=None)
    Mobile: Optional[str] = Field(default=None)
    MS365CalendarEnabled: Optional[bool] = Field(default=None)
    MS365ContactsEnabled: Optional[bool] = Field(default=None)
    MS365SignInEnabled: Optional[bool] = Field(default=None)
    MS365TeamsEnabled: Optional[bool] = Field(default=None)
    MyPhoneAllowDeleteRecordings: Optional[bool] = Field(default=None)
    MyPhoneHideForwardings: Optional[bool] = Field(default=None)
    MyPhonePush: Optional[bool] = Field(default=None)
    MyPhoneShowRecordings: Optional[bool] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    OfficeHoursProps: list[OfficeHoursBits] = Field(default_factory=list)
    OutboundCallerID: Optional[str] = Field(default=None)
    PbxDeliversAudio: Optional[bool] = Field(default=None)
    Phones: list[Phone] = Field(default_factory=list)
    PinProtected: Optional[bool] = Field(default=None)
    PinProtectTimeout: Optional[int] = Field(default=None)
    PrimaryGroupId: Optional[int] = Field(default=None)
    prompt_set: Optional[str] = Field(default=None, alias="PromptSet")
    QueueStatus: Optional[QueueStatusType] = Field(default=None)
    RecordCalls: Optional[bool] = Field(default=None)
    RecordEmailNotify: Optional[bool] = Field(default=None)
    RecordExternalCallsOnly: Optional[bool] = Field(default=None)
    Require2FA: Optional[bool] = Field(default=None)
    SendEmailMissedCalls: Optional[bool] = Field(default=None)
    SIPID: Optional[str] = Field(default=None)
    SRTPMode: Optional[SRTPModeType] = Field(default=None)
    Tags: list[UserTag] = Field(default_factory=list)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    VMDisablePinAuth: Optional[bool] = Field(default=None)
    VMEmailOptions: Optional[VMEmailOptionsType] = Field(default=None)
    VMEnabled: Optional[bool] = Field(default=None)
    VMPIN: Optional[str] = Field(default=None)
    VMPlayCallerID: Optional[bool] = Field(default=None)
    VMPlayMsgDateTime: Optional[VMPlayMsgDateTimeType] = Field(default=None)
    WebMeetingApproveParticipants: Optional[bool] = Field(default=None)
    WebMeetingFriendlyName: Optional[str] = Field(default=None)


class UserCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[User] = Field(default_factory=list)


class UserGroupCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[UserGroup] = Field(default_factory=list)


class UsersRequestOptions(Schema):
    Count: int = Field(default_factory=list)
    NextPageToken: Optional[str] = Field(default=None)
    Search: Optional[str] = Field(default=None)
    type_of_user: TypeOfUser = Field(..., alias="TypeOfUser")


class UsersSyncConfiguration(Schema):
    IsEnabled: Optional[bool] = Field(default=None)
    SelectedUsers: list[str] = Field(default_factory=list)
    SyncType: Optional[IntegrationSyncType] = Field(default=None)


class Microsoft365Integration(Schema):
    AdUsers: Optional[ADUsersSyncConfiguration] = Field(default=None)
    ApplicationId: str = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    SharedMailboxesSync: Optional[UsersSyncConfiguration] = Field(default=None)
    TenantId: str = Field(default_factory=list)


class Variable(Schema):
    Name: str = Field(default_factory=list)
    Value: str = Field(default_factory=list)


class Fxs(Schema):
    Brand: Optional[str] = Field(default=None)
    Codecs: list[str] = Field(default_factory=list)
    FxsLineCount: Optional[int] = Field(default=None)
    FxsLines: list[DeviceLine] = Field(default_factory=list)
    group: Optional[str] = Field(default=None, alias="Group")
    Language: Optional[str] = Field(default=None)
    MacAddress: str = Field(default_factory=list)
    Model: Optional[str] = Field(default=None)
    ModelName: Optional[str] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Password: Optional[str] = Field(default=None)
    Provisioning: Optional[FxsProvisioning] = Field(default=None)
    Registered: Optional[RegistrarFxs] = Field(default=None)
    Secret: Optional[str] = Field(default=None)
    Template: Optional[FxsTemplate] = Field(default=None)
    time_zone: Optional[str] = Field(default=None, alias="TimeZone")
    Variables: list[Variable] = Field(default_factory=list)


class FxsCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Fxs] = Field(default_factory=list)


class Trunk(Schema):
    AuthID: Optional[str] = Field(default=None)
    AuthPassword: Optional[ConcealedPassword] = Field(default=None)
    Certificate: Optional[str] = Field(default=None)
    CertificateName: Optional[str] = Field(default=None)
    ConfigurationIssue: Optional[str] = Field(default=None)
    DidNumbers: list[str] = Field(default_factory=list)
    Direction: Optional[DirectionType] = Field(default=None)
    DisableVideo: Optional[bool] = Field(default=None)
    DiversionHeader: Optional[bool] = Field(default=None)
    E164CountryCode: Optional[str] = Field(default=None)
    E164ProcessIncomingNumber: Optional[bool] = Field(default=None)
    EmergencyGeoLocations: list[EmergencyGeoTrunkLocation] = Field(default_factory=list)
    EnableInboundCalls: Optional[bool] = Field(default=None)
    EnableOutboundCalls: Optional[bool] = Field(default=None)
    ExternalNumber: Optional[str] = Field(default=None)
    gateway: Optional[Gateway] = Field(default=None, alias="Gateway")
    Groups: list[UserGroup] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    InCIDFormatting: list[CIDFormatting] = Field(default_factory=list)
    IPRestriction: Optional[TypeOfIPDestriction] = Field(default=None)
    IsOnline: Optional[bool] = Field(default=None)
    Messaging: Optional[TrunkMessaging] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    OutboundCallerID: Optional[str] = Field(default=None)
    OutCIDFormatting: list[CIDFormatting] = Field(default_factory=list)
    PublicInfoGroups: list[str] = Field(default_factory=list)
    PublicIPinSIP: Optional[str] = Field(default=None)
    PublishInfo: Optional[bool] = Field(default=None)
    ReceiveExtensions: list[Peer] = Field(default_factory=list)
    ReceiveInfo: Optional[bool] = Field(default=None)
    RemoteMyPhoneUriHost: Optional[str] = Field(default=None)
    RemotePBXPreffix: Optional[str] = Field(default=None)
    RoutingRules: list[InboundRule] = Field(default_factory=list)
    SecondaryRegistrar: Optional[str] = Field(default=None)
    SeparateAuthId: Optional[str] = Field(default=None)
    SimultaneousCalls: Optional[int] = Field(default=None)
    Tags: list[UserTag] = Field(default_factory=list)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    TransportRestriction: Optional[TypeOfTransportRestriction] = Field(default=None)
    TrunkRegTimes: list[Variable] = Field(default_factory=list)
    TunnelEnabled: Optional[bool] = Field(default=None)
    TunnelRemoteAddr: Optional[str] = Field(default=None)
    TunnelRemotePort: Optional[int] = Field(default=None)
    UseSeparateAuthId: Optional[bool] = Field(default=None)


class CallFlowApp(Schema):
    CompilationLastSuccess: Optional[datetime] = Field(default=None)
    CompilationResult: Optional[str] = Field(default=None)
    CompilationSucceeded: Optional[bool] = Field(default=None)
    Groups: list[UserGroup] = Field(default_factory=list)
    Id: int = Field(default_factory=list)
    InvalidScript: Optional[bool] = Field(default=None)
    IsRegistered: Optional[bool] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Number: Optional[str] = Field(default=None)
    RejectedCode: Optional[str] = Field(default=None)
    RoutingType: Optional[CfaRoutingType] = Field(default=None)
    ScriptCode: Optional[str] = Field(default=None)
    TranscriptionMode: Optional[TranscriptionType] = Field(default=None)
    trunk: Optional[Trunk] = Field(default=None, alias="Trunk")


class CallFlowAppCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[CallFlowApp] = Field(default_factory=list)


class TrunkCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Trunk] = Field(default_factory=list)


class VariableCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Variable] = Field(default_factory=list)


class VersionUpdateType(Schema):
    Type: Optional[UpdateType] = Field(default=None)


class VoicemailSettings(Schema):
    AutoDeleteDays: Optional[int] = Field(default=None)
    AutoDeleteEnabled: Optional[bool] = Field(default=None)
    Extension: Optional[str] = Field(default=None)
    Id: int = Field(default_factory=list)
    MinDuration: Optional[int] = Field(default=None)
    OperatorEnabled: Optional[bool] = Field(default=None)
    Quota: Optional[int] = Field(default=None)
    RemoteStorageEnabled: Optional[bool] = Field(default=None)
    SendEmailQuotaEnabled: Optional[bool] = Field(default=None)
    SendEmailQuotaPercentage: Optional[int] = Field(default=None)
    transcribe_engine: Optional[TranscribeEngine] = Field(default=None, alias="TranscribeEngine")
    TranscribeLanguage: Optional[str] = Field(default=None)
    TranscribeRegion: Optional[str] = Field(default=None)
    TranscribeSecretKey: Optional[ConcealedPassword] = Field(default=None)
    UsedSpace: Optional[int] = Field(default=None)


class VoipProvider(Schema):
    Countries: list[str] = Field(default_factory=list)
    Id: str = Field(default_factory=list)
    Name: str = Field(default_factory=list)
    Type: TemplateType = Field(...)


class WebsiteLinksTranslations(Schema):
    AuthenticationMessage: Optional[str] = Field(default=None)
    EndingMessage: Optional[str] = Field(default=None)
    FirstResponseMessage: Optional[str] = Field(default=None)
    GdprMessage: Optional[str] = Field(default=None)
    GreetingMessage: Optional[str] = Field(default=None)
    GreetingOfflineMessage: Optional[str] = Field(default=None)
    InviteMessage: Optional[str] = Field(default=None)
    OfflineEmailMessage: Optional[str] = Field(default=None)
    OfflineFinishMessage: Optional[str] = Field(default=None)
    OfflineFormInvalidEmail: Optional[str] = Field(default=None)
    OfflineFormInvalidName: Optional[str] = Field(default=None)
    OfflineFormMaximumCharactersReached: Optional[str] = Field(default=None)
    OfflineNameMessage: Optional[str] = Field(default=None)
    StartChatButtonText: Optional[str] = Field(default=None)
    UnavailableMessage: Optional[str] = Field(default=None)
    WindowTitle: Optional[str] = Field(default=None)


class Weblink(Schema):
    Advanced: Optional[LiveChatAdvancedSettings] = Field(default=None)
    CallsEnabled: Optional[bool] = Field(default=None)
    ChatBox: Optional[LiveChatBox] = Field(default=None)
    ChatEnabled: Optional[bool] = Field(default=None)
    DefaultRecord: Optional[bool] = Field(default=None)
    DN: Optional[Peer] = Field(default=None)
    EnableReCaptcha: Optional[bool] = Field(default=None)
    General: Optional[GeneralLiveChatSettings] = Field(default=None)
    group: Optional[str] = Field(default=None, alias="Group")
    Hidden: Optional[bool] = Field(default=None)
    Id: Optional[int] = Field(default=None)
    Link: str = Field(default_factory=list)
    MeetingEnabled: Optional[bool] = Field(default=None)
    Name: Optional[str] = Field(default=None)
    Styling: Optional[LiveChatStyling] = Field(default=None)
    Translations: Optional[WebsiteLinksTranslations] = Field(default=None)
    Website: list[str] = Field(default_factory=list)


class WeblinkCollectionResponse(BaseCollectionPaginationCountResponse):
    value: list[Weblink] = Field(default_factory=list)


class XLicenseParams(Schema):
    CompanyName: Optional[str] = Field(default=None)
    ContactName: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None, alias="Country")
    Email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None, alias="Phone")


class XOutboundRulePurge(Schema):
    Ids: list[int] = Field(default_factory=list)


class XServiceManageOptions(Schema):
    ServiceNames: list[str] = Field(default_factory=list)
