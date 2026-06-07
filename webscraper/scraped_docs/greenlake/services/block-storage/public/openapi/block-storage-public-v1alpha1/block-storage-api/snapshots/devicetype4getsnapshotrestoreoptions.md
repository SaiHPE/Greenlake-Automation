---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{childSnapshotId}/restore-options"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/snapshots/devicetype4getsnapshotrestoreoptions.md"
scraped_at: "2026-06-07T06:14:39.873356+00:00Z"
---

# Get the details of all read-write parent snapshots and base volume to which the child snapshot identified by {childSnapshotId} can be restored on HPE Alletra Storage MP B10000 system identified by {systemId}.

Get the details of all read-write parent snapshots and base volume to which the child snapshot identified by {childSnapshotId} can be restored on HPE Alletra Storage MP B10000 system identified by {systemId}.

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{childSnapshotId}/restore-options
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `childSnapshotId` (string, required)
    UID of the child snapshot to be restored
    Example: "c7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter by Key.
    Example: "name eq array1 and wwn eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort by Key.
    Example: "systemWWN desc"

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    UID of the snapshot. Filter
    Example: "b7107a30-260a-41c1-a47f-e50770c414c9"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.adminAllocationSettings` (object,null)

  - `items.adminAllocationSettings.deviceSpeed` (object,null)
    device speed

  - `items.adminAllocationSettings.deviceSpeed.text` (string,null)

  - `items.adminAllocationSettings.deviceSpeed.value` (integer,null)

  - `items.adminAllocationSettings.deviceType` (string,null)

  - `items.adminAllocationSettings.diskFilter` (string,null)

  - `items.adminAllocationSettings.ha` (object,null)

  - `items.adminAllocationSettings.ha.default` (string,null)
    Example: "Magazine"

  - `items.adminAllocationSettings.ha.key` (string,null)
    Example: "hajbod-10"

  - `items.adminAllocationSettings.raidType` (string,null)

  - `items.adminAllocationSettings.requestedHa` (object,null)

  - `items.adminAllocationSettings.setSize` (string,null)

  - `items.adminAllocationSettings.stepSize` (integer,null)

  - `items.baseId` (integer,null)
    snapshot Tdvv Size

  - `items.comment` (string,null)
    Comments

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

  - `items.compressionPolicy` (string,null)
    compression policy

  - `items.conversionType` (string,null)
    Conversion Type of Volume
    Enum: "CONVERSIONTYPE_THIN", "CONVERSIONTYPE_DDS", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2", null

  - `items.copyOfId` (integer,null)
    Copy of ID

  - `items.creationTime` (object,null)
    Creation Time Sort

  - `items.creationTime.ms` (integer,null)

  - `items.creationTime.tz` (string,null)

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.dataReduction` (string,null)
    Data Reduction type

  - `items.dedup` (string,null)

  - `items.devType` (string,null)
    Device Type

  - `items.displayname` (string,null)
    Display name of the volume

  - `items.domain` (string,null)
    Domain of the volume

  - `items.fullyProvisioned` (boolean,null)

  - `items.generation` (integer,null)
    generation

  - `items.headsPerCylinder` (integer,null)
    Heads per Cylinder

  - `items.healthState` (integer,null)
    Health status of the Volume.

  - `items.hidden` (boolean,null)
    Flag to know if the Volume is hidden or not

  - `items.initiators` (array,null)
    Initiator details

  - `items.initiators.deviceDiscoveredName` (string,null)
    Host/HostGroup name on device.
    Example: "TEST11"

  - `items.initiators.id` (string)
    Resource id
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.initiators.resourceUri` (string,null)
    Resource URI
    Example: "/v1/host-initiators/6848ef683c27403e96caa51816ddc72c"

  - `items.initiators.type` (string)
    Resource Name
    Example: "host-initiators"

  - `items.name` (string,null)
    A user friendly name to identify the storage system volume (resourceName).
    Example: "Finance"

  - `items.parentId` (integer,null)
    Parent Id

  - `items.physParentId` (integer,null)
    physical Parent Id

  - `items.physicalCopy` (boolean,null)

  - `items.policy` (object,null)

  - `items.policy.fileService` (boolean,null)

  - `items.policy.noCache` (boolean,null)

  - `items.policy.oneHost` (boolean,null)

  - `items.policy.ransomware` (boolean,null)
    Indicates Whether ransomware detection has been enabled on this volume (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and above).

  - `items.policy.staleSnapshot` (boolean,null)

  - `items.policy.system` (boolean,null)

  - `items.policy.zeroDetect` (boolean,null)

  - `items.policy.zeroFill` (boolean,null)

  - `items.provType` (string,null)
    Provisioning type

  - `items.raid` (string,null)
    Raid

  - `items.rcopyStatus` (string,null)
    RemoteCopy Status

  - `items.readOnly` (boolean,null)

  - `items.roChildId` (integer,null)
    RO child id

  - `items.rwChildId` (integer,null)

  - `items.rwareAlert` (boolean,null)
    Indicates whether this snapshot acts as an alert snapshot for the base volume. Alert snapshot is generated when the OS detects a possible ransomware attack on the base volume (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and above).

  - `items.sectorsPerTrack` (integer,null)
    Sector per Track

  - `items.sharedParentId` (integer,null)
    Shared Parent Id

  - `items.snapshotCapacity` (object,null)

  - `items.snapshotCapacity.adminSpace` (object,null)

  - `items.snapshotCapacity.adminSpace.freeMiB` (number,null)

  - `items.snapshotCapacity.adminSpace.grownMiB` (number,null)

  - `items.snapshotCapacity.adminSpace.rawReservedMiB` (number,null)

  - `items.snapshotCapacity.adminSpace.reclaimedMiB` (number,null)

  - `items.snapshotCapacity.adminSpace.reservedMiB` (number,null)

  - `items.snapshotCapacity.adminSpace.totalMiB` (number,null)

  - `items.snapshotCapacity.adminSpace.usedMiB` (number,null)

  - `items.snapshotCapacity.branchUsedBlocksMiB` (number,null)
    Branch used blocks size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS version 10.3.0 and above.

  - `items.snapshotCapacity.branchVirtualSizeMiB` (number,null)
    Branch virtual size in MiB. This attribute contains the provisioned or virtual size of the base volume and its Read-Only snapshots.
    Example: 2048

  - `items.snapshotCapacity.compactEfficiency` (number,null)
    Compact Efficiency

  - `items.snapshotCapacity.compressionEfficiency` (number,null)
    Compression Efficiency

  - `items.snapshotCapacity.copiedMb` (number,null)
    Copied MB

  - `items.snapshotCapacity.copiedPerc` (integer,null)
    Copied Perecentage

  - `items.snapshotCapacity.ddcSize` (number,null)

  - `items.snapshotCapacity.ddsSize` (number,null)

  - `items.snapshotCapacity.dedupSavingsSize` (number,null)

  - `items.snapshotCapacity.dedupWrittenSize` (number,null)

  - `items.snapshotCapacity.hostWrittenMiB` (number,null)
    Host written data size in MiB.

  - `items.snapshotCapacity.hostWrittenToVirtualPercent` (number,null)
    Host written to virtual percent

  - `items.snapshotCapacity.sizeMiB` (number,null)
    Size in MiB

  - `items.snapshotCapacity.snapshotTdvvSize` (object,null)

  - `items.snapshotCapacity.snapshotTdvvSize.ddcSizeMiB` (number,null)

  - `items.snapshotCapacity.snapshotTdvvSize.ddsSizeMiB` (number,null)

  - `items.snapshotCapacity.snapshotTdvvSize.virtualSizeMiB` (number,null)

  - `items.snapshotCapacity.snapshotTdvvSize.writtenSizeMiB` (number,null)

  - `items.snapshotCapacity.snapshotUsedToVirtualPercent` (number,null)
    Snapshot used to virtual percent

  - `items.snapshotCapacity.totalRawReservedMiB` (number,null)
    Total Raw Reserved Space in MiB

  - `items.snapshotCapacity.totalReservedMiB` (number,null)
    Description

  - `items.snapshotCapacity.totalSpaceMiB` (number,null)
    Total Space in MiB

  - `items.snapshotCapacity.usedBlocksMiB` (number,null)
    Used Blocks Size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS versions equal and below 10.2.x. For the system OS version 10.3.0 and above, please refer the field branchUsedBlocksMiB.

  - `items.snapshotCapacity.usedCapacity` (number,null)
    Used volume capacity.

  - `items.snapshotCapacity.usedSizeMiB` (number,null)
    Used Size in MiB

  - `items.snapshotCapacity.userReservedToVirtualPercent` (number,null)
    User reseved to virtual percent

  - `items.snapshotCapacity.userSpace` (object,null)

  - `items.snapshotCapacity.userUsedToVirtualPercent` (number,null)
    User used to virtual percent

  - `items.snapshotId` (integer,null)
    Numeric ID of the resource

  - `items.snapshotType` (string,null)

  - `items.started` (boolean,null)

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `items.thinProvisioned` (boolean,null)
    Thin provisioning details

  - `items.userAllocLimit` (integer,null)
    User alloc limit

  - `items.userAllocWarning` (integer,null)
    User alloc space limit warning

  - `items.userAllocationSettings` (object,null)

  - `items.userCpgId` (integer,null)
    User CPG Id

  - `items.userCpgName` (string,null)
    User CPG Name

  - `items.vlunSectorSize` (integer,null)
    VLUN sector size

  - `items.wwn` (string,null)
    Volume wwn.
    Example: "60002AC0000000000000006B0001FFEB"

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
