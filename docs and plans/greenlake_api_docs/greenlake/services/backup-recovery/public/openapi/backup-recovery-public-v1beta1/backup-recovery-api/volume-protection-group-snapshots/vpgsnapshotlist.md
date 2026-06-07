---
title: "GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/volume-protection-group-snapshots/vpgsnapshotlist.md"
scraped_at: "2026-06-07T06:14:10.382214+00:00Z"
---

# Get all Volume Protection Group snapshots.

List all Volume Protection Group snapshots.

Endpoint: GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots
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
GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots?filter=storageSystemInfo/name eq 'myStorageSystem'

Filters are supported on following attributes:
* state
* status
* storageSystemInfo/id
* storageSystemInfo/name
* pointInTime

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
    UUID string uniquely identifying the Volume Protection Group snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created.

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated.

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
    A brief description of the Volume Protection Group snapshot.

  - `items.expiresAt` (string)
    Absolute value of time in UTC at which the application.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.individualSnapshotsInfo` (array)
    Information about the individual snapshots on volumes.

  - `items.individualSnapshotsInfo.id` (string)
    UUID of the resource.

  - `items.individualSnapshotsInfo.name` (string)
    User provided name for this snapshot.
    Example: "mySnapshot"

  - `items.individualSnapshotsInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.individualSnapshotsInfo.sizeInMiB` (integer)
    Size of the snapshot object.

  - `items.individualSnapshotsInfo.volumeId` (string)
    UUID of the volume.

  - `items.individualSnapshotsInfo.volumeName` (string)
    Name of the volume.

  - `items.lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.name` (string)
    A user-friendly name to identify Volume Protection Group snapshot.
    Example: "myVpgSnapshot"

  - `items.pointInTime` (string)
    Time in UTC at which the application snapshot was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/volume-protection-groups/8740e4f8-9f68-4b36-8f89-6bdf0808e111/snapshots/9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

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
    Current state of the snapshot
    Enum: "OK", "ERROR", "ATTACHING", "ATTACHED", "DETACHING", "DETACHED", "DISCOVERING", "DISCOVERED", "CLEANING_UP", "CLEANED_UP", "RESTORING", "CREATING", "DELETING", "DELETED", "UPDATING", "REFRESHING", "BACKUP_INITIALIZING", "PENDING_DELETE_APPROVAL"

  - `items.stateReason` (string)
    Brief reason for the current state of the snapshot

  - `items.status` (string)
    Current status of the snapshot
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageSystemInfo` (object)
    Describes a storage system.

  - `items.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `items.storageSystemInfo.productFamily` (string)
    Product Family
    Example: "deviceType1"

  - `items.storageSystemInfo.type` (string)
    Type of storage system.

  - `items.storageSystemSnapshotId` (string)
    Reference to the group snapshot

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


