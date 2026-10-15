---
title: "GET /backup-recovery/v1beta1/protection-jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-jobs/datamanagementjobslist.md"
scraped_at: "2026-06-07T06:14:16.024093+00:00Z"
---

# Get all the Protection Jobs.

List all the Protection Jobs.

Endpoint: GET /backup-recovery/v1beta1/protection-jobs
Version: 1.1.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set

  - `limit` (integer)
    The numbers of items to return

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.
The returned set of resources must match the criteria in the filter query parameter.
            
A comparison compares a property name to a literal. The following comparisons are supported:
“eq” : Is a property equal to value. Valid for number, boolean and string properties.
“gt” : Is a property greater than a value. Valid for number or string timestamp properties.
“lt” : Is a property less than a value. Valid for number or string timestamp properties
“in” : Is a value in a property (that is an array of strings)

Examples:
GET /backup-recovery/v1beta1/protection-jobs?filter=assetInfo/type eq 'virtualization/virtual-machine'

Filters are supported on following attributes:
* assetInfo/name
* assetInfo/type
* assetInfo/id
* assetInfo/resourceUri
* operational
* dataOrchestratorId
* protectionPolicyInfo/id
* protectionPolicyInfo/name

  - `sort` (string)
    comma separated list of properties defining the sort order

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the job.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.applicationType` (string)
    Specifies type of application that the protection applies to. It is a mandatory field.
    Enum: "VMWARE", "AWS", "HPE_ARRAY_VOLUME", "MSSQL"

  - `items.assetInfo` (object)

  - `items.assetInfo.displayName` (string)
    A user-friendly name to identify the asset

  - `items.assetInfo.id` (string)
    The UUID of either the asset or asset group.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.assetInfo.name` (string)
    Name of the asset.
    Example: "VM-Finance"

  - `items.assetInfo.resourceUri` (string)
    Reference to resource.

  - `items.assetInfo.type` (string)
    Type of asset. Supported types are virtualization/virtual-machine, virtualization/datastore, backup-recovery/virtual-machine-protection-group, virtualization/csp-machine-instance, virtualization/csp-volume, backup-recovery/csp-protection-group, backup-recovery/mssql-database-protection-group, backup-recovery/volume-protection-group, virtualization/csp-rds-instance, virtualization/csp-k8s-application
    Example: "virtualization/virtual-machine"

  - `items.associatedAssetsInfo` (array)
    An array of associated assets this job is indirectly protecting

  - `items.dataOrchestratorId` (string)
    UUID string uniquely identifying the Data Orchestrator.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.effectiveFromDateTime` (string)
    Time in UTC at which the Protection Policy assignment will be effective from.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.operational` (string)
    Enum: "ACTIVE", "SUSPENDED", "PARTIALLY_SUSPENDED", "PERMANENTLY_SUSPENDED"

  - `items.protectionPolicyInfo` (object)
    Information about the Protection Policy that was used to create the job.

  - `items.protectionPolicyInfo.id` (string)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.protectionPolicyInfo.name` (string)
    User defined name of the Protection Policy.
    Example: "Gold-Protection-Policy"

  - `items.protectionPolicyInfo.resourceUri` (string)
    Reference to resource

  - `items.protections` (array)
    An array of protection objectives

  - `items.protections.id` (string)

  - `items.protections.protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `items.protections.protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.protections.protectionStoreInfo.name` (string)
    Name of the protection store.

  - `items.protections.protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `items.protections.protectionStoreInfo.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/protection-stores/6a38acc7-e470-4ed7-b141-ca9509672da"

  - `items.protections.protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `items.protections.schedules` (array)
    Array of schedules and attributes.

  - `items.protections.schedules.executionStatuses` (array)
    List of statuses of last 5 schedule triggers

  - `items.protections.schedules.executionStatuses.errorMessage` (string)
    Captures the reason for failures in case of status being warning or Error or Skipped.

  - `items.protections.schedules.executionStatuses.status` (string)
    The current job status. The set of possible values are common across many of the different Atlas resources.
    Enum: "OK", "ERROR", "WARNING", "IN_PROGRESS", "SKIPPED"

  - `items.protections.schedules.executionStatuses.taskUri` (string)
    The storage central task that corresponds to the job

  - `items.protections.schedules.executionStatuses.timestamp` (string)
    Time in UTC when schedule was triggered
    Example: "2020-03-03T05:03:08.902Z"

  - `items.protections.schedules.expireAfter` (object)
    Copy expiration attribute, which specifies the expiration for the artifacts created.

  - `items.protections.schedules.expireAfter.unit` (string)
    Accepted units
    Enum: "HOURS", "DAYS", "WEEKS", "MONTHS", "YEARS"

  - `items.protections.schedules.expireAfter.value` (integer)
    Expiration value

  - `items.protections.schedules.lockFor` (object)
    Retention attribute, which specifies the retention period for the artifacts created. Artifacts are locked for deletion for the specified period of time.

  - `items.protections.schedules.lockFor.value` (integer)
    Retention value

  - `items.protections.schedules.name` (string)
    User provided name for this schedule

  - `items.protections.schedules.namePattern` (object)
    Format for the snapshot names

  - `items.protections.schedules.namePattern.format` (string)
    Format for the name with combination of the tokens and alphabets and numbers. "snapprefix-{SourceAssetName}-snapsuffix-{DateFormat}". Total length will be 255 characters. Possible tokens: {SourceAssetName} - Name of the source asset (DB or VM) {DateFormat} - User friendly date and time of artifact creation
    Example: "Test_{SourceAssetName}_Copy_{DateFormat}"

  - `items.protections.schedules.nextRunTime` (string)
    Time in UTC when the next schedule will trigger
    Example: "2020-03-05T05:03:08.902Z"

  - `items.protections.schedules.overrides` (object)

  - `items.protections.schedules.overrides.backupGranularity` (string)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `items.protections.schedules.overrides.consistency` (string)
    Specifies whether to create crash consistent or application consistent snapshot.
CrashConsistentOnFailure: If an application consistent snapshot fails for any reason,
with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `items.protections.schedules.overrides.createSnapshotOnFailure` (boolean)
    Specifies if the snapshot can be crash consistent in case of script execution failure.

  - `items.protections.schedules.overrides.postScriptInfo` (object)

  - `items.protections.schedules.overrides.postScriptInfo.params` (string, required)
    Parameters required to run the post-script file.

  - `items.protections.schedules.overrides.preScriptInfo` (object)

  - `items.protections.schedules.overrides.preScriptInfo.params` (string, required)
    Parameters required to run the pre-script file.

  - `items.protections.schedules.overrides.schedule` (object)
    This schema defines a schedule.

  - `items.protections.schedules.overrides.schedule.recurrence` (string, required)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `items.protections.schedules.overrides.schedule.repeatInterval` (object, required)
    Specifies the repeat interval. The interpretation varies with recurrence type. Examples: - 'BY_MINUTES' every '15' -> Every 15 minutes - 'HOURLY' every '6' on '30' -> Every 6 hours on half past of that hour - 'DAILY' every '1', startTime '06:00' -> Every day at 06:00 - 'WEEKLY' every '2' on '0' -> Every two weeks on the Monday of that week. - 'MONTHLY' every '3' on '7' -> Every three months on the 7th day of the month.

  - `items.protections.schedules.overrides.schedule.repeatInterval.every` (integer, required)
    Specifies the recurrence interval. 'BY_MINUTES' [1...60], 'HOURLY' [1...24], 'DAILY' [1...n], 'WEEKLY' [1...n], 'MONTHLY' [1...n]

  - `items.protections.schedules.overrides.schedule.repeatInterval.on` (array)
    'BY_MINUTES' N/A. 'HOURLY' specific minute [0...59]. 'DAILY' N/A, startTime can be used to specify exact hour and minute of schedule run. 'WEEKLY' specific day of the week [0...6]. This is [mon-sun]. 'MONTHLY' specific day of the month [0...31]. '0' is used to specify last day of the month.

  - `items.protections.schedules.overrides.schedule.activeTime` (object)
    Active time for the schedule. If specified then the schedule will be executed only in this period. Applicable only for 'BY_MINUTES' and 'HOURLY' schedules only.

  - `items.protections.schedules.overrides.schedule.activeTime.activeFromTime` (string, required)
    UTC time of day when schedule is active from.
    Example: "16:15"

  - `items.protections.schedules.overrides.schedule.activeTime.activeUntilTime` (string, required)
    UTC time of day when schedule is active until.
    Example: "20:15"

  - `items.protections.schedules.overrides.schedule.startTime` (string)
    Time when schedule is to be executed. Applicable for 'DAILY', 'WEEKLY' and 'MONTHLY' schedules only.
    Example: "16:35"

  - `items.protections.schedules.prevRunTime` (string)
    Time in UTC when the last schedule was triggered
    Example: "2020-03-05T05:03:08.902Z"

  - `items.protections.schedules.prevSuccessfulRunTime` (string)
    Time in UTC when the last successful schedule was triggered
    Example: "2020-03-05T05:03:08.902Z"

  - `items.protections.schedules.scheduleId` (integer)
    Client provided id for this schedule.

  - `items.protections.schedules.sourceProtectionScheduleId` (integer)
    Id of the source protection schedule. If provided this schedule becomes dependent.

  - `items.protections.schedules.vmwareOptions` (object)

  - `items.protections.schedules.vmwareOptions.includeRdmDisks` (boolean)
    Option to include RDM disks of VMs for protection.
Option needed only for datastore protection.
By default RDM disks of VMs are not included for protection
when protection is applied at datastore level.
Only RDM disks of VMs completely residing in the datastore
disks are included protection.
    Example: true

  - `items.protections.type` (string)
    Specifies type of protection. It is a mandatory field. 'SNAPSHOT' and 'REPLICATED_SNAPSHOT' types are array level snapshots.
    Enum: "SNAPSHOT", "BACKUP", "CLOUD_BACKUP", "REPLICATED_SNAPSHOT", "DATABASE_LOG_BACKUP"

  - `items.resourceUri` (string)
    The 'self' reference resource URI for the Protection Policy.

  - `offset` (integer, required)
    The number of items to skip before starting to collect the result set

  - `total` (integer)
    Total number of documents matching filter criteria.

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


