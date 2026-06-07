---
title: "PATCH /backup-recovery/v1beta1/protection-policies/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/protection-policies/datamanagementtemplateupdate.md"
scraped_at: "2026-06-07T06:14:05.379972+00:00Z"
---

# Update an assigned Protection Policy.

Update an assigned Protection Policy for data protection.

Endpoint: PATCH /backup-recovery/v1beta1/protection-policies/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

## Request fields (application/merge-patch+json):

  - `description` (string)
    A brief description about the Protection Policy.

  - `name` (string)
    User defined name of the Protection Policy.

  - `protections` (array)
    An array of protection objectives

  - `protections.id` (string)
    Example: "2a1172be-4281-44f9-848b-9c3f86378b13"

  - `protections.schedules` (array)
    An array of protection requirements specifying the frequency of creation, targets, retention and expiry related attributes.

  - `protections.schedules.scheduleId` (integer, required)
    Client provided id for this schedule.

  - `protections.schedules.schedule` (object, required)
    This schema defines a schedule.

  - `protections.schedules.schedule.recurrence` (string, required)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `protections.schedules.schedule.repeatInterval` (object, required)
    Specifies the repeat interval. The interpretation varies with recurrence type. Examples: - 'BY_MINUTES' every '15' -> Every 15 minutes - 'HOURLY' every '6' on '30' -> Every 6 hours on half past of that hour - 'DAILY' every '1', startTime '06:00' -> Every day at 06:00 - 'WEEKLY' every '2' on '0' -> Every two weeks on the Monday of that week. - 'MONTHLY' every '3' on '7' -> Every three months on the 7th day of the month.

  - `protections.schedules.schedule.repeatInterval.every` (integer, required)
    Specifies the recurrence interval. 'BY_MINUTES' [1...60], 'HOURLY' [1...24], 'DAILY' [1...n], 'WEEKLY' [1...n], 'MONTHLY' [1...n]

  - `protections.schedules.schedule.repeatInterval.on` (array)
    'BY_MINUTES' N/A. 'HOURLY' specific minute [0...59]. 'DAILY' N/A, startTime can be used to specify exact hour and minute of schedule run. 'WEEKLY' specific day of the week [0...6]. This is [mon-sun]. 'MONTHLY' specific day of the month [0...31]. '0' is used to specify last day of the month.

  - `protections.schedules.schedule.activeTime` (object)
    Active time for the schedule. If specified then the schedule will be executed only in this period. Applicable only for 'BY_MINUTES' and 'HOURLY' schedules only.

  - `protections.schedules.schedule.activeTime.activeFromTime` (string, required)
    UTC time of day when schedule is active from.
    Example: "16:15"

  - `protections.schedules.schedule.activeTime.activeUntilTime` (string, required)
    UTC time of day when schedule is active until.
    Example: "20:15"

  - `protections.schedules.schedule.startTime` (string)
    Time when schedule is to be executed. Applicable for 'DAILY', 'WEEKLY' and 'MONTHLY' schedules only.
    Example: "16:35"

  - `protections.schedules.expireAfter` (object)
    Copy expiration attribute, which specifies the expiration for the artifacts created.

  - `protections.schedules.expireAfter.unit` (string)
    Accepted units
    Enum: "HOURS", "DAYS", "WEEKS", "MONTHS", "YEARS"

  - `protections.schedules.expireAfter.value` (integer)
    Expiration value

  - `protections.schedules.lockFor` (object)
    Retention attribute, which specifies the retention period for the artifacts created. Artifacts are locked for deletion for the specified period of time.

  - `protections.schedules.lockFor.value` (integer)
    Retention value

  - `protections.schedules.name` (string)
    User provided name for this schedule

  - `protections.schedules.namePattern` (object)
    Format for the snapshot names

  - `protections.schedules.namePattern.format` (string)
    Format for the name with combination of the tokens and alphabets and numbers. "snapprefix-{SourceAssetName}-snapsuffix-{DateFormat}". Total length will be 255 characters. Possible tokens: {SourceAssetName} - Name of the source asset (DB or VM) {DateFormat} - User friendly date and time of artifact creation
    Example: "Test_{SourceAssetName}_Copy_{DateFormat}"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `type` (string, required)
    The type of resource.

  - `applicationType` (string)
    Specifies type of application that the protection applies to. It is a mandatory field.
    Enum: "VMWARE", "AWS", "HPE_ARRAY_VOLUME", "MSSQL"

  - `assigned` (boolean)
    Boolean indicating if the Protection Policy has been used to create Protection Jobs

  - `consoleUri` (string)
    The URI for console screen that displays this object.

  - `createdAt` (string)
    UTC time when the Protection Policy was created.
    Example: "2019-07-21T17:32:28Z"

  - `createdBy` (object)
    Information about the user who created the Protection Policy.

  - `createdBy.id` (string)
    Example: "2a1172be-4281-44f9-848b-9c3f86378b13"

  - `createdBy.name` (string)
    Example: "Admin"

  - `description` (string)
    A brief description about the Protection Policy.
    Example: "Protection Policy protecting Finance department's Virtual Machines or datastores."

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `name` (string)
    User defined name of the Protection Policy.
    Example: "Gold-Protection-Policy"

  - `protectionJobsInfo` (array)
    Details of the Protection Jobs using the Protection Policy

  - `protectionJobsInfo.assetInfo` (object)

  - `protectionJobsInfo.assetInfo.displayName` (string)
    A user-friendly name to identify the asset

  - `protectionJobsInfo.assetInfo.id` (string)
    The UUID of either the asset or asset group.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `protectionJobsInfo.assetInfo.name` (string)
    Name of the asset.
    Example: "VM-Finance"

  - `protectionJobsInfo.assetInfo.resourceUri` (string)
    Reference to resource.

  - `protectionJobsInfo.assetInfo.type` (string)
    Type of asset. Supported types are virtualization/virtual-machine, virtualization/datastore, backup-recovery/virtual-machine-protection-group, virtualization/csp-machine-instance, virtualization/csp-volume, backup-recovery/csp-protection-group, backup-recovery/mssql-database-protection-group, backup-recovery/volume-protection-group, virtualization/csp-rds-instance, virtualization/csp-k8s-application
    Example: "virtualization/virtual-machine"

  - `protections` (array)
    An array of protection objectives.

  - `protections.protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `protections.protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `protections.protectionStoreInfo.name` (string)
    Name of the protection store.

  - `protections.protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `protections.protectionStoreInfo.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/protection-stores/6a38acc7-e470-4ed7-b141-ca9509672da"

  - `protections.protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `protections.schedules` (array)
    Array of schedules and attributes.

  - `protections.schedules.expireAfter` (object)
    Copy expiration attribute, which specifies the expiration for the artifacts created.

  - `protections.schedules.expireAfter.unit` (string)
    Accepted units
    Enum: "HOURS", "DAYS", "WEEKS", "MONTHS", "YEARS"

  - `protections.schedules.expireAfter.value` (integer)
    Expiration value

  - `protections.schedules.lockFor` (object)
    Retention attribute, which specifies the retention period for the artifacts created. Artifacts are locked for deletion for the specified period of time.

  - `protections.schedules.lockFor.value` (integer)
    Retention value

  - `protections.schedules.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `protections.schedules.namePattern` (object)
    Format for the snapshot names

  - `protections.schedules.namePattern.format` (string)
    Format for the name with combination of the tokens and alphabets and numbers. "snapprefix-{SourceAssetName}-snapsuffix-{DateFormat}". Total length will be 255 characters. Possible tokens: {SourceAssetName} - Name of the source asset (DB or VM) {DateFormat} - User friendly date and time of artifact creation
    Example: "Test_{SourceAssetName}_Copy_{DateFormat}"

  - `protections.schedules.postScriptInfo` (object)
    Details required to run the post-script.

  - `protections.schedules.postScriptInfo.path` (string, required)
    Specifies the absolute path of the post-script file.

  - `protections.schedules.postScriptInfo.hostId` (string)
    Id of the host

  - `protections.schedules.postScriptInfo.params` (string)
    Parameters required to run the post-script file.

  - `protections.schedules.postScriptInfo.timeoutInSeconds` (integer)
    Timeout period while running the post-script.

  - `protections.schedules.preScriptInfo` (object)
    Details required to run the pre-script.

  - `protections.schedules.preScriptInfo.path` (string, required)
    Specifies the absolute path of the pre-script file.

  - `protections.schedules.preScriptInfo.params` (string)
    Parameters required to run the pre-script file.

  - `protections.schedules.preScriptInfo.timeoutInSeconds` (integer)
    Timeout period while running the pre-script.

  - `protections.schedules.schedule` (object)
    This schema defines a schedule.

  - `protections.schedules.schedule.recurrence` (string, required)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `protections.schedules.schedule.repeatInterval` (object, required)
    Specifies the repeat interval. The interpretation varies with recurrence type. Examples: - 'BY_MINUTES' every '15' -> Every 15 minutes - 'HOURLY' every '6' on '30' -> Every 6 hours on half past of that hour - 'DAILY' every '1', startTime '06:00' -> Every day at 06:00 - 'WEEKLY' every '2' on '0' -> Every two weeks on the Monday of that week. - 'MONTHLY' every '3' on '7' -> Every three months on the 7th day of the month.

  - `protections.schedules.schedule.repeatInterval.every` (integer, required)
    Specifies the recurrence interval. 'BY_MINUTES' [1...60], 'HOURLY' [1...24], 'DAILY' [1...n], 'WEEKLY' [1...n], 'MONTHLY' [1...n]

  - `protections.schedules.schedule.repeatInterval.on` (array)
    'BY_MINUTES' N/A. 'HOURLY' specific minute [0...59]. 'DAILY' N/A, startTime can be used to specify exact hour and minute of schedule run. 'WEEKLY' specific day of the week [0...6]. This is [mon-sun]. 'MONTHLY' specific day of the month [0...31]. '0' is used to specify last day of the month.

  - `protections.schedules.schedule.activeTime` (object)
    Active time for the schedule. If specified then the schedule will be executed only in this period. Applicable only for 'BY_MINUTES' and 'HOURLY' schedules only.

  - `protections.schedules.schedule.activeTime.activeFromTime` (string, required)
    UTC time of day when schedule is active from.
    Example: "16:15"

  - `protections.schedules.schedule.activeTime.activeUntilTime` (string, required)
    UTC time of day when schedule is active until.
    Example: "20:15"

  - `protections.schedules.schedule.startTime` (string)
    Time when schedule is to be executed. Applicable for 'DAILY', 'WEEKLY' and 'MONTHLY' schedules only.
    Example: "16:35"

  - `protections.schedules.scheduleId` (integer)
    Client provided id for this schedule.

  - `protections.schedules.sourceProtectionScheduleId` (integer)
    Id of the source protection schedule. If provided this schedule becomes dependent.

  - `protections.type` (string)
    Specifies type of protection. It is a mandatory field. 'SNAPSHOT' and 'REPLICATED_SNAPSHOT' types are array level snapshots.
    Enum: "SNAPSHOT", "BACKUP", "CLOUD_BACKUP", "REPLICATED_SNAPSHOT", "DATABASE_LOG_BACKUP"

  - `resourceUri` (string)
    The 'self' reference resource URI for the Protection Policy.

  - `updatedAt` (string)
    UTC time when the Protection Policy was last updated.
    Example: "2019-07-21T17:32:28Z"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


