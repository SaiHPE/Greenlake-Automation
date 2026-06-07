---
title: "GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackuplist.md"
scraped_at: "2026-06-07T06:14:21.292262+00:00Z"
---

# Get all Volume Protection Group backups.

List all Volume Protection Group backups.

Endpoint: GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

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
GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups?filter=backupType eq 'CLOUD_BACKUP'

Filters are supported on following attributes:
* backupType
* state
* status
* sourceCopyInfo/id
* pointInTime
* storageSystemInfo/id
* storageSystemInfo/name
* protectionStoreInfo/id
* protectionStoreInfo/name

  - `sort` (string)
    Comma separated list of properties defining the sort order

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the Volume Protection Group backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created.

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `items.backupSetsInfo` (array)
    Information about the associated backupSetInfo. This is an array to handle application backups spanning multiple objects in the device.

  - `items.backupSetsInfo.backups` (array)
    Details of the individual backup objects

  - `items.backupSetsInfo.backups.id` (string)
    The UUID of backup object.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.backupSetsInfo.backups.mountState` (string)
    Mount state of the backup
    Enum: "UNATTACHED", "ATTACHING", "ATTACHED", "DETACHING"

  - `items.backupSetsInfo.backups.mountedHostsIqn` (array)
    list of IQN of mounted hosts

  - `items.backupSetsInfo.backups.objectCount` (integer)
    Number of objects on the backup.

  - `items.backupSetsInfo.backups.sizeInBytes` (integer)
    Size of the backup object.

  - `items.backupSetsInfo.backups.sourceCopyInfo` (object)

  - `items.backupSetsInfo.backups.sourceCopyInfo.copyType` (string)
    Specifies type of copy from where this copy was created
    Enum: "SNAPSHOT", "BACKUP"

  - `items.backupSetsInfo.backups.sourceCopyInfo.name` (string)
    Name of the copy.
    Example: "SnapshotVM-1"

  - `items.backupSetsInfo.backups.sourceCopyInfo.scsiIdentifier` (string)
    SCSI identifier of the volumes. Applicable only for snapshots.

  - `items.backupSetsInfo.backups.sourceVolumeInfo` (object)

  - `items.backupSetsInfo.backups.sourceVolumeInfo.id` (string)
    The UUID of the volume.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.backupSetsInfo.backups.sourceVolumeInfo.name` (string)
    Name of the volume.
    Example: "volume-1"

  - `items.backupSetsInfo.backups.sourceVolumeInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.backupSetsInfo.backups.sourceVolumeInfo.scsiIdentifier` (string)
    SCSI identifier of the volume

  - `items.backupSetsInfo.sourceStorageSystemInfo` (object)
    Describes a storage system.

  - `items.backupSetsInfo.sourceStorageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.backupSetsInfo.sourceStorageSystemInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `items.backupSetsInfo.sourceStorageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `items.backupSetsInfo.sourceStorageSystemInfo.type` (string)
    Type of storage system.

  - `items.backupType` (string)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `items.createdByInfo` (object)
    Information about the user who initiated the workflow that
created this snapshot or Protection Policy.

  - `items.createdByInfo.id` (string)
    UUID of the user.

  - `items.createdByInfo.name` (string)
    Name of the user.

  - `items.customerId` (string)
    The customer application identifier.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.description` (string)
    A brief description of the Volume Protection Group backup.

  - `items.expiresAt` (string)
    Absolute value of time in UTC at which the application expires.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.lockedUntil` (string)
    Absolute value of time in UTC until which the application backup is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.name` (string)
    A user-friendly name to identify Volume Protection Group backup.
    Example: "myVpgBackup"

  - `items.pointInTime` (string)
    Time in UTC at which the application backup was created on the device.
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

  - `items.protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `items.scheduleInfo` (object)
    Details about the schedule which created this snapshot.

  - `items.scheduleInfo.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `items.scheduleInfo.recurrence` (string)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `items.scheduleInfo.scheduleId` (integer)
    Client provided id for this schedule.

  - `items.state` (string)
    Current state of the backup
    Enum: "OK", "ERROR", "CREATING", "RESTORING", "PARTIAL", "DELETING", "DELETED", "UPDATING", "REFRESHING", "PENDING_DELETE_APPROVAL", "IN_USE_FOR_MOUNT"

  - `items.stateReason` (string)
    Brief reason for the current state of the backup

  - `items.status` (string)
    Current status of the backup
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageSystemInfo` (object)
    Describes a storage system.

  - `items.storageSystemInfo.productFamily` (string)
    Product Family
    Example: "deviceType1"

  - `items.vpgInfo` (object)
    Information about the Volume Protection Group.

  - `items.vpgInfo.id` (string)
    UUID string uniquely identifying the Volume Protection Group.

  - `items.vpgInfo.name` (string)
    Name of the Volume Protection Group.

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


