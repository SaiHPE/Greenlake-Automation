---
title: "GET /backup-recovery/v1beta1/datastores/{id}/backups/{backup-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-backups/datastorebackup.md"
scraped_at: "2026-06-07T06:14:19.751390+00:00Z"
---

# Get details of a datastore backup.

Get detailed information for a datastore backup qualified by backup-id.

Endpoint: GET /backup-recovery/v1beta1/datastores/{id}/backups/{backup-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the datastore
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `backup-id` (string, required)
    UUID string uniquely identifying the datastore backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the datastore backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.
    Example: "backup-recovery/datastore-backup"

  - `appType` (string)
    Type of the application to which the backup belongs.
    Enum: "VMWARE"

  - `backupSetsInfo` (array)
    Information about the associated backupSetInfo. This is an array to handle application backups spanning multiple objects in the device.

  - `backupSetsInfo.backups` (array)
    Details of the individual backup objects.

  - `backupSetsInfo.backups.id` (string)
    The UUID of backup object.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `backupSetsInfo.backups.objectCount` (integer)
    Number of objects on the backup.

  - `backupSetsInfo.backups.sizeInMib` (integer)
    Size of the backup in mega bytes.
    Example: 614400

  - `backupSetsInfo.backups.sourceCopyInfo` (array)

  - `backupSetsInfo.backups.sourceCopyInfo.copyType` (string)
    Specifies type of copy from where this copy was created.
    Enum: "SNAPSHOT", "BACKUP"

  - `backupSetsInfo.backups.sourceCopyInfo.name` (string)
    Name of the copy.
    Example: "SnapshotVM-1"

  - `backupSetsInfo.backups.sourceCopyInfo.resourceUri` (string)
    Reference to resource.

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
    The 'self' reference for this resource.

  - `backupSetsInfo.backups.sourceVolumeInfo.scsiIdentifier` (string)
    SCSI identifier of the volume.

  - `backupSetsInfo.sourceStorageSystemInfo` (object)
    Information about storage system where application was hosted.

  - `backupSetsInfo.sourceStorageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `backupSetsInfo.sourceStorageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `backupSetsInfo.sourceStorageSystemInfo.storageSystemType` (string)
    Type of storage system.
    Enum: "HPE_NIMBLE", "HPE_PRIMERA", "HPE_ALLETRA_STORAGE_MP"

  - `backupSetsInfo.sourceStorageSystemInfo.type` (string)
    Type of storage system.

  - `backupType` (string)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `consistency` (string)
    Specifies whether to create crash consistent or application consistent snapshot.
CrashConsistentOnFailure: If an application consistent snapshot fails for any reason,
with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `consoleUri` (string)
    The URI for console screen that displays this object.

  - `containsRdmDisks` (boolean)
    Indicates if the recovery point has RDM disk or not.

  - `createdAt` (string)
    Time in UTC at which the object was created.

  - `createdByInfo` (object)
    Information about the user who initiated the workflow that
created this backup.

  - `createdByInfo.id` (string)
    UUID of the user.

  - `createdByInfo.name` (string)
    Name of the user.

  - `customerId` (string)
    The customer application identifier

  - `dataOrchestratorInfo` (array)

  - `dataOrchestratorInfo.id` (string)
    The id of the Data Orchestrator.

  - `dataOrchestratorInfo.resourceUri` (string)
    Example: "/backup-recovery/v1beta1/data-orchestrators/613a8115-00f4-4785-831f-f3b2183cdcb7"

  - `dataOrchestratorInfo.type` (string)
    Example: "backup-recovery/data-orchestrator"

  - `description` (string)
    Brief description about the application backup.

  - `expiresAt` (string)
    Absolute value of time in UTC when the application snapshot expires.

  - `fullBackup` (boolean)

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot remains locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `name` (string)
    A user-friendly name to identify datastore backup.
    Example: "backup1"

  - `pointInTime` (string)
    Time in UTC at which the application backup
was created on the device.
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

  - `protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `scheduleInfo` (object)
    Details about the schedule that created this snapshot.

  - `scheduleInfo.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `scheduleInfo.recurrence` (string)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `scheduleInfo.scheduleId` (integer)
    Client provided id for this schedule.

  - `state` (string)
    The current state of the application backup.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "DELETE_PENDING", "IN_USE_FOR_RESTORE", "MOUNTED", "IN_USE", "PENDING_DELETE_APPROVAL"

  - `stateReason` (string)
    Brief reason for the current state of the application backup.

  - `status` (string)
    Current status of the application backup.
    Enum: "OK", "ERROR", "WARNING"

  - `storageSystemInfo` (object)
    Information about storage system where backup is created.

  - `storageSystemInfo.displayName` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `verificationInfo` (object)
    Backup verification status details. Block level verification of backup with snapshot.

  - `verificationInfo.state` (string)
    Enum: "VERIFIED", "NOT_VERIFIED", "VERIFYING", "VERIFY_ERROR"

  - `verificationInfo.stateReason` (string)
    Brief reason for the verification state of backup.
    Example: "Successfully completed."

  - `verificationInfo.status` (string)
    Backup verification state.
    Enum: "OK", "ERROR", "WARNING"

  - `verificationInfo.verifiedAt` (string)
    Time in UTC at which the backup was verified.
    Example: "2020-03-03T05:03:08.902Z"

  - `verified` (boolean)
    Flag indicating whether the backup-set was verified or not.

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


