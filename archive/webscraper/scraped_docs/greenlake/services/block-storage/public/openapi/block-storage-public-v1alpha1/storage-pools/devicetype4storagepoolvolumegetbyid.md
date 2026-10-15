---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools/{id}/volumes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/devicetype4storagepoolvolumegetbyid.md"
scraped_at: "2026-06-07T06:14:24.512697+00:00Z"
---

# Get all volumes for storage-pool identified by {uuid} of HPE Alletra Storage MP B10000

Get all volumes for storage-pool identified by {uuid} of HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools/{id}/volumes
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    Identifier of pool. A 32 digit number.
    Example: "147c439db3ecb34d1ccccc932d14fd60"

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
    UUID string uniquely identifying the storage system object. Filter

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

  - `items.associatedLinks` (array,null)
    Associated Links
    Example: [{"resourceUri":"v1/storage-systems/{systemUid}/contollers","type":"controllers"},{"resourceUri":"v1/storage-systems/{systemUid}/shelves","type":"shelves"},{"resourceUri":"v1/storage-systems/{systemUid}/disks","type":"disks"},{"resourceUri":"v1/storage-systems/{systemUid}/storage-ports","type":"storage-ports"},{"resourceUri":"v1/storage-systems/{systemUid}/storage-devices-settings","type":"storage-devices-settings"},{"resourceUri":"v1/storage-systems/{systemUid}/storage-pools","type":"storage-pools"},{"resourceUri":"v1/storage-systems/{systemUid}/volume-sets","type":"volume-sets"},{"resourceUri":"v1/storage-systems/{systemUid}/host-groups","type":"host-groups"}]

  - `items.associatedLinks.resourceUri` (string,null)
    Resource URI

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.baseId` (integer,null)
    snapshot Tdvv Size

  - `items.bulkvv` (boolean,null)
    Volume is bulk volume or not

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
    Compression Policy

  - `items.conversionType` (string,null)
    Conversion Type of Volume
    Enum: "CONVERSIONTYPE_THIN", "CONVERSIONTYPE_DDS", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2", null

  - `items.copyOfId` (integer,null)
    Copy of Id

  - `items.copyOfShortName` (string,null)
    Short name of volume parent, if a copy
    Example: "VegaCopyOfShortNames~66"

  - `items.creationTime` (object,null)
    Creation Time. Sort

  - `items.creationTime.ms` (integer,null)

  - `items.creationTime.tz` (string,null)

  - `items.customerId` (string,null)
    customerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.dataReduction` (string,null)
    Data Reduction type. Possible values:
              - DATA_REDUCTION_ON
              - DATA_REDUCTION_OFF
              - DATA_REDUCTION_DISABLED

  - `items.dedup` (string,null)
    Field to indicate Dedup status

  - `items.devType` (string,null)
    Device Type Filter

  - `items.displayname` (string,null)
    Display name of the volume

  - `items.domain` (string,null)
    Domain of the volume

  - `items.fullyProvisioned` (boolean,null)

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.headsPerCylinder` (integer,null)
    Heads per Cylinder

  - `items.healthState` (integer,null)
    Health status of the Volume. Filter, Sort

  - `items.hidden` (boolean,null)
    Flag to know if the Volume is hidden or not

  - `items.name` (string,null)
    A user friendly name to identify the storage system volume (resourceName). Filter, Sort
    Example: "Finance"

  - `items.nguid` (string,null)
    Namespace Globally Unique Identifier. This data is available only for NVMe enabled storage system. Filter
    Example: "60002AC0000800660002AC130007EEFD"

  - `items.parentId` (integer,null)
    Parent Id Filter

  - `items.pevv` (boolean,null)
    Volume is pe volume or not

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
    Description

  - `items.raid` (string,null)
    Raid

  - `items.rcopyStatus` (string,null)
    RemoteCopy Status

  - `items.readOnly` (boolean,null)

  - `items.resourceUri` (string,null)
    resourceUri for detailed volume object
    Example: "/v1/storage-systems/primea/2FF70002AC018D94/volumes/{uid}"

  - `items.sectorsPerTrack` (integer,null)
    Sector per Track

  - `items.sharedParentId` (integer,null)
    Shared Parent Id

  - `items.shortName` (string,null)
    Short name of the storage system volume
    Example: "VegaVolumesShortName~67245"

  - `items.snapShotTier` (string,null)
    Snapshot Tier

  - `items.started` (boolean,null)

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.storageTier` (string,null)
    Storage Tier

  - `items.systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `items.thinProvisioned` (boolean,null)
    Description

  - `items.userAllocLimit` (integer,null)
    User alloc limit

  - `items.userAllocWarning` (integer,null)
    User alloc space limit warning

  - `items.userAllocationSettings` (object,null)

  - `items.userCpgId` (integer,null)
    User CPG Id Filter

  - `items.userCpgName` (string,null)
    User CPG Name Filter

  - `items.usrCpgShortName` (string,null)
    Short name of volume user CPG
    Example: "VegaUserCpgShortName~97"

  - `items.vlunSectorSize` (integer,null)
    VLUN sector size

  - `items.volumeCapacity` (object,null)

  - `items.volumeCapacity.adminSpace` (object,null)

  - `items.volumeCapacity.adminSpace.freeMiB` (number,null)

  - `items.volumeCapacity.adminSpace.grownMiB` (number,null)

  - `items.volumeCapacity.adminSpace.rawReservedMiB` (number,null)

  - `items.volumeCapacity.adminSpace.reclaimedMiB` (number,null)

  - `items.volumeCapacity.adminSpace.reservedMiB` (number,null)

  - `items.volumeCapacity.adminSpace.totalMiB` (number,null)

  - `items.volumeCapacity.adminSpace.usedMiB` (number,null)

  - `items.volumeCapacity.branchUsedBlocksMiB` (number,null)
    Branch used blocks size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS version 10.3.0 and above.

  - `items.volumeCapacity.branchVirtualSizeMiB` (number,null)
    Branch virtual size in MiB. This attribute contains the provisioned or virtual size of the base volume and its Read-Only snapshots.
    Example: 2048

  - `items.volumeCapacity.compactEfficiency` (number,null)
    Compact Efficiency

  - `items.volumeCapacity.compressSavings` (integer,null)
    The space savings in MiB by compressing data

  - `items.volumeCapacity.compressionEfficiency` (number,null)
    Compression Efficiency

  - `items.volumeCapacity.copiedMb` (number,null)
    Copied MB

  - `items.volumeCapacity.copiedPerc` (integer,null)
    Copied Perecentage

  - `items.volumeCapacity.ddcSize` (number,null)

  - `items.volumeCapacity.ddsSize` (number,null)

  - `items.volumeCapacity.dedupSavingsSize` (number,null)

  - `items.volumeCapacity.dedupWrittenSize` (number,null)

  - `items.volumeCapacity.hostWrittenMiB` (number,null)
    Host written data size in MiB.

  - `items.volumeCapacity.hostWrittenToVirtualPercent` (number,null)
    Host written to virtual percent

  - `items.volumeCapacity.nonReducibleData` (integer,null)
    Amount of data that could not be reduced

  - `items.volumeCapacity.reduceSavings` (integer,null)
    Savings from data reduction in MiB and this is the combination of compression and dedup savings

  - `items.volumeCapacity.reduceSavingsRatio` (number,null)
    Reduce ratio

  - `items.volumeCapacity.reducibleReduceSavings` (integer,null)
    Data reduction savings in MiB using the reducible data. This savings is the combination of compression and dedup savings

  - `items.volumeCapacity.reducibleReduceSavingsRatio` (number,null)
    Data reduction savings ratio using the reducible data. This savings is the combination of compression and dedup savings.

  - `items.volumeCapacity.sizeMiB` (number,null)
    Size in MiB Filter, Sort
    Example: 2048

  - `items.volumeCapacity.snapshotTdvvSize` (object,null)

  - `items.volumeCapacity.snapshotTdvvSize.ddcSizeMiB` (number,null)

  - `items.volumeCapacity.snapshotTdvvSize.ddsSizeMiB` (number,null)

  - `items.volumeCapacity.snapshotTdvvSize.virtualSizeMiB` (number,null)

  - `items.volumeCapacity.snapshotTdvvSize.writtenSizeMiB` (number,null)

  - `items.volumeCapacity.snapshotUsedToVirtualPercent` (number,null)
    Snapshot used to virtual percent

  - `items.volumeCapacity.thinSaving` (integer,null)
    The space savings from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space.

  - `items.volumeCapacity.thinSavings` (string,null)
    Thin savings for the detailed volume object

  - `items.volumeCapacity.thinSavingsRatio` (number,null)
    The space savings ratio from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space

  - `items.volumeCapacity.totalRawReservedMiB` (number,null)
    Total Raw Reserved Space in MiB

  - `items.volumeCapacity.totalReservedMiB` (number,null)
    Description

  - `items.volumeCapacity.totalSavings` (integer,null)
    Total space savings including thin, compression, dedup, clone, zero packing, and snaps in MiB

  - `items.volumeCapacity.totalSavingsRatio` (number,null)
    Total space savings ratio including thin, compression, dedup, clone, zero packing, and snaps

  - `items.volumeCapacity.totalSpaceMiB` (number,null)
    Total Space in MiB

  - `items.volumeCapacity.treeVirtualSize` (number,null)
    Virtual size of volume tree

  - `items.volumeCapacity.usedBlocksMiB` (number,null)
    Used Blocks Size in MiB. This attribute contains the used space of the base volume and its Read-Only snapshots. This field is relevant for the system OS versions equal and below 10.2.x. For the system OS version 10.3.0 and above, please refer the field branchUsedBlocksMiB.

  - `items.volumeCapacity.usedCapacity` (number,null)
    Used volume capacity. Filter, Sort

  - `items.volumeCapacity.usedSizeMiB` (number,null)
    Used Size in MiB

  - `items.volumeCapacity.userReservedToVirtualPercent` (number,null)
    User reseved to virtual percent

  - `items.volumeCapacity.userSpace` (object,null)

  - `items.volumeCapacity.userUsedToVirtualPercent` (number,null)
    User used to virtual percent

  - `items.volumeCapacity.vvtreeHostWrt` (integer,null)
    Total data written to volume family tree by the host

  - `items.volumeId` (integer,null)
    Numeric ID of the resource

  - `items.volumePerformance` (object,null)

  - `items.volumePerformance.iops` (object,null)
    kpi metrics with read, write and total average values

  - `items.volumePerformance.iops.read` (object,null)
    Performance metrics average values

  - `items.volumePerformance.iops.read.avgOf1day` (number,null)
    last one day avg data
    Example: 33.65

  - `items.volumePerformance.iops.read.avgOf1hour` (number,null)
    last one hour avg data
    Example: 40.4

  - `items.volumePerformance.iops.read.avgOf8hours` (number,null)
    last 8 hours avg data
    Example: 50.98

  - `items.volumePerformance.iops.read.avgOfLatest` (number,null)
    latest perf data
    Example: 3.4

  - `items.volumePerformance.iops.total` (object,null)
    Performance metrics average values

  - `items.volumePerformance.iops.write` (object,null)
    Performance metrics average values

  - `items.volumePerformance.latencyMs` (object,null)
    kpi metrics with read, write and total average values

  - `items.volumePerformance.throughputKbps` (object,null)
    kpi metrics with read, write and total average values

  - `items.volumeType` (string,null)
    VV Type
    Example: "VVTYPE_BASE"

  - `items.wwn` (string,null)
    Volume wwn. Filter
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


