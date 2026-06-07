---
title: "GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-group-snapshots/vpgsnapshot.md"
scraped_at: "2026-06-07T06:14:22.023732+00:00Z"
---

# Get a Volume Protection Group snapshot identified by {id}.

Get detailed information for a registered Volume Protection Group snapshot qualified by id.

Endpoint: GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `snapshot-id` (string, required)
    UUID string uniquely identifying the Volume Protection Group snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created.

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated.

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
    A brief description of the Volume Protection Group snapshot.

  - `expiresAt` (string)
    Absolute value of time in UTC at which the application.
    Example: "2020-04-03T05:03:08.900Z"

  - `individualSnapshotsInfo` (array)
    Information about the individual snapshots on volumes.

  - `individualSnapshotsInfo.id` (string)
    UUID of the resource.

  - `individualSnapshotsInfo.name` (string)
    User provided name for this snapshot.
    Example: "mySnapshot"

  - `individualSnapshotsInfo.resourceUri` (string)
    The URI reference for this resource.

  - `individualSnapshotsInfo.sizeInMiB` (integer)
    Size of the snapshot object.

  - `individualSnapshotsInfo.volumeId` (string)
    UUID of the volume.

  - `individualSnapshotsInfo.volumeName` (string)
    Name of the volume.

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `name` (string)
    A user-friendly name to identify Volume Protection Group snapshot.
    Example: "myVpgSnapshot"

  - `pointInTime` (string)
    Time in UTC at which the application snapshot was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/volume-protection-groups/8740e4f8-9f68-4b36-8f89-6bdf0808e111/snapshots/9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

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
    Current state of the snapshot
    Enum: "OK", "ERROR", "ATTACHING", "ATTACHED", "DETACHING", "DETACHED", "DISCOVERING", "DISCOVERED", "CLEANING_UP", "CLEANED_UP", "RESTORING", "CREATING", "DELETING", "DELETED", "UPDATING", "REFRESHING", "BACKUP_INITIALIZING", "PENDING_DELETE_APPROVAL"

  - `stateReason` (string)
    Brief reason for the current state of the snapshot

  - `status` (string)
    Current status of the snapshot
    Enum: "OK", "ERROR", "WARNING"

  - `storageSystemInfo` (object)
    Describes a storage system.

  - `storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `storageSystemInfo.productFamily` (string)
    Product Family
    Example: "deviceType1"

  - `storageSystemInfo.type` (string)
    Type of storage system.

  - `storageSystemSnapshotId` (string)
    Reference to the group snapshot

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


