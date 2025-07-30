from threecxapi.util import TcxStrEnum
from enum import auto


class AuthenticateMode(TcxStrEnum):
    Password = auto()
    CertificateFile = auto()


class RemoteAccessStatus(TcxStrEnum):
    NONE = auto()
    Requested = auto()
    Active = auto()


class IVRType(TcxStrEnum):
    Default = auto()
    CodeBased = auto()
    ScriptBased = auto()
    Wakeup = auto()


class PeerType(TcxStrEnum):
    NONE = auto()
    Extension = auto()
    Queue = auto()
    RingGroup = auto()
    IVR = auto()
    Fax = auto()
    Conference = auto()
    Parking = auto()
    ExternalLine = auto()
    SpecialMenu = auto()
    Group = auto()
    RoutePoint = auto()


class IVRForwardType(TcxStrEnum):
    EndCall = auto()
    Extension = auto()
    RingGroup = auto()
    Queue = auto()
    IVR = auto()
    VoiceMail = auto()
    CallByName = auto()
    RepeatPrompt = auto()
    CustomInput = auto()


class DestinationType(TcxStrEnum):
    NONE = auto()
    VoiceMail = auto()
    Extension = auto()
    Queue = auto()
    RingGroup = auto()
    IVR = auto()
    External = auto()
    Fax = auto()
    Boomerang = auto()
    Deflect = auto()
    VoiceMailOfDestination = auto()
    Callback = auto()
    RoutePoint = auto()
    ProceedWithNoExceptions = auto()


class BlockType(TcxStrEnum):
    Block = auto()
    Allow = auto()


class AddedBy(TcxStrEnum):
    Manual = auto()
    Mcu = auto()
    Webmeeting = auto()
    AutoBlacklist = auto()
    Whitelist = auto()


class StrategyType(TcxStrEnum):
    Hunt = auto()
    RingAll = auto()
    Paging = auto()


class Authentication(TcxStrEnum):
    Both = auto()
    Name = auto()
    Email = auto()
    NONE = auto()


class PollingStrategyType(TcxStrEnum):
    Hunt = auto()
    RingAll = auto()
    HuntRandomStart = auto()
    NextAgent = auto()
    LongestWaiting = auto()
    LeastTalkTime = auto()
    FewestAnswered = auto()
    HuntBy3s = auto()
    First3Available = auto()
    SkillBasedRouting_RingAll = auto()
    SkillBasedRouting_HuntRandomStart = auto()
    SkillBasedRouting_RoundRobin = auto()
    SkillBasedRouting_FewestAnswered = auto()


class TypeOfChatOwnershipType(TcxStrEnum):
    TakeManually = auto()
    AutoAssign = auto()


class QueueRecording(TcxStrEnum):
    Disabled = auto()
    AllowToOptOut = auto()
    AskToOptIn = auto()


class QueueNotifyCode(TcxStrEnum):
    Callback = auto()
    CallbackFail = auto()
    SLATimeBreached = auto()
    CallLost = auto()


class ResetQueueStatisticsFrequency(TcxStrEnum):
    Disabled = auto()
    Daily = auto()
    Weekly = auto()
    Monthly = auto()


class DayOfWeek(TcxStrEnum):
    Sunday = auto()
    Monday = auto()
    Tuesday = auto()
    Wednesday = auto()
    Thursday = auto()
    Friday = auto()
    Saturday = auto()


class VMEmailOptionsType(TcxStrEnum):
    NONE = auto()
    Notification = auto()
    Attachment = auto()
    AttachmentAndDelete = auto()


class VMPlayMsgDateTimeType(TcxStrEnum):
    NONE = auto()
    Play12Hr = auto()
    Play24Hr = auto()


class ProfileType(TcxStrEnum):
    Default = auto()
    Available = auto()
    Away = auto()
    OutOfOffice = auto()
    Available2 = auto()
    OutOfOffice2 = auto()


