---
title: "GET /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/datastore-snapshots/datastoresnapshot.md"
scraped_at: "2026-06-07T06:14:20.423571+00:00Z"
---

# Get details of a datastore snapshot.

Get detailed information for a datastore snapshot qualified by snapshot-id.

Endpoint: GET /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the datastore
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
    Example: "backup-recovery/datastore-snapshot"

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
created this snapshot or protection policy.

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
    Brief description about the application snapshot.

  - `expiresAt` (string)
    Absolute value of time in UTC when the application snapshot expires.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot remains locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `name` (string)
    Name of the application snapshot.
    Example: "Nimble-DS1-snap"

  - `pointInTime` (string)
    Time in UTC at which the application snapshot was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/datastores/id/snapshots/id/"

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

  - `storageSystemsInfo` (object)
    Describes a storage system.

  - `storageSystemsInfo.displayName` (string)
    A user-friendly name that identifies the storage system.
    Example: "my-dev-3par1.ind.hpecorp.net"

  - `storageSystemsInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `storageSystemsInfo.managed` (boolean)
    Specify if the storage system is registered.

  - `storageSystemsInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `storageSystemsInfo.resourceUri` (string)
    The URI reference for this resource.
    Example: "/storage-fleet/v1/storage-systems/{uuid}"

  - `storageSystemsInfo.serialNumber` (string)
    Serial number of the storage system.
    Example: "AF-10122"

  - `storageSystemsInfo.storageSystemType` (string)
    Type of storage system.
    Enum: "HPE_NIMBLE", "HPE_PRIMERA", "HPE_ALLETRA_STORAGE_MP"

  - `storageSystemsInfo.vendorName` (string)
    Storage system provider name.
    Example: "hpe"

  - `updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `volumesSnapshotInfo` (array)
    Details of the associated snapshot volumes.

  - `volumesSnapshotInfo.id` (string)
    UUID string uniquely identifying the snapshot volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesSnapshotInfo.name` (string)
    Name of the snapshot volume.
    Example: "ATL-0106052-ro-210503202357032"

  - `volumesSnapshotInfo.resourceUri` (string)
    Reference to resource.

  - `volumesSnapshotInfo.scsiIdentifier` (string)
    SCSI identifier of the volume or snapshot .
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `volumesSnapshotInfo.sizeInMib` (integer)
    Size of the volume or snapshot in mega bytes.
    Example: 614400

  - `volumesSnapshotInfo.storageSystemInfo` (object)
    Describes a storage system.

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


