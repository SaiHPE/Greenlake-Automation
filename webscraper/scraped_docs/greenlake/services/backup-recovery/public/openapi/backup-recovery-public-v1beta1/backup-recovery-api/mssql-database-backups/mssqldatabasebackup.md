---
title: "GET /backup-recovery/v1beta1/mssql-databases/{db-id}/backups/{backup-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-database-backups/mssqldatabasebackup.md"
scraped_at: "2026-06-07T06:14:03.058546+00:00Z"
---

# Get details of a MSSQL database backup.

Get detailed information for a MSSQL database backup qualified by backup-id.

Endpoint: GET /backup-recovery/v1beta1/mssql-databases/{db-id}/backups/{backup-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `db-id` (string, required)
    UUID string uniquely identifying the MSSQL Database
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `backup-id` (string, required)
    UUID string uniquely identifying the backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `associatedDatabases` (array)
    Details of the databases whose backup is also part of this backup object. On deleting this backup object the backed up data of the associated databases which is part of this backup is also deleted

  - `associatedDatabases.id` (string)
    UUID string uniquely identifying the MSSQL Database

  - `associatedDatabases.name` (string)
    Name of the MSSQL Database as configured in the application host

  - `associatedDatabases.resourceUri` (string)
    The 'self' reference for this resource.

  - `backupGranularity` (string)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `backupSetsInfo` (array)
    Information about the associated backupSetInfo. This is an array to handle application backups spanning multiple objects in the device.

  - `backupSetsInfo.backups` (array)
    Details of the individual backup objects

  - `backupSetsInfo.backups.id` (string)
    The UUID of backup object.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `backupSetsInfo.backups.objectCount` (integer)
    Number of objects on the backup.

  - `backupSetsInfo.backups.sizeInBytes` (integer)
    Size of the backup object.

  - `backupSetsInfo.backups.sourceCopyInfo` (array)

  - `backupSetsInfo.backups.sourceCopyInfo.copyType` (string)
    Specifies type of copy from where this copy was created
    Enum: "SNAPSHOT", "BACKUP"

  - `backupSetsInfo.backups.sourceCopyInfo.name` (string)
    Name of the copy.
    Example: "SnapshotDB-1"

  - `backupSetsInfo.backups.sourceCopyInfo.resourceUri` (string)
    Reference to resource.

  - `backupSetsInfo.backups.sourceCopyInfo.scsiIdentifier` (string)
    SCSI identifier of the volumes. Applicable only for snapshots

  - `backupSetsInfo.backups.sourceVolumeInfo` (object)

  - `backupSetsInfo.backups.sourceVolumeInfo.id` (string)
    The UUID of the volume.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `backupSetsInfo.backups.sourceVolumeInfo.name` (string)
    Name of the volume.
    Example: "volume-1"

  - `backupSetsInfo.backups.sourceVolumeInfo.scsiIdentifier` (string)
    SCSI identifier of the volume

  - `backupSetsInfo.sourceStorageSystemInfo` (object)
    Information about storage system where application was hosted.

  - `backupSetsInfo.sourceStorageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `backupSetsInfo.sourceStorageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `backupSetsInfo.sourceStorageSystemInfo.type` (string)
    Type of storage system.
    Enum: "NIMBLE", "3PAR", "PRIMERA", "PROTECTION_STORE_GATEWAY", "STOREONCE"

  - `backupType` (string)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `createdByInfo` (object)
    Information about the user who initiated the workflow that
created this backup.

  - `createdByInfo.id` (string)
    UUID of the user.

  - `createdByInfo.name` (string)
    Name of the user.

  - `customerId` (string)
    The customer application identifier.

  - `description` (string)
    Brief description about the application backup.

  - `expiresAt` (string)
    Absolute value of time in UTC at which the application backup expires.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application backup is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `logBackupInfo` (object)

  - `logBackupInfo.lastLogBackupTime` (string)
    Time in UTC at which the last log backup was created before the next full backup.
    Example: "2020-03-03T06:03:08.902Z"

  - `logBackupInfo.protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `logBackupInfo.protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `logBackupInfo.protectionStoreInfo.name` (string)
    Name of the protection store.

  - `logBackupInfo.protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `logBackupInfo.protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `logBackupInfo.storageSystemInfo` (object)
    Information about storage system where backup is created.

  - `logBackupInfo.storageSystemInfo.displayName` (string)
    Name of the storage system.
    Example: "atlas-dev-psg1.ind.hpecorp.net"

  - `name` (string)
    Name of the application backup.
    Example: "Nimble-DB1-snap"

  - `pointInTime` (string)
    Time in UTC at which the application backup was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `scheduleInfo` (object)
    Details about the schedule which created this snapshot.

  - `scheduleInfo.id` (string)
    Client provided id for this schedule.

  - `scheduleInfo.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `scheduleInfo.recurrence` (string)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `state` (string)
    The current state of the application backup.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "DELETE_PENDING", "IN_USE_FOR_RESTORE", "MOUNTED", "IN_USE", "PENDING_DELETE_APPROVAL"

  - `stateReason` (string)
    Brief reason for the current state of the application backup.

  - `status` (string)
    Current status of the application backup.
    Enum: "OK", "ERROR", "WARNING"

  - `updatedAt` (string)
    Time in UTC at which the object was last updated.

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


