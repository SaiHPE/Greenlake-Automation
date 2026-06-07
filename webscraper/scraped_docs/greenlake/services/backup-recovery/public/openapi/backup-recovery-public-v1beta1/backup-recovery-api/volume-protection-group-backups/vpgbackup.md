---
title: "GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackup.md"
scraped_at: "2026-06-07T06:14:10.385003+00:00Z"
---

# Get a Volume Protection Group backup identified by {id}.

Get detailed information for a registered Volume Protection Group backup qualified by id.

Endpoint: GET /backup-recovery/v1beta1/volume-protection-groups/{id}/backups/{backup-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `backup-id` (string, required)
    UUID string uniquely identifying the Volume Protection Group backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created.

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `backupSetsInfo` (array)
    Information about the associated backupSetInfo. This is an array to handle application backups spanning multiple objects in the device.

  - `backupSetsInfo.backups` (array)
    Details of the individual backup objects

  - `backupSetsInfo.backups.id` (string)
    The UUID of backup object.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `backupSetsInfo.backups.mountState` (string)
    Mount state of the backup
    Enum: "UNATTACHED", "ATTACHING", "ATTACHED", "DETACHING"

  - `backupSetsInfo.backups.mountedHostsIqn` (array)
    list of IQN of mounted hosts

  - `backupSetsInfo.backups.objectCount` (integer)
    Number of objects on the backup.

  - `backupSetsInfo.backups.sizeInBytes` (integer)
    Size of the backup object.

  - `backupSetsInfo.backups.sourceCopyInfo` (object)

  - `backupSetsInfo.backups.sourceCopyInfo.copyType` (string)
    Specifies type of copy from where this copy was created
    Enum: "SNAPSHOT", "BACKUP"

  - `backupSetsInfo.backups.sourceCopyInfo.name` (string)
    Name of the copy.
    Example: "SnapshotVM-1"

  - `backupSetsInfo.backups.sourceCopyInfo.scsiIdentifier` (string)
    SCSI identifier of the volumes. Applicable only for snapshots.

  - `backupSetsInfo.backups.sourceVolumeInfo` (object)

  - `backupSetsInfo.backups.sourceVolumeInfo.id` (string)
    The UUID of the volume.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `backupSetsInfo.backups.sourceVolumeInfo.name` (string)
    Name of the volume.
    Example: "volume-1"

  - `backupSetsInfo.backups.sourceVolumeInfo.resourceUri` (string)
    The URI reference for this resource.

  - `backupSetsInfo.backups.sourceVolumeInfo.scsiIdentifier` (string)
    SCSI identifier of the volume

  - `backupSetsInfo.sourceStorageSystemInfo` (object)
    Describes a storage system.

  - `backupSetsInfo.sourceStorageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `backupSetsInfo.sourceStorageSystemInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `backupSetsInfo.sourceStorageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `backupSetsInfo.sourceStorageSystemInfo.type` (string)
    Type of storage system.

  - `backupType` (string)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `createdByInfo` (object)
    Information about the user who initiated the workflow that
created this snapshot or Protection Policy.

  - `createdByInfo.id` (string)
    UUID of the user.

  - `createdByInfo.name` (string)
    Name of the user.

  - `customerId` (string)
    The customer application identifier.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `description` (string)
    A brief description of the Volume Protection Group backup.

  - `expiresAt` (string)
    Absolute value of time in UTC at which the application expires.
    Example: "2020-04-03T05:03:08.900Z"

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application backup is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `name` (string)
    A user-friendly name to identify Volume Protection Group backup.
    Example: "myVpgBackup"

  - `pointInTime` (string)
    Time in UTC at which the application backup was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `protectionStoreInfo.name` (string)
    Name of the protection store.

  - `protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `protectionStoreInfo.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/protection-stores/6a38acc7-e470-4ed7-b141-ca9509672da"

  - `protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `scheduleInfo` (object)
    Details about the schedule which created this snapshot.

  - `scheduleInfo.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `scheduleInfo.recurrence` (string)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `scheduleInfo.scheduleId` (integer)
    Client provided id for this schedule.

  - `state` (string)
    Current state of the backup
    Enum: "OK", "ERROR", "CREATING", "RESTORING", "PARTIAL", "DELETING", "DELETED", "UPDATING", "REFRESHING", "PENDING_DELETE_APPROVAL", "IN_USE_FOR_MOUNT"

  - `stateReason` (string)
    Brief reason for the current state of the backup

  - `status` (string)
    Current status of the backup
    Enum: "OK", "ERROR", "WARNING"

  - `storageSystemInfo` (object)
    Describes a storage system.

  - `storageSystemInfo.productFamily` (string)
    Product Family
    Example: "deviceType1"

  - `vpgInfo` (object)
    Information about the Volume Protection Group.

  - `vpgInfo.id` (string)
    UUID string uniquely identifying the Volume Protection Group.

  - `vpgInfo.name` (string)
    Name of the Volume Protection Group.

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


