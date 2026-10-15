---
title: "GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots/{snapshot-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-database-snapshots/mssqldatabasesnapshot.md"
scraped_at: "2026-06-07T06:14:03.704599+00:00Z"
---

# Get details of a MSSQL database snapshot.

Get detailed information for a MSSQL database snapshot qualified by snapshot-id.

Endpoint: GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots/{snapshot-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `db-id` (string, required)
    UUID string uniquely identifying the MSSQL Database
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `snapshot-id` (string, required)
    UUID string uniquely identifying the snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `associatedDatabases` (array)
    Details of the databases whose backup is also part of this snapshot object. On deleting this snapshot object the backed up data of the associated databases which is part of this snapshot is also deleted

  - `associatedDatabases.id` (string)
    UUID string uniquely identifying the MSSQL Database

  - `associatedDatabases.name` (string)
    Name of the MSSQL Database as configured in the application host

  - `associatedDatabases.resourceUri` (string)
    The 'self' reference for this resource.

  - `createdByInfo` (object)
    Information about the user who initiated the workflow that
created this snapshot or template.

  - `createdByInfo.id` (string)
    UUID of the user.

  - `createdByInfo.name` (string)
    Name of the user.

  - `customerId` (string)
    The customer application identifier.

  - `description` (string)
    Brief description about the application snapshot.

  - `expiresAt` (string)
    Absolute value of time in UTC at which the snapshot expires.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot is locked.
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

  - `logBackupInfo.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `logBackupInfo.storageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `logBackupInfo.storageSystemInfo.type` (string)
    Type of storage system.
    Enum: "PROTECTION_STORE_GATEWAY", "STOREONCE"

  - `name` (string)
    Name of the application snapshot.
    Example: "Nimble-DB1-snap"

  - `pointInTime` (string)
    Time in UTC at which the application snapshot was created on the device.
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

  - `snapshotType` (string)
    Enum: "SNAPSHOT"

  - `state` (string)
    The current state of the application snapshot.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "DELETE_PENDING", "IN_USE", "PENDING_DELETE_APPROVAL"

  - `stateReason` (string)
    Brief reason for the current state of the application snapshot.

  - `status` (string)
    Current status of the application snapshot.
    Enum: "OK", "ERROR", "WARNING"

  - `storageSystemsInfo` (array)
    Storage info details of this MSSQL Database

  - `storageSystemsInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `storageSystemsInfo.resourceUri` (string)
    The URI reference for this resource.

  - `updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `volumesSnapshotInfo` (array)
    Details of the associated snapshot volumes

  - `volumesSnapshotInfo.id` (string)
    UUID string uniquely identifying the snapshot volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesSnapshotInfo.name` (string)
    Name of the snapshot volume.
    Example: "ATL-0106052-ro-210503202357032"

  - `volumesSnapshotInfo.scsiIdentifier` (string)
    SCSI identifier of the volume or snapshot .
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `volumesSnapshotInfo.sizeInMib` (integer)
    Size of the volume or snapshot in mega bytes.
    Example: 614400

  - `volumesSnapshotInfo.storageSystemInfo` (object)
    Describes a storage system.

  - `volumesSnapshotInfo.storageSystemInfo.displayName` (string)
    A user-friendly name that identifies the storage system.
    Example: "my-dev-3par1.ind.hpecorp.net"

  - `volumesSnapshotInfo.storageSystemInfo.managed` (boolean)
    Specify if the storage system is registered.

  - `volumesSnapshotInfo.storageSystemInfo.serialNumber` (string)
    Serial number of the storage system.
    Example: "AF-10122"

  - `volumesSnapshotInfo.storageSystemInfo.storageSystemType` (string)
    Type of storage system.
    Enum: "HPE_NIMBLE", "HPE_PRIMERA", "HPE_ALLETRA_STORAGE_MP"

  - `volumesSnapshotInfo.storageSystemInfo.vendorName` (string)
    Storage system provider name.
    Example: "hpe"

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