class RuleHoursType(TcxStrEnum):
    AllHours = auto()
    OfficeHours = auto()
    OutOfOfficeHours = auto()
    SpecificHours = auto()
    SpecificHoursExcludingHolidays = auto()
    OutOfSpecificHours = auto()
    OutOfSpecificHoursIncludingHolidays = auto()
    Never = auto()
    BreakTime = auto()


class OfficeHoursBits(TcxStrEnum):
    GlobalSchedule = auto()
    AutoSwitchProfiles = auto()
    AutoQueueLogOut = auto()
    BlockOutboundCalls = auto()


class ProvType(TcxStrEnum):
    LocalLan = auto()
    RemoteExt = auto()
    RemoteExtSipProxyMgr = auto()
    SBC = auto()


class XferTypeEnum(TcxStrEnum):
    BXfer = auto()
    AttXfer = auto()


class PhoneDeviceVlanType(TcxStrEnum):
    Wan = auto()
    Pc = auto()


class UserTag(TcxStrEnum):
    MS = auto()
    Teams = auto()
    Google = auto()
    WakeUp = auto()
    FaxServer = auto()
    Principal = auto()
    WeakID = auto()
    WeakPass = auto()
    WM = auto()


class TemplateType(TcxStrEnum):
    Preferred = auto()
    Supported = auto()
    Dedicated = auto()
    ThirdParty = auto()
    Deleted = auto()
    Unknown = auto()


class TrunkEditorType(TcxStrEnum):
    Messaging = auto()
    Voip = auto()


class TrunkVariableType(TcxStrEnum):
    Text = auto()
    Password = auto()


class RecordingCallType(TcxStrEnum):
    Local = auto()
    InboundExternal = auto()
    OutboundExternal = auto()


class ScheduleType(TcxStrEnum):
    Daily = auto()
    Weekly = auto()
    Monthly = auto()
    Hourly = auto()
    Immediate = auto()


class FileSystemType(TcxStrEnum):
    Local = auto()
    Ftp = auto()
    GoogleDrive = auto()
    NetworkShare = auto()
    Logs = auto()
    Sftp = auto()
    GoogleBucket = auto()
    SharePoint = auto()


class CallHandlingFlags(TcxStrEnum):
    WelcomeMessageForIncomingCalls = auto()
    HoldCall = auto()


class GroupHoursMode(TcxStrEnum):
    Default = auto()
    ForceOpened = auto()
    ForceClosed = auto()
    ForceBreak = auto()
    ForceCustomOperator = auto()
    ForceHoliday = auto()
    HasForcedMask = auto()


class StartupLicense(TcxStrEnum):
    Free = auto()
    Pro = auto()


class DirectionType(TcxStrEnum):
    NONE = auto()
    Inbound = auto()
    Outbound = auto()
    Both = auto()


class SRTPModeType(TcxStrEnum):
    SRTPDisabled = auto()
    SRTPEnabled = auto()
    SRTPEnforced = auto()


class MatchingStrategyType(TcxStrEnum):
    MatchAnyFields = auto()
    MatchAllFields = auto()


class RequireRegistrationForType(TcxStrEnum):
    Nothing = auto()
    IncomingCalls = auto()
    OutgoingCalls = auto()
    InOutCalls = auto()


class GatewayType(TcxStrEnum):
    Unknown = auto()
    Analog = auto()
    Provider = auto()
    BridgeMaster = auto()
    BridgeSlave = auto()
    BridgeSlaveOverTunnel = auto()
    BRI = auto()
    T1 = auto()
    E1 = auto()


class IPInRegistrationContactType(TcxStrEnum):
    External = auto()
    Internal = auto()
    Both = auto()
    Specified = auto()


class RuleCallTypeType(TcxStrEnum):
    AllCalls = auto()
    InternalCallsOnly = auto()
    ExternalCallsOnly = auto()


