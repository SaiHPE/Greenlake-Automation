---
title: "GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgbackuplist.md"
scraped_at: "2026-06-07T06:14:18.204916+00:00Z"
---

# Get information about all virtual machine protection groups backups.

Get information about all Virtual Machine protection group backups.

Endpoint: GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups
Version: 1.1.0
Security: bearer

## Path parameters:

  - `vmpg-id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set.

  - `limit` (integer)

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.
The returned set of resources must match the criteria in the filter query parameter.

A comparision compares a property name to a literal. The comparisons supported are the following:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties.
* “in” : Is a value in a property (that is an array of strings).

Filters are supported on following attributes:
* backupType
* state
* status
* createdByInfo/id
* createdByInfo/name
* sourceCopyInfo/id
* pointInTime
* verified
* storageSystemInfo/id
* storageSystemInfo/name
* protectionStoreInfo/id
* protectionStoreInfo/name
* dataOrchestratorInfo/id
* expiresAt
* name
Examples:
* GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups?filter=backupType eq 'CLOUD_BACKUP'

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified, the
default order is ascending.

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    The number of resources in the items array.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource
    Example: "backup-recovery/virtual-machine-protection-group-backup"

  - `items.appType` (string)
    Type of the application to which the backup belongs.
    Enum: "VMWARE"

  - `items.backupSetsInfo` (array)
    Information about the associated backupSetInfo. This is an array to handle application backups spanning multiple objects in the device.

  - `items.backupSetsInfo.backups` (array)
    Details of the individual backup objects

  - `items.backupSetsInfo.backups.id` (string)
    The UUID of backup object.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.backupSetsInfo.backups.objectCount` (integer)
    Number of objects on the backup.

  - `items.backupSetsInfo.backups.sizeInBytes` (integer)
    Size of the backup object.

  - `items.backupSetsInfo.backups.sourceCopyInfo` (array)

  - `items.backupSetsInfo.backups.sourceCopyInfo.copyType` (string)
    Specifies type of copy from where this copy was created
    Enum: "SNAPSHOT", "BACKUP"

  - `items.backupSetsInfo.backups.sourceCopyInfo.name` (string)
    Name of the copy.
    Example: "SnapshotVM-1"

  - `items.backupSetsInfo.backups.sourceCopyInfo.resourceUri` (string)
    Reference to resource.

  - `items.backupSetsInfo.backups.sourceCopyInfo.scsiIdentifier` (string)
    SCSI identifier of the volumes. Applicable only for snapshots.

  - `items.backupSetsInfo.backups.sourceVolumeInfo` (object)

  - `items.backupSetsInfo.backups.sourceVolumeInfo.id` (string)
    The UUID of the volume.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.backupSetsInfo.backups.sourceVolumeInfo.name` (string)
    Name of the volume.
    Example: "volume-1"

  - `items.backupSetsInfo.backups.sourceVolumeInfo.scsiIdentifier` (string)
    SCSI identifier of the volume

  - `items.backupSetsInfo.sourceStorageSystemInfo` (object)
    Information about storage system where application was hosted.

  - `items.backupSetsInfo.sourceStorageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.backupSetsInfo.sourceStorageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `items.backupSetsInfo.sourceStorageSystemInfo.type` (string)
    Type of storage system.

  - `items.backupType` (string)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `items.consistency` (string)
    Specifies whether to create crash consistent or application consistent snapshot.
CrashConsistentOnFailure: If an application consistent snapshot fails for any reason,
with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `items.consoleUri` (string)
    The URI for console screen that displays this object.

  - `items.containsRdmDisks` (boolean)
    Indicates if the recovery point has RDM disk or not

  - `items.createdAt` (string)
    Time in UTC at which the object was created.

  - `items.createdByInfo` (object)
    Information about the user who initiated the workflow that
created this backup.

  - `items.createdByInfo.id` (string)
    UUID of the user.

  - `items.createdByInfo.name` (string)
    Name of the user.

  - `items.customerId` (string)
    The customer application identifier

  - `items.dataOrchestratorInfo` (array)

  - `items.dataOrchestratorInfo.id` (string)
    The id of the Data Orchestrator

  - `items.dataOrchestratorInfo.resourceUri` (string)
    Example: "/backup-recovery/v1beta1/data-orchestrators/613a8115-00f4-4785-831f-f3b2183cdcb7"

  - `items.dataOrchestratorInfo.type` (string)
    Example: "backup-recovery/data-orchestrator"

  - `items.description` (string)
    Brief description about the application backup.

  - `items.expiresAt` (string)
    Absolute value of time in UTC at which the application.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.lockedUntil` (string)
    Absolute value of time in UTC until which the application backup is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.name` (string)
    A user-friendly name to identify Virtual Machine Protection Group backup.
    Example: "backup1"

  - `items.pointInTime` (string)
    Time in UTC at which the application backup
was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `items.protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.protectionStoreInfo.name` (string)
    Name of the protection store.

  - `items.protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `items.protectionStoreInfo.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/protection-stores/6a38acc7-e470-4ed7-b141-ca9509672da"

  - `items.scheduleInfo` (object)
    Details about the schedule which created this snapshot.

  - `items.scheduleInfo.id` (string)
    UUID string uniquely identifying the schedule

  - `items.scheduleInfo.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `items.scheduleInfo.recurrence` (string)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `items.state` (string)
    The current state of the application backup.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "DELETE_PENDING", "IN_USE_FOR_RESTORE", "MOUNTED", "IN_USE", "PENDING_DELETE_APPROVAL"

  - `items.stateReason` (string)
    Brief reason for the current state of the application backup.

  - `items.status` (string)
    Current status of the application backup.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageSystemInfo` (object)
    Information about storage system where backup is created.

  - `items.storageSystemInfo.displayName` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `items.updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `items.verificationInfo` (object)
    Backup verification status details. Block level verification of backup with snapshot.

  - `items.verificationInfo.state` (string)
    Enum: "VERIFIED", "NOT_VERIFIED", "VERIFYING", "VERIFY_ERROR"

  - `items.verificationInfo.stateReason` (string)
    Brief reason for the verification state of backup
    Example: "Successfully completed."

  - `items.verificationInfo.status` (string)
    Backup verification state
    Enum: "OK", "ERROR", "WARNING"

  - `items.verificationInfo.verifiedAt` (string)
    Time in UTC at which the backup was verified
    Example: "2020-03-03T05:03:08.902Z"

  - `items.verified` (boolean)
    Flag indicating whether backup-set was verified or not

  - `offset` (integer, required)
    The offset specified in the offset query parameter.

  - `total` (integer)
    The total count of objects in the result set.

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

## Response 404 fields (application/json):

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


