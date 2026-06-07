---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners/{replicationPartnerId}/volumes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4getreplicationpartnervolumesbyappsetid.md"
scraped_at: "2026-06-07T06:14:34.362229+00:00Z"
---

# Get volume details of replication partners identified by {appsetId} and {replicationPartnerId} for HPE Alletra Storage MP B10000

Get volume details of replication partners identified by {appsetId} and {replicationPartnerId} for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners/{replicationPartnerId}/volumes
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `appsetId` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `replicationPartnerId` (string, required)
    ID of device-type4 replication partner
    Example: "aedec7d11d02f73611a6ff992c256bdb"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique Identifier of the volume.
    Example: "b23a03cf79a0830f507eebb90c30410c"

  - `items.type` (string, required)
    type
    Example: "volume"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    customerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.displayName` (string,null)
    Volume display name
    Example: "testVol624_1"

  - `items.domain` (string,null)
    Domain that the resource belongs to.
    Example: "Domain2"

  - `items.generation` (integer,null)
    generation

  - `items.groupId` (string,null)
    Unique id of replication partner remote group.
    Example: "0af26e4430948dd5c37bea1757107caf"

  - `items.groupName` (string,null)
    Replication partner remote group name.
    Example: "testGroup"

  - `items.groupObjectId` (integer,null)
    Replication partner group ID.
    Example: 11

  - `items.isRemoteArraySupportReplication` (boolean)
    Boolean value to indicate if remote array OS version supports replication
    Example: true

  - `items.localVolumeId` (integer,null)
    Volume ID.
    Example: 21

  - `items.localVolumeName` (string,null)
    Volume name.
    Example: "testVol624_1"

  - `items.remoteVolume` (object,null)
    remote volume properties associated with replication partner

  - `items.remoteVolume.asyncOutstanding` (integer,null)
    Total outstanding data to be synchronized in MB. You can calculate backlog data for the Remote Copy Async group by summing up the asyncOutsstanding value for all the volumes in the group. Defaults to -1.
    Example: -1

  - `items.remoteVolume.remoteVolumeId` (integer,null)
    Volume ID on the target system.
    Example: 31

  - `items.remoteVolume.remoteVolumeName` (string,null)
    Volume name on the target system.
    Example: "testVol624_1.r"

  - `items.remoteVolume.resyncIteration` (string,null)
    A correlator used to determine the data consistency point of the resynchroniztion snapshot relative to the remote volume and/or snapshots. Returns 'NA' if not set.
    Example: "134383/1"

  - `items.remoteVolume.resyncSnapshotName` (string,null)
    Snapshot indicating the starting point of the remote volume. The primary array uses this snapshot to determine which changes to synchronize to the secondary volume. The target array uses this snapshot as a recovery point if there is a resynchronization failure.
    Example: "rcpy.41.88.134"

  - `items.remoteVolume.syncIteration` (string,null)
    A correlator used to determine the data consistency point of the synchronization snapshot relative to the remote volume and/or snapshots. Returns 'NA' if not set.
    Example: "NA"

  - `items.remoteVolume.syncPercentage` (integer,null)
    Synchronization percentage of the volume.
    Example: 36

  - `items.remoteVolume.syncSnapshotName` (string,null)
    Snapshot indicating the destination point of the Remote Copy volume on successful completion of resynchronization. Upon completion of a resynchronization, the remote base volume mirrors this synchronization snapshot. This snapshot becomes the resync snapshot when resynchronization completes.
    Example: "none"

  - `items.remoteVolume.syncStatus` (string,null)
    Synchronization status of the volume. Can be New, Syncing, Synced, Not Synced, Stale, New Pre Synced, New Sync from Snap, Failsafe, Logging, New Pending, Pending Dismiss or Remote Pending Dismiss. Null if unset.
    Example: "Synced"

  - `items.remoteVolume.targetName` (string,null)
    Target to which the volume group is mirrored.
    Example: "sp2bh"

  - `items.remoteVolume.volumeIteration` (string,null)
    A correlator used to determine the data consistency point of the volume relative to the remote volume and/or snapshots. Returns 'NA' if not set.
    Example: "134383/1"

  - `items.remoteVolume.volumeLastSyncTime` (object,null)
    Last synchronization time in milliseconds since epoch.

  - `items.remoteVolume.volumeLastSyncTime.ms` (integer,null)
    Epoch time in milliseconds.
    Example: 1552301131100

  - `items.remoteVolume.volumeLastSyncTime.tz` (string,null)
    Time zone name
    Example: "UTC"

  - `items.remoteVolume.volumeSyncLength` (integer,null)
    Volume synchronization total length. Returns -1 if unset
    Example: -1

  - `items.remoteVolume.volumeSyncOffset` (integer,null)
    Volume synchronization offset. Returns -1 if unset.
    Example: -1

  - `items.resourceUri` (string)
    resourceUri for detailed volume object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/volumes/b23a03cf79a0830f507eebb90c30410c"

  - `items.systemId` (string,null)
    Unique ID or serial number of the system.
    Example: "7CE816P0SR"

  - `items.systemWwn` (string,null)
    WWN of the system.
    Example: "2FF70002AC020DA1"

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

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

## Response 503 fields (application/json):

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

## Response default fields (application/json):

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


## Response 304 fields