class RuleConditionType(TcxStrEnum):
    NoAnswer = auto()
    PhoneBusy = auto()
    PhoneNotRegistered = auto()
    ForwardAll = auto()
    BasedOnCallerID = auto()
    BasedOnDID = auto()


class TypeOfIPDestriction(TcxStrEnum):
    Any = auto()
    IPV4 = auto()
    IPV6 = auto()


class TypeOfTransportRestriction(TcxStrEnum):
    Any = auto()
    UDP = auto()
    TCP = auto()
    TLS = auto()


class DeviceType(TcxStrEnum):
    Fxs = auto()
    Dect = auto()


class PromptSetType(TcxStrEnum):
    System = auto()
    Custom = auto()


class PromptType(TcxStrEnum):
    File = auto()
    Playlist = auto()
    DepFile = auto()


class AnimationStyle(TcxStrEnum):
    SlideUp = auto()
    SlideFromSide = auto()
    FadeIn = auto()
    NoAnimation = auto()


class LiveChatGreeting(TcxStrEnum):
    Disabled = auto()
    OnlyOnDesktop = auto()
    OnlyOnMobile = auto()
    DesktopAndMobile = auto()


class LiveChatCommunication(TcxStrEnum):
    ChatOnly = auto()
    PhoneAndChat = auto()
    PhoneOnly = auto()
    VideoPhoneAndChat = auto()


class LiveChatMinimizedStyle(TcxStrEnum):
    BubbleLeft = auto()
    BubbleRight = auto()
    BottomLeft = auto()
    BottomRight = auto()


class LiveChatLanguage(TcxStrEnum):
    browser = auto()
    en = auto()
    es = auto()
    de = auto()
    fr = auto()
    it = auto()
    pl = auto()
    ru = auto()
    pt = auto()
    zh = auto()


class LiveMessageUserinfoFormat(TcxStrEnum):
    Avatar = auto()
    Name = auto()
    Both = auto()
    NONE = auto()


class LiveChatMessageDateformat(TcxStrEnum):
    Date = auto()
    Time = auto()
    Both = auto()


class ButtonIconType(TcxStrEnum):
    Url = auto()
    Default = auto()
    Bubble = auto()
    DoubleBubble = auto()


class UpdateType(TcxStrEnum):
    Release = auto()
    Beta = auto()
    MajorRelease = auto()
    Alpha = auto()
    Hotfix = auto()


class FailoverMode(TcxStrEnum):
    Active = auto()
    Passive = auto()


class FailoverCondition(TcxStrEnum):
    AllService = auto()
    AnyService = auto()


class ChatType(TcxStrEnum):
    SMS = auto()
    LiveChat = auto()
    Facebook = auto()
    Internal = auto()
    RCS = auto()


class ParameterType(TcxStrEnum):
    String = auto()
    Integer = auto()
    Double = auto()
    Boolean = auto()
    DateTime = auto()
    Password = auto()
    OAuth = auto()
    List = auto()


class EditorType(TcxStrEnum):
    String = auto()
    Sql = auto()


class AuthenticationType(TcxStrEnum):
    FALSE = auto()
    Basic = auto()
    Scenario = auto()


class TypeOfCDRLog(TcxStrEnum):
    SingleFileForAllCalls = auto()
    SingleFileForEachCall = auto()
    PassiveSocket = auto()
    ActiveSocket = auto()


class EventLogType(TcxStrEnum):
    Error = auto()
    Warning = auto()
    Info = auto()


class ServiceStatus(TcxStrEnum):
    Stopped = auto()
    StartPending = auto()
    StopPending = auto()
    Running = auto()
    ContinuePending = auto()
    PausePending = auto()
    Paused = auto()


class IntegrationSyncType(TcxStrEnum):
    SyncAllUsers = auto()
    SyncAllUsersExceptSelected = auto()
    SyncSelected = auto()


class TypeOfUser(TcxStrEnum):
    Users = auto()
    SharedMailboxes = auto()
    LicensedUsers = auto()


