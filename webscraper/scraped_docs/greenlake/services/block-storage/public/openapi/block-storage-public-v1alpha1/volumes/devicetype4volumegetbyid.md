---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumegetbyid.md"
scraped_at: "2026-06-07T06:14:28.474331+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Volume identified by {id}

Get details for a single HPE Alletra Storage MP B10000 volume identified by {id}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID(volumeuid) of the storage system
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the storage system object.

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

  - `associatedLinks` (array,null)
    Associated Links
    Example: [{"resourceUri":"v1/storage-systems/{systemUid}/contollers","type":"controllers"},{"resourceUri":"v1/storage-systems/{systemUid}/shelves","type":"shelves"},{"resourceUri":"v1/storage-systems/{systemUid}/disks","type":"disks"},{"resourceUri":"v1/storage-systems/{systemUid}/storage-ports","type":"storage-ports"},{"resourceUri":"v1/storage-systems/{systemUid}/storage-devices-settings","type":"storage-devices-settings"},{"resourceUri":"v1/storage-systems/{systemUid}/storage-pools","type":"storage-pools"},{"resourceUri":"v1/storage-systems/{systemUid}/volume-sets","type":"volume-sets"},{"resourceUri":"v1/storage-systems/{systemUid}/host-groups","type":"host-groups"}]

  - `associatedLinks.resourceUri` (string,null)
    Resource URI

  - `associatedLinks.type` (string)
    Resource Name

  - `baseId` (integer,null)
    snapshot Tdvv Size

  - `bulkvv` (boolean,null)
    Volume is bulk volume or not

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
    Compression Policy

  - `conversionType` (string,null)
    Conversion Type of Volume
    Enum: "CONVERSIONTYPE_THIN", "CONVERSIONTYPE_DDS", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2", null

  - `copyOfId` (integer,null)
    Copy of Id

  - `copyOfShortName` (string,null)
    Short name of volume parent, if a copy
    Example: "VegaCopyOfShortNames~66"

  - `creationTime` (object,null)

  - `creationTime.ms` (integer,null)

  - `creationTime.tz` (string,null)

  - `customerId` (string,null)
    customerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `dataReduction` (string,null)
    Data Reduction type. Possible values:
  - DATA_REDUCTION_ON
  - DATA_REDUCTION_OFF
  - DATA_REDUCTION_DISABLED

  - `dedup` (string,null)
    Dedup

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

  - `name` (string,null)
    A user friendly name to identify the storage system volume (resourceName).
    Example: "Finance"

  - `nguid` (string,null)
    Namespace Globally Unique Identifier. This data is available only for NVMe enabled storage system.
    Example: "60002AC0000800660002AC130007EEFD"

  - `parentId` (integer,null)
    Parent Id

  - `pevv` (boolean,null)
    Volume is pe volume or not

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
    Description

  - `raid` (string,null)
    Raid

  - `rcopyStatus` (string,null)
    RemoteCopy Status

  - `readOnly` (boolean,null)

  - `resourceUri` (string,null)
    resourceUri for detailed volume object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/volumes/{uid}"

  - `sectorsPerTrack` (integer,null)
    Sector per Track

  - `sharedParentId` (integer,null)
    Shared Parent Id

  - `shortName` (string,null)
    Short name of the storage system volume
    Example: "VegaVolumesShortName~67245"

  - `snapShotTier` (string,null)
    Snapshot Tier

  - `started` (boolean,null)

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `storageTier` (string,null)
    Storage Tier

  - `systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `thinProvisioned` (boolean,null)
    Description

  - `userAllocLimit` (integer,null)
    User alloc limit

  - `userAllocWarning` (integer,null)
    User alloc space limit warning

  - `userAllocationSettings` (object,null)

  - `userCpgId` (integer,null)
    User CPG Id

  - `userCpgName` (string,null)
    User CPG Name

  - `usrCpgShortName` (string,null)
    Short name of volume user CPG
    Example: "VegaUserCpgShortName~97"

  - `vlunSectorSize` (integer,null)
    VLUN sector size

  - `volumeCapacity` (object,null)

  - `volumeCapacity.adminSpace` (object,null)

  - `volumeCapacity.adminSpace.freeMiB` (number,null)

  - `volumeCapacity.adminSpace.grownMiB` (number,null)

  - `volumeCapacity.adminSpace.rawReservedMiB` (number,null)

  - `volumeCapacity.adminSpace.reclaimedMiB` (number,null)

  - `volumeCapacity.adminSpace.reservedMiB` (number,null)

  - `volumeCapacity.adminSpace.totalMiB` (number,null)

  - `volumeCapacity.adminSpace.usedMiB` (number,null)

  - `volumeCapacity.branchUsedBlocksMiB` (number,null)
    Branch used blocks size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS version 10.3.0 and above.

  - `volumeCapacity.branchVirtualSizeMiB` (number,null)
    Branch virtual size in MiB. This attribute contains the provisioned or virtual size of the base volume and its Read-Only snapshots.
    Example: 2048

  - `volumeCapacity.compactEfficiency` (number,null)
    Compact Efficiency

  - `volumeCapacity.compressSavings` (integer,null)
    The space savings in MiB by compressing data

  - `volumeCapacity.compressionEfficiency` (number,null)
    Compression Efficiency

  - `volumeCapacity.copiedMb` (number,null)
    Copied MB

  - `volumeCapacity.copiedPerc` (integer,null)
    Copied Perecentage

  - `volumeCapacity.ddcSize` (number,null)

  - `volumeCapacity.ddsSize` (number,null)

  - `volumeCapacity.dedupSavingsSize` (number,null)

  - `volumeCapacity.dedupWrittenSize` (number,null)

  - `volumeCapacity.hostWrittenMiB` (number,null)
    Host written data size in MiB.

  - `volumeCapacity.hostWrittenToVirtualPercent` (number,null)
    Host written to virtual percent

  - `volumeCapacity.nonReducibleData` (integer,null)
    Amount of data that could not be reduced

  - `volumeCapacity.reduceSavings` (integer,null)
    Savings from data reduction in MiB and this is the combination of compression and dedup savings

  - `volumeCapacity.reduceSavingsRatio` (number,null)
    Reduce ratio

  - `volumeCapacity.reducibleReduceSavings` (integer,null)
    Data reduction savings in MiB using the reducible data. This savings is the combination of compression and dedup savings

  - `volumeCapacity.reducibleReduceSavingsRatio` (number,null)
    Data reduction savings ratio using the reducible data. This savings is the combination of compression and dedup savings.

  - `volumeCapacity.sizeMiB` (number,null)
    Size in MiB Filter, Sort
    Example: 2048

  - `volumeCapacity.snapshotTdvvSize` (object,null)

  - `volumeCapacity.snapshotTdvvSize.ddcSizeMiB` (number,null)

  - `volumeCapacity.snapshotTdvvSize.ddsSizeMiB` (number,null)

  - `volumeCapacity.snapshotTdvvSize.virtualSizeMiB` (number,null)

  - `volumeCapacity.snapshotTdvvSize.writtenSizeMiB` (number,null)

  - `volumeCapacity.snapshotUsedToVirtualPercent` (number,null)
    Snapshot used to virtual percent

  - `volumeCapacity.thinSaving` (integer,null)
    The space savings from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space.

  - `volumeCapacity.thinSavings` (string,null)
    Thin savings for the detailed volume object

  - `volumeCapacity.thinSavingsRatio` (number,null)
    The space savings ratio from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space

  - `volumeCapacity.totalRawReservedMiB` (number,null)
    Total Raw Reserved Space in MiB

  - `volumeCapacity.totalReservedMiB` (number,null)
    Description

  - `volumeCapacity.totalSavings` (integer,null)
    Total space savings including thin, compression, dedup, clone, zero packing, and snaps in MiB

  - `volumeCapacity.totalSavingsRatio` (number,null)
    Total space savings ratio including thin, compression, dedup, clone, zero packing, and snaps

  - `volumeCapacity.totalSpaceMiB` (number,null)
    Total Space in MiB

  - `volumeCapacity.treeVirtualSize` (number,null)
    Virtual size of volume tree

  - `volumeCapacity.usedBlocksMiB` (number,null)
    Used Blocks Size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS versions equal and below 10.2.x. For the system OS version 10.3.0 and above, please refer the field branchUsedBlocksMiB.

  - `volumeCapacity.usedCapacity` (number,null)
    Used volume capacity. Filter, Sort

  - `volumeCapacity.usedSizeMiB` (number,null)
    Used Size in MiB

  - `volumeCapacity.userReservedToVirtualPercent` (number,null)
    User reseved to virtual percent

  - `volumeCapacity.userSpace` (object,null)

  - `volumeCapacity.userUsedToVirtualPercent` (number,null)
    User used to virtual percent

  - `volumeCapacity.vvtreeHostWrt` (integer,null)
    Total data written to volume family tree by the host

  - `volumeId` (integer,null)
    Numeric ID of the resource

  - `volumePerformance` (object,null)

  - `volumePerformance.iops` (object,null)
    kpi metrics with read, write and total average values

  - `volumePerformance.iops.read` (object,null)
    Performance metrics average values

  - `volumePerformance.iops.read.avgOf1day` (number,null)
    last one day avg data
    Example: 33.65

  - `volumePerformance.iops.read.avgOf1hour` (number,null)
    last one hour avg data
    Example: 40.4

  - `volumePerformance.iops.read.avgOf8hours` (number,null)
    last 8 hours avg data
    Example: 50.98

  - `volumePerformance.iops.read.avgOfLatest` (number,null)
    latest perf data
    Example: 3.4

  - `volumePerformance.iops.total` (object,null)
    Performance metrics average values

  - `volumePerformance.iops.write` (object,null)
    Performance metrics average values

  - `volumePerformance.latencyMs` (object,null)
    kpi metrics with read, write and total average values

  - `volumePerformance.throughputKbps` (object,null)
    kpi metrics with read, write and total average values

  - `volumeType` (string,null)
    VV Type
    Example: "VVTYPE_BASE"

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
