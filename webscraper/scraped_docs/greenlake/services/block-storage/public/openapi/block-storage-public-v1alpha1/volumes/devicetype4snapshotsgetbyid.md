---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4snapshotsgetbyid.md"
scraped_at: "2026-06-07T06:14:29.936328+00:00Z"
---

# Get details of snapshot identified by {snapshotId} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

Get details of vlun identified by {id} for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{volumeId}/snapshots/{snapshotId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `volumeId` (string, required)
    UID(volumeuid) of the storage system
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

  - `snapshotId` (string, required)
    UID of the snapshots
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    UID of the snapshot. Filter
    Example: "b7107a30-260a-41c1-a47f-e50770c414c9"

  - `type` (string, required)
    type
    Example: "string"

  - `adminAllocationSettings` (object,null)

  - `adminAllocationSettings.deviceSpeed` (object,null)
    device speed

  - `adminAllocationSettings.deviceSpeed.text` (string,null)

  - `adminAllocationSettings.deviceSpeed.value` (integer,null)

  - `adminAllocationSettings.deviceType` (string,null)

  - `adminAllocationSettings.diskFilter` (string,null)

  - `adminAllocationSettings.ha` (object,null)

  - `adminAllocationSettings.ha.default` (string,null)
    Example: "Magazine"

  - `adminAllocationSettings.ha.key` (string,null)
    Example: "hajbod-10"

  - `adminAllocationSettings.raidType` (string,null)

  - `adminAllocationSettings.requestedHa` (object,null)

  - `adminAllocationSettings.setSize` (string,null)

  - `adminAllocationSettings.stepSize` (integer,null)

  - `baseId` (integer,null)
    snapshot Tdvv Size

  - `comment` (string,null)
    Comments

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `compressionPolicy` (string,null)
    compression policy

  - `conversionType` (string,null)
    Conversion Type of Volume
    Enum: "CONVERSIONTYPE_THIN", "CONVERSIONTYPE_DDS", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2", null

  - `copyOfId` (integer,null)
    Copy of ID

  - `creationTime` (object,null)
    Creation Time

  - `creationTime.ms` (integer,null)

  - `creationTime.tz` (string,null)

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `dataReduction` (string,null)
    Data Reduction type

  - `dedup` (string,null)

  - `devType` (string,null)
    Device Type

  - `displayname` (string,null)
    Display name of the volume

  - `domain` (string,null)
    Domain of the volume

  - `fullyProvisioned` (boolean,null)

  - `generation` (integer,null)
    generation

  - `headsPerCylinder` (integer,null)
    Heads per Cylinder

  - `healthState` (integer,null)
    Health status of the Volume.

  - `hidden` (boolean,null)
    Flag to know if the Volume is hidden or not

  - `initiators` (array,null)
    Initiator details

  - `initiators.deviceDiscoveredName` (string,null)
    Host/HostGroup name on device.
    Example: "TEST11"

  - `initiators.id` (string)
    Resource id
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `initiators.resourceUri` (string,null)
    Resource URI
    Example: "/v1/host-initiators/6848ef683c27403e96caa51816ddc72c"

  - `initiators.type` (string)
    Resource Name
    Example: "host-initiators"

  - `name` (string,null)
    A user friendly name to identify the storage system volume (resourceName).
    Example: "Finance"

  - `parentId` (integer,null)
    Parent Id

  - `physParentId` (integer,null)
    physical Parent Id

  - `physicalCopy` (boolean,null)

  - `policy` (object,null)

  - `policy.fileService` (boolean,null)

  - `policy.noCache` (boolean,null)

  - `policy.oneHost` (boolean,null)

  - `policy.ransomware` (boolean,null)
    Indicates Whether ransomware detection has been enabled on this volume (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and above).

  - `policy.staleSnapshot` (boolean,null)

  - `policy.system` (boolean,null)

  - `policy.zeroDetect` (boolean,null)

  - `policy.zeroFill` (boolean,null)

  - `provType` (string,null)
    Provisioning type

  - `raid` (string,null)
    Raid

  - `rcopyStatus` (string,null)
    RemoteCopy Status

  - `readOnly` (boolean,null)

  - `roChildId` (integer,null)
    RO child id

  - `rwChildId` (integer,null)

  - `rwareAlert` (boolean,null)
    Indicates whether this snapshot acts as an alert snapshot for the base volume. Alert snapshot is generated when the OS detects a possible ransomware attack on the base volume (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and above).

  - `sectorsPerTrack` (integer,null)
    Sector per Track

  - `sharedParentId` (integer,null)
    Shared Parent Id

  - `snapshotCapacity` (object,null)

  - `snapshotCapacity.adminSpace` (object,null)

  - `snapshotCapacity.adminSpace.freeMiB` (number,null)

  - `snapshotCapacity.adminSpace.grownMiB` (number,null)

  - `snapshotCapacity.adminSpace.rawReservedMiB` (number,null)

  - `snapshotCapacity.adminSpace.reclaimedMiB` (number,null)

  - `snapshotCapacity.adminSpace.reservedMiB` (number,null)

  - `snapshotCapacity.adminSpace.totalMiB` (number,null)

  - `snapshotCapacity.adminSpace.usedMiB` (number,null)

  - `snapshotCapacity.branchUsedBlocksMiB` (number,null)
    Branch used blocks size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS version 10.3.0 and above.

  - `snapshotCapacity.branchVirtualSizeMiB` (number,null)
    Branch virtual size in MiB. This attribute contains the provisioned or virtual size of the base volume and its Read-Only snapshots.
    Example: 2048

  - `snapshotCapacity.compactEfficiency` (number,null)
    Compact Efficiency

  - `snapshotCapacity.compressionEfficiency` (number,null)
    Compression Efficiency

  - `snapshotCapacity.copiedMb` (number,null)
    Copied MB

  - `snapshotCapacity.copiedPerc` (integer,null)
    Copied Perecentage

  - `snapshotCapacity.ddcSize` (number,null)

  - `snapshotCapacity.ddsSize` (number,null)

  - `snapshotCapacity.dedupSavingsSize` (number,null)

  - `snapshotCapacity.dedupWrittenSize` (number,null)

  - `snapshotCapacity.hostWrittenMiB` (number,null)
    Host written data size in MiB.

  - `snapshotCapacity.hostWrittenToVirtualPercent` (number,null)
    Host written to virtual percent

  - `snapshotCapacity.sizeMiB` (number,null)
    Size in MiB

  - `snapshotCapacity.snapshotTdvvSize` (object,null)

  - `snapshotCapacity.snapshotTdvvSize.ddcSizeMiB` (number,null)

  - `snapshotCapacity.snapshotTdvvSize.ddsSizeMiB` (number,null)

  - `snapshotCapacity.snapshotTdvvSize.virtualSizeMiB` (number,null)

  - `snapshotCapacity.snapshotTdvvSize.writtenSizeMiB` (number,null)

  - `snapshotCapacity.snapshotUsedToVirtualPercent` (number,null)
    Snapshot used to virtual percent

  - `snapshotCapacity.totalRawReservedMiB` (number,null)
    Total Raw Reserved Space in MiB

  - `snapshotCapacity.totalReservedMiB` (number,null)
    Description

  - `snapshotCapacity.totalSpaceMiB` (number,null)
    Total Space in MiB

  - `snapshotCapacity.usedBlocksMiB` (number,null)
    Used Blocks Size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS versions equal and below 10.2.x. For the system OS version 10.3.0 and above, please refer the field branchUsedBlocksMiB.

  - `snapshotCapacity.usedCapacity` (number,null)
    Used volume capacity.

  - `snapshotCapacity.usedSizeMiB` (number,null)
    Used Size in MiB

  - `snapshotCapacity.userReservedToVirtualPercent` (number,null)
    User reseved to virtual percent

  - `snapshotCapacity.userSpace` (object,null)

  - `snapshotCapacity.userUsedToVirtualPercent` (number,null)
    User used to virtual percent

  - `snapshotId` (integer,null)
    Numeric ID of the resource

  - `snapshotType` (string,null)

  - `started` (boolean,null)

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `thinProvisioned` (boolean,null)
    Thin provisioning details

  - `userAllocLimit` (integer,null)
    User alloc limit

  - `userAllocWarning` (integer,null)
    User alloc space limit warning

  - `userAllocationSettings` (object,null)

  - `userCpgId` (integer,null)
    User CPG Id

  - `userCpgName` (string,null)
    User CPG Name

  - `vlunSectorSize` (integer,null)
    VLUN sector size

  - `wwn` (string,null)
    Volume wwn.
    Example: "60002AC0000000000000006B0001FFEB"

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