class MailServerType(TcxStrEnum):
    Tcx = auto()
    MS365 = auto()
    Custom = auto()
    GoogleWorkspace = auto()


class PmsIntegrationType(TcxStrEnum):
    tcxpms = auto()
    fidelio = auto()


class XOperatingSystemType(TcxStrEnum):
    Other = auto()
    Linux = auto()
    Windows = auto()


class TypeOfAutoPickupForward(TcxStrEnum):
    TransferBack = auto()
    DN = auto()
    ExtensionVoiceMail = auto()
    ExternalNumber = auto()
    RoutePoint = auto()


class TypeOfPhoneBookResolving(TcxStrEnum):
    NotResolve = auto()
    MatchExact = auto()
    MatchLength = auto()


class TypeOfPhoneBookDisplay(TcxStrEnum):
    FirstNameLastName = auto()
    LastNameFirstName = auto()


class TypeOfPhoneBookAddQueueName(TcxStrEnum):
    NotAdd = auto()
    Append = auto()
    Prepend = auto()


class ChatRecipientsType(TcxStrEnum):
    NONE = auto()
    MyGroupManagers = auto()
    MyGroupAllMembers = auto()
    AllGroupsManagers = auto()


class PhonebookPriorityOptions(TcxStrEnum):
    NotQueryIfInPhonebookFound = auto()
    AlwaysQuery = auto()


class ContactType(TcxStrEnum):
    Company = auto()
    Personal = auto()


class ReferenceNumeric(TcxStrEnum):
    NEGATIVE_INF = "NEGATIVE_INFINITY"
    INF = "INFINITY"
    NaN = "NAN"


class AvatarStyle(TcxStrEnum):
    Square = auto()
    Circle = auto()


class CfaRoutingType(TcxStrEnum):
    DialCode = auto()
    Forward = auto()
    Trunk = auto()


class CreateTicketStatus(TcxStrEnum):
    OK = auto()
    KeyNotFound = auto()
    KeyNotAssignedToUser = auto()
    KeyAssignedToPartner = auto()
    KeyIsNotCommercial = auto()
    KeyHasNoSupportTickets = auto()


class GCCollectionMode(TcxStrEnum):
    Default = auto()
    Forced = auto()
    Optimized = auto()
    Aggressive = auto()


class LoginType(TcxStrEnum):
    Local = auto()
    Guest = auto()


class McuOperation(TcxStrEnum):
    Create = auto()
    Delete = auto()


class McuReqState(TcxStrEnum):
    Pending = auto()
    Success = auto()
    Failure = auto()


class OnBoardMcuServerOS(TcxStrEnum):
    Debian10 = auto()
    Debian11 = auto()
    Debian12 = auto()


class QueueStatusType(TcxStrEnum):
    LoggedOut = auto()
    LoggedIn = auto()


class ReportScheduleType(TcxStrEnum):
    Daily = auto()
    Weekly = auto()
    Monthly = auto()
    Hourly = auto()
    NotScheduled = auto()


class RevokeReason(TcxStrEnum):
    TooMany = auto()
    SetPassword = auto()
    InvalidatePassword = auto()
    Logout = auto()
    Manual = auto()


class ServerTrustMode(TcxStrEnum):
    Prefer = auto()
    Require = auto()
    VerifyFull = auto()


class SynchronizedM365Profile(TcxStrEnum):
    Available = auto()
    Busy = auto()
    Away = auto()
    AvailableIdle = auto()
    BusyIdle = auto()
    DoNotDisturb = auto()
    BeRightBack = auto()
    InMeeting = auto()
    InCall = auto()


class SynchronizedPbxProfile(TcxStrEnum):
    Available = auto()
    OutOfOffice = auto()
    Away = auto()


class TranscriptionType(TcxStrEnum):
    Nothing = auto()
    Voicemail = auto()
    Recordings = auto()
    Both = auto()
    Inherit = auto()


class TrunkType(TcxStrEnum):
    Voxtelesys = auto()
    Twilio = auto()


