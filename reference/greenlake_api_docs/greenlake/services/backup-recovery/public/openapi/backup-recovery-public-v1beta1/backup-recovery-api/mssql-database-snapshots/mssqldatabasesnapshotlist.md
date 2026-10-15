---
title: "GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-database-snapshots/mssqldatabasesnapshotlist.md"
scraped_at: "2026-06-07T06:14:03.654224+00:00Z"
---

# Get information about all MSSQL database snapshots.

Get information about all MSSQL database snapshots.

Endpoint: GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots
Version: 1.1.0
Security: bearer

## Path parameters:

  - `db-id` (string, required)
    UUID string uniquely identifying the MSSQL Database
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

Examples:
* GET /backup-recovery/v1beta1/mssql-databases/{db-id}/snapshots?filter="consistency eq APPLICATION"

Filters are supported on the following attributes:
* snapshotType
* state
* status
* createdByInfo/id
* createdByInfo/name
* storageSystemInfo/id
* storageSystemInfo/type
* storageSystemInfo/name
* verified
* consistency
* pointInTime

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified, the
default order is ascending.

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.associatedDatabases` (array)
    Details of the databases whose backup is also part of this snapshot object. On deleting this snapshot object the backed up data of the associated databases which is part of this snapshot is also deleted

  - `items.associatedDatabases.id` (string)
    UUID string uniquely identifying the MSSQL Database

  - `items.associatedDatabases.name` (string)
    Name of the MSSQL Database as configured in the application host

  - `items.associatedDatabases.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.createdByInfo` (object)
    Information about the user who initiated the workflow that
created this snapshot or template.

  - `items.createdByInfo.id` (string)
    UUID of the user.

  - `items.createdByInfo.name` (string)
    Name of the user.

  - `items.customerId` (string)
    The customer application identifier.

  - `items.description` (string)
    Brief description about the application snapshot.

  - `items.expiresAt` (string)
    Absolute value of time in UTC at which the snapshot expires.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.lockedUntil` (string)
    Absolute value of time in UTC until which the application snapshot is locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.logBackupInfo` (object)

  - `items.logBackupInfo.lastLogBackupTime` (string)
    Time in UTC at which the last log backup was created before the next full backup.
    Example: "2020-03-03T06:03:08.902Z"

  - `items.logBackupInfo.protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `items.logBackupInfo.protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.logBackupInfo.protectionStoreInfo.name` (string)
    Name of the protection store.

  - `items.logBackupInfo.protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `items.logBackupInfo.protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `items.logBackupInfo.storageSystemInfo` (object)
    Information about storage system where backup is created.

  - `items.logBackupInfo.storageSystemInfo.displayName` (string)
    Name of the storage system.
    Example: "atlas-dev-psg1.ind.hpecorp.net"

  - `items.logBackupInfo.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.logBackupInfo.storageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `items.logBackupInfo.storageSystemInfo.type` (string)
    Type of storage system.
    Enum: "PROTECTION_STORE_GATEWAY", "STOREONCE"

  - `items.name` (string)
    Name of the application snapshot.
    Example: "Nimble-DB1-snap"

  - `items.pointInTime` (string)
    Time in UTC at which the application snapshot was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.scheduleInfo` (object)
    Details about the schedule which created this snapshot.

  - `items.scheduleInfo.id` (string)
    Client provided id for this schedule.

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

  - `items.storageSystemsInfo` (array)
    Storage info details of this MSSQL Database

  - `items.storageSystemsInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `items.storageSystemsInfo.resourceUri` (string)
    The URI reference for this resource.

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

  - `items.volumesSnapshotInfo.scsiIdentifier` (string)
    SCSI identifier of the volume or snapshot .
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.volumesSnapshotInfo.sizeInMib` (integer)
    Size of the volume or snapshot in mega bytes.
    Example: 614400

  - `items.volumesSnapshotInfo.storageSystemInfo` (object)
    Describes a storage system.

  - `items.volumesSnapshotInfo.storageSystemInfo.displayName` (string)
    A user-friendly name that identifies the storage system.
    Example: "my-dev-3par1.ind.hpecorp.net"

  - `items.volumesSnapshotInfo.storageSystemInfo.managed` (boolean)
    Specify if the storage system is registered.

  - `items.volumesSnapshotInfo.storageSystemInfo.serialNumber` (string)
    Serial number of the storage system.
    Example: "AF-10122"

  - `items.volumesSnapshotInfo.storageSystemInfo.storageSystemType` (string)
    Type of storage system.
    Enum: "HPE_NIMBLE", "HPE_PRIMERA", "HPE_ALLETRA_STORAGE_MP"

  - `items.volumesSnapshotInfo.storageSystemInfo.vendorName` (string)
    Storage system provider name.
    Example: "hpe"

  - `count` (integer, required)
    Number of items in this response.

  - `pageLimit` (integer)
    The numbers of items to return

  - `pageOffset` (integer)
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


