---
title: "GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgsnapshotlist.md"
scraped_at: "2026-06-07T06:14:07.823070+00:00Z"
---

# Get information about all virtual machine protection groups snapshots.

Get information about all virtual machine protection groups snapshots.

Endpoint: GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots
Version: 1.1.0
Security: bearer

## Path parameters:

  - `vmpg-id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set

  - `limit` (integer)
    The numbers of items to return

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.
The returned set of resources must match the criteria in the filter query parameter.

A comparision compares a property name to a literal. The comparisons supported are the following:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Filters are supported on following attributes:
* snapshotType
* state
* status
* createdByInfo/id
* createdByInfo/name
* storageSystemsInfo/id
* storageSystemsInfo/storageSystemType
* storageSystemsInfo/name
* consistency
* pointInTime
* dataOrchestratorInfo/id
* expiresAt
* name
Examples:
* GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots?filter=consistency eq 'APPLICATION'

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
    UUID string uniquely identifying the snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource
    Example: "backup-recovery/virtual-machine-protection-group-snapshot"

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
created this snapshot or protection policy.

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
    Brief description about the application snapshot.

  - `items.expiresAt` (string)
    Absolute value of time in UTC at which the application.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.name` (string)
    Name of the application snapshot.
    Example: "Nimble-DS1-snap"

  - `items.pointInTime` (string)
    Time in UTC at which the application snapshot was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/virtual-machine-protection-groups/id/snapshots/id/"

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

  - `items.snapshotType` (string)
    Enum: "SNAPSHOT"

  - `items.state` (string)
    The current state of the application snapshot.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "DELETE_PENDING", "IN_USE", "PENDING_DELETE_APPROVAL"

  - `items.stateReason` (string)
    Brief reason for the current state of the application snapshot.

  - `items.status` (string)
    Current status of the application snapshot.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageSystemsInfo` (object)
    Describes a storage system.

  - `items.storageSystemsInfo.displayName` (string)
    A user-friendly name that identifies the storage system.
    Example: "my-dev-3par1.ind.hpecorp.net"

  - `items.storageSystemsInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.storageSystemsInfo.managed` (boolean)
    Specify if the storage system is registered.

  - `items.storageSystemsInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `items.storageSystemsInfo.resourceUri` (string)
    The URI reference for this resource.
    Example: "/storage-fleet/v1/storage-systems/{uuid}"

  - `items.storageSystemsInfo.serialNumber` (string)
    Serial number of the storage system.
    Example: "AF-10122"

  - `items.storageSystemsInfo.storageSystemType` (string)
    Type of storage system.
    Enum: "HPE_NIMBLE", "HPE_PRIMERA", "HPE_ALLETRA_STORAGE_MP"

  - `items.storageSystemsInfo.type` (string)
    The type of resource.
    Example: "storage-fleet/storage-system"

  - `items.storageSystemsInfo.vendorName` (string)
    Storage system provider name.
    Example: "hpe"

  - `items.updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `items.volumesSnapshotInfo` (array)
    Details of the associated snapshot volumes

  - `items.volumesSnapshotInfo.id` (string)
    UUID string uniquely identifying the snapshot volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesSnapshotInfo.name` (string)
    Name of the snapshot volume.
    Example: "ATL-0106052-ro-210503202357032"

  - `items.volumesSnapshotInfo.resourceUri` (string)
    Reference to resource.

  - `items.volumesSnapshotInfo.scsiIdentifier` (string)
    SCSI identifier of the volume or snapshot .
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.volumesSnapshotInfo.sizeInMib` (integer)
    Size of the volume or snapshot in mega bytes.
    Example: 614400

  - `items.volumesSnapshotInfo.storageSystemInfo` (object)
    Describes a storage system.

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