class OffloadDestination(TcxStrEnum):
    NONE = auto()
    Postgre = auto()
    BigQuery = auto()


class ScheduledReportType(TcxStrEnum):
    NONE = auto()
    CallLogs = auto()
    ChatLogs = auto()
    AuditLogs = auto()
    InboundRules = auto()
    QueueAbandonedCalls = auto()
    QueueAnsweredCallsByWaitingTime = auto()
    QueueCallbacks = auto()
    QueueFailedCallbacks = auto()
    QueuePerformanceOverview = auto()
    QueueDetailedStatistics = auto()
    QueueTeamGeneralStatistics = auto()
    SlaStatistics = auto()
    SlaBreaches = auto()
    AgentInQueueStatistics = auto()
    AgentLoginHistory = auto()
    ExtensionsStatisticsByRingGroups = auto()
    ExtensionStatistics = auto()
    CallCostByExtensionDept = auto()
    QueueChatPerformance = auto()
    QueueAgentsChat = auto()
    AbandonedChats = auto()
    RingGroups = auto()
    InboundCalls = auto()
    OutBoundCalls = auto()
    UserActivity = auto()
    CallDistribution = auto()


class TranscribeEngine(TcxStrEnum):
    NONE = auto()
    Google = auto()
    OpenAI = auto()
    Whisper = auto()
    Engine3CX = auto()


class Warnings(TcxStrEnum):
    WARNINGS__CONTACTS_SPECIFY_NAME_SURNAME_COMPANY = "WARNINGS.CONTACTS_SPECIFY_NAME_SURNAME_COMPANY"
    WARNINGS__CONTACTS_SPECIFY_PHONE_NUMBER = "WARNINGS.CONTACTS_SPECIFY_PHONE_NUMBER"
    WARNINGS__LENGTH_NOT_MORE_50_CHARS = "WARNINGS.LENGTH_NOT_MORE_50_CHARS"
    WARNINGS__LENGTH_NOT_MORE_255_CHARS = "WARNINGS.LENGTH_NOT_MORE_255_CHARS"
    WARNINGS__XAPI__LENGTH_NOT_MORE_2048_CHARS = "WARNINGS.XAPI.LENGTH_NOT_MORE_2048_CHARS"
    WARNINGS__XAPI__INVALID_HEX_CHARACTER = "WARNINGS.XAPI.INVALID_HEX_CHARACTER"
    WARNINGS__NO_MORE_NUMBERS_AVAILABLE = "WARNINGS.NO_MORE_NUMBERS_AVAILABLE"
    WARNINGS__ERP_SERVER_ERROR = "WARNINGS.ERP_SERVER_ERROR"
    WARNINGS__LICENSE_NOT_FOUND = "WARNINGS.LICENSE_NOT_FOUND"
    WARNINGS__LIMIT_REACHED = "WARNINGS.LIMIT_REACHED"
    WARNINGS__XAPI__INVALID = "WARNINGS.XAPI.INVALID"
    WARNINGS__XAPI__CAPTCHA_ERROR = "WARNINGS.XAPI.CAPTCHA_ERROR"
    WARNINGS__XAPI__INVALID_PIN_NUMBER = "WARNINGS.XAPI.INVALID_PIN_NUMBER"
    WARNINGS__XAPI__NOT_SUPPORTED = "WARNINGS.XAPI.NOT_SUPPORTED"
    WARNINGS__XAPI__USER_ROLE_DOWNGRADE = "WARNINGS.XAPI.USER_ROLE_DOWNGRADE"
    WARNINGS__GROUP_CANNOT_BE_DELETED = "WARNINGS.GROUP_CANNOT_BE_DELETED"
    WARNINGS__CANNOT_BE_DELETED = "WARNINGS.CANNOT_BE_DELETED"
    WARNINGS__GROUP_WITH_MEMBERS_CANNOT_BE_DELETED = "WARNINGS.GROUP_WITH_MEMBERS_CANNOT_BE_DELETED"
    WARNINGS__XAPI__OTHER_USER_ROLE_DOWNGRADE = "WARNINGS.XAPI.OTHER_USER_ROLE_DOWNGRADE"
    WARNINGS__XAPI__INVALID_LICENSE_TYPE = "WARNINGS.XAPI.INVALID_LICENSE_TYPE"
    WARNINGS__XAPI__INVALID_PASSWORD = "WARNINGS.XAPI.INVALID_PASSWORD"
    WARNINGS__XAPI__NOT_FOUND = "WARNINGS.XAPI.NOT_FOUND"
    WARNINGS__XAPI__FILE_NOT_FOUND = "WARNINGS.XAPI.FILE_NOT_FOUND"
    WARNINGS__XAPI__FILE_NOT_ACCESSIBLE = "WARNINGS.XAPI.FILE_NOT_ACCESSIBLE"
    WARNINGS__XAPI__REQUIRED = "WARNINGS.XAPI.REQUIRED"
    WARNINGS__XAPI__CAN_NOT_BE_EMPTY_STRING = "WARNINGS.XAPI.CAN_NOT_BE_EMPTY_STRING"
    WARNINGS__XAPI__DUPLICATE = "WARNINGS.XAPI.DUPLICATE"
    WARNINGS__XAPI__ALREADY_IN_USE = "WARNINGS.XAPI.ALREADY_IN_USE"
    WARNINGS__XAPI__PLAYLIST_IN_USE = "WARNINGS.XAPI.PLAYLIST_IN_USE"
    WARNINGS__XAPI__OUT_OF_THE_RANGE = "WARNINGS.XAPI.OUT_OF_THE_RANGE"
    WARNINGS__XAPI__TOO_MANY_PHONES = "WARNINGS.XAPI.TOO_MANY_PHONES"
    WARNINGS__XAPI__TOO_MANY_TRUNKS = "WARNINGS.XAPI.TOO_MANY_TRUNKS"
    WARNINGS__XAPI__TOO_MANY_SBC = "WARNINGS.XAPI.TOO_MANY_SBC"
    WARNINGS__XAPI__TOO_MANY_PROMPTS = "WARNINGS.XAPI.TOO_MANY_PROMPTS"
    WARNINGS__XAPI__OUTBOUND_RULES_LIMIT_REACHED = "WARNINGS.XAPI.OUTBOUND_RULES_LIMIT_REACHED"
    WARNINGS__XAPI__FORBIDDEN_CHANGE = "WARNINGS.XAPI.FORBIDDEN_CHANGE"
    WARNINGS__FAX_SERVER_CANNOT_BE_DELETED = "WARNINGS.FAX_SERVER_CANNOT_BE_DELETED"
    WARNINGS__OPERATOR_CANNOT_BE_DELETED = "WARNINGS.OPERATOR_CANNOT_BE_DELETED"
    WARNINGS__USER_EXTENSION_CANNOT_BE_DELETED = "WARNINGS.USER_EXTENSION_CANNOT_BE_DELETED"
    WARNINGS__XAPI__NUMBER_IGNORED = "WARNINGS.XAPI.NUMBER_IGNORED"
    WARNINGS__XAPI__INVALID_TIMEZONE = "WARNINGS.XAPI.INVALID_TIMEZONE"
    WARNINGS__XAPI__INVALID_PATH = "WARNINGS.XAPI.INVALID_PATH"
    WARNINGS__XAPI__PATH_SHOULD_NOT_CONTAIN_SPACES = "WARNINGS.XAPI.PATH_SHOULD_NOT_CONTAIN_SPACES"
    WARNINGS__XAPI__INVALID_CREDENTIALS = "WARNINGS.XAPI.INVALID_CREDENTIALS"
    WARNINGS__XAPI__CANNOT_CONNECT_FTP = "WARNINGS.XAPI.CANNOT_CONNECT_FTP"
    WARNINGS__XAPI__CANNOT_CONNECT_SMB = "WARNINGS.XAPI.CANNOT_CONNECT_SMB"
    WARNINGS__XAPI__CANNOT_CONNECT_SFTP = "WARNINGS.XAPI.CANNOT_CONNECT_SFTP"
    WARNINGS__XAPI__CANNOT_CONNECT_GOOGLE_BUCKET = "WARNINGS.XAPI.CANNOT_CONNECT_GOOGLE_BUCKET"
    WARNINGS__XAPI__PLAYLIST_NO_SOURCE = "WARNINGS.XAPI.PLAYLIST_NO_SOURCE"
    WARNINGS__XAPI__NO_USERS_IN_TEAMS = "WARNINGS.XAPI.NO_USERS_IN_TEAMS"
    WARNINGS__XAPI__FILE_FORMAT_IS_INCORRECT = "WARNINGS.XAPI.FILE_FORMAT_IS_INCORRECT"
    WARNINGS__XAPI__INVALID_FILE_NAME = "WARNINGS.XAPI.INVALID_FILE_NAME"
    WARNINGS__CSV_INVALID_FILE_FORMAT = "WARNINGS.CSV_INVALID_FILE_FORMAT"
    WARNINGS__CSV_LINE_CORRUPTED = "WARNINGS.CSV_LINE_CORRUPTED"
    WARNINGS__WRONG_CSV_FILE_REQUIRED_COLUMNS_NOT_FOUND = "WARNINGS.WRONG_CSV_FILE_REQUIRED_COLUMNS_NOT_FOUND"
    WARNINGS__CSV_IMPORT_LIMIT_REACHED = "WARNINGS.CSV_IMPORT_LIMIT_REACHED"
    WARNINGS__WRONG_CSV_FILE_REQUIRED_HEADER_NOT_FOUND = "WARNINGS.WRONG_CSV_FILE_REQUIRED_HEADER_NOT_FOUND"
    WARNINGS__XAPI__FILE_IS_TOO_LARGE = "WARNINGS.XAPI.FILE_IS_TOO_LARGE"
    WARNINGS__XAPI__SBC_CERT_FQDN_MISMATCH = "WARNINGS.XAPI.SBC_CERT_FQDN_MISMATCH"
    WARNINGS__XAPI__SBC_CERT_EXPIRED = "WARNINGS.XAPI.SBC_CERT_EXPIRED"
    WARNINGS__XAPI__SBC_KEY_CERT_MISMATCH = "WARNINGS.XAPI.SBC_KEY_CERT_MISMATCH"
    WARNINGS__XAPI__NON_EXISTENT_EXT_NUMBER = "WARNINGS.XAPI.NON_EXISTENT_EXT_NUMBER"
    WARNINGS__XAPI__MCM_MODE_REQUIRED = "WARNINGS.XAPI.MCM_MODE_REQUIRED"
    WARNINGS__INTERNATIONALPREFIX_IS_MISSING = "WARNINGS.INTERNATIONALPREFIX_IS_MISSING"
    WARNINGS__TIMEZONEID_IS_MISSING = "WARNINGS.TIMEZONEID_IS_MISSING"
    WARNINGS__XAPI__CHAT_LOG_IS_DISABLED = "WARNINGS.XAPI.CHAT_LOG_IS_DISABLED"
    WARNINGS__WAKEUP_IVR_EXISTS = "WARNINGS.WAKEUP_IVR_EXISTS"
    WARNINGS__RING_GROUP_ENABLE_PAGING = "WARNINGS.RING_GROUP_ENABLE_PAGING"
    WARNINGS__XAPI__CREATE_1_SIP_TRUCK_EMERGENCY = "WARNINGS.XAPI.CREATE_1_SIP_TRUCK_EMERGENCY"
    WARNINGS__DELETING_ALREADY_IN_PROGRESS = "WARNINGS.DELETING_ALREADY_IN_PROGRESS"
    WARNINGS__INVALID_IP_MASK = "WARNINGS.INVALID_IP_MASK"
    WARNINGS__TOO_MANY_BACKUPS = "WARNINGS.TOO_MANY_BACKUPS"
    WARNINGS__BACKUP_LOCATION_CONFIG_ERROR = "WARNINGS.BACKUP_LOCATION_CONFIG_ERROR"
    WARNINGS__BACKUP_NOT_FOUND_OR_INVALID = "WARNINGS.BACKUP_NOT_FOUND_OR_INVALID"
    WARNINGS__INVALID_CALL_FLOW_FILE = "WARNINGS.INVALID_CALL_FLOW_FILE"
    WARNINGS__ALREADY_EXPIRED = "WARNINGS.ALREADY_EXPIRED"
    WARNINGS__CALL_FLOW_MUST_BE_ALPHANUMERIC = "WARNINGS.CALL_FLOW_MUST_BE_ALPHANUMERIC"
    WARNINGS__EXTRACTING_OUTSIDE_THE_DESTINATION_DIRECTORY = "WARNINGS.EXTRACTING_OUTSIDE_THE_DESTINATION_DIRECTORY"
    WARNINGS__INVALID_EXTENSION_NUMBER_LENGTH = "WARNINGS.INVALID_EXTENSION_NUMBER_LENGTH"
    WARNINGS__DN_NUMBER_CANNOT_BE_USED = "WARNINGS.DN_NUMBER_CANNOT_BE_USED"
    WARNINGS__WIRESHARK_NOT_FOUND = "WARNINGS.WIRESHARK_NOT_FOUND"
    WARNINGS__CAPTURE_LOCALHOST_NOT_ALLOWED = "WARNINGS.CAPTURE_LOCALHOST_NOT_ALLOWED"
    WARNINGS__CAPTURE_ONGOING = "WARNINGS.CAPTURE_ONGOING"
    WARNINGS__CANNOT_DELETE_TRUNKS_BINDED_ERMERGENCY_NUMBER = "WARNINGS.CANNOT_DELETE_TRUNKS_BINDED_ERMERGENCY_NUMBER"
    WARNINGS__BLACKLIST_NUMBER_LIMIT_EXCEEDED = "WARNINGS.BLACKLIST_NUMBER_LIMIT_EXCEEDED"
    WARNINGS__DOUBLE_QUOTES_NOT_ALLOWED = "WARNINGS.DOUBLE_QUOTES_NOT_ALLOWED"
    WARNINGS__MCU_REQUEST_ALREADY_IN_PROGRESS = "WARNINGS.MCU_REQUEST_ALREADY_IN_PROGRESS"
    WARNINGS__MCU_LIMIT_REACHED = "WARNINGS.MCU_LIMIT_REACHED"
    WARNINGS__MCU_WEBMEETING_BRIDGE_NOT_FOUND = "WARNINGS.MCU_WEBMEETING_BRIDGE_NOT_FOUND"
    WARNINGS__MCU_REQUEST_NOT_FOUND = "WARNINGS.MCU_REQUEST_NOT_FOUND"
    WARNINGS__MCU_REQUEST_TIMEOUT = "WARNINGS.MCU_REQUEST_TIMEOUT"
    WARNINGS__SUPPORTED_MEDIA_FORMAT_WAV = "WARNINGS.SUPPORTED_MEDIA_FORMAT_WAV"
    WARNINGS__NO_SECRET_DEFINED = "WARNINGS.NO_SECRET_DEFINED"
    WARNINGS__INVALID_SECURITY_CODE = "WARNINGS.INVALID_SECURITY_CODE"
    WARNINGS__UNABLE_REACH_UPDATES_SERVER = "WARNINGS.UNABLE_REACH_UPDATES_SERVER"
    WARNINGS__ERROR_DOWNLOADING_FROM_UPDATES_SERVER = "WARNINGS.ERROR_DOWNLOADING_FROM_UPDATES_SERVER"
