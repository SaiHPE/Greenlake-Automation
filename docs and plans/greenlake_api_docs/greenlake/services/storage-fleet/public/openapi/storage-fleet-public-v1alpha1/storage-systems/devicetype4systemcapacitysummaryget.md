---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/capacity-summary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-systems/devicetype4systemcapacitysummaryget.md"
scraped_at: "2026-06-07T06:15:59.766253+00:00Z"
---

# Get system capacity for an HPE Alletra Storage MP B10000 storage system

Get system capacity for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/capacity-summary
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

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
    ID string uniquely identifying the object.

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.capacityByTier` (object,null)

  - `items.capacityByTier.fcFree` (number,null)
    fc free capacity

  - `items.capacityByTier.fcUsed` (number,null)
    fc used capacity

  - `items.capacityByTier.nlFree` (number,null)
    nl free capacity
    Example: 58368

  - `items.capacityByTier.nlUsed` (number,null)
    nl used capacity
    Example: 17408

  - `items.capacityByTier.qlcFree` (number,null)
    qlc free capacity

  - `items.capacityByTier.qlcUsed` (number,null)
    qlc used capacity

  - `items.capacityByTier.ssdFree` (number,null)
    ssd free capacity

  - `items.capacityByTier.ssdUsed` (number,null)
    ssd used capacity

  - `items.capacityByTier.totalUsed` (number,null)
    usable capacity
    Example: 17408

  - `items.capacityByTier.usableCapacity` (number,null)
    usable capacity
    Example: 58368

  - `items.capacityDetail` (object,null)

  - `items.capacityDetail.snapSpace` (number,null)
    Total snap capacity used
    Example: 228565.15

  - `items.capacityDetail.volumeSpace` (number,null)
    Total volume capacity used
    Example: 233359.43

  - `items.capacitySummary` (object,null)

  - `items.capacitySummary.bulkvvPrivateSnp` (number,null)
    Bulk VVs private snap capacity
    Example: 0.08

  - `items.capacitySummary.bulkvvsAdmin` (number,null)
    Bulk VVs admin capacity
    Example: 0.08

  - `items.capacitySummary.bulkvvsCopy` (number,null)
    Bulk VVs copy capacity
    Example: 0.08

  - `items.capacitySummary.bulkvvsUsr` (number,null)
    Bulk VVs user capacity
    Example: 0.08

  - `items.capacitySummary.compaction` (number,null)
    Compaction details
    Example: 8384.594860579551

  - `items.capacitySummary.compressSavings` (integer,null)
    The space savings in MiB by compressing data
    Example: 1

  - `items.capacitySummary.compression` (number,null)
    Compression details

  - `items.capacitySummary.compressratio` (number,null)
    Compression ratio
    Example: 0.08

  - `items.capacitySummary.cpgsAdminUnused` (number,null)
    CPGs admin unused capacity
    Example: 0.08

  - `items.capacitySummary.cpgsAdminUsed` (number,null)
    CPGs admin used capacity
    Example: 0.08

  - `items.capacitySummary.cpgsCopy` (number,null)
    CPGs copy capacity
    Example: 0.08

  - `items.capacitySummary.cpgsCopyUsed` (number,null)
    CPGs copy used capacity
    Example: 0.08

  - `items.capacitySummary.cpgsDedupttes` (number,null)
    CPGs dedup TTES capacity
    Example: 0.08

  - `items.capacitySummary.cpgsMetadata` (number,null)
    CPgs metadata capacity
    Example: 0.08

  - `items.capacitySummary.cpgsSvcnt` (number,null)
    CPGs SVcnt capacity
    Example: 0.08

  - `items.capacitySummary.cpgsTotCountSd` (number,null)
    CPGs total count SD capacity
    Example: 0.08

  - `items.capacitySummary.cpgsTotUsedSize` (number,null)
    Total space used by all CPGs
    Example: 0.08

  - `items.capacitySummary.cpgsUnused` (number,null)
    CPGs unused capacity
    Example: 0.08

  - `items.capacitySummary.cpgsUsr` (number,null)
    CPGs user capacity
    Example: 0.08

  - `items.capacitySummary.cpgsUsrUsed` (number,null)
    CPGs user used capacity
    Example: 0.08

  - `items.capacitySummary.cpgsVirtualSize` (number,null)
    Virtual size of all CPGs
    Example: 0.08

  - `items.capacitySummary.dataReduction` (number,null)
    Data reduction

  - `items.capacitySummary.dedup` (number,null)
    Dedup Details

  - `items.capacitySummary.dedupSavings` (integer,null)
    Savings due to dedup in MiB
    Example: 1

  - `items.capacitySummary.dedupratio` (number,null)
    Dedup ratio
    Example: 0.08

  - `items.capacitySummary.failed` (number,null)
    Failed capacity
    Example: 2048

  - `items.capacitySummary.failedPercentage` (number,null)
    Percentage of failed capacity
    Example: 0.00006787023211619383

  - `items.capacitySummary.free` (number,null)
    Free capacity of the system
    Example: 23020544

  - `items.capacitySummary.freeInitialized` (number,null)
    Intialized capacity out of the free capacity
    Example: 23020544

  - `items.capacitySummary.freePercentage` (number,null)
    Percentage of the free capacity
    Example: 0.7628953441020768

  - `items.capacitySummary.freeUninitialized` (number,null)
    Uninitialized capacity out of the free capacity

  - `items.capacitySummary.hostWrt` (integer,null)
    Total Written By Hosts in MiB
    Example: 1

  - `items.capacitySummary.nonReducibleData` (integer,null)
    Amount of data that could not be reduced
    Example: 2

  - `items.capacitySummary.overAllocspace` (number,null)
    Over-provisioning allocated space capacity
    Example: 0.08

  - `items.capacitySummary.overAvail` (number,null)
    Over-provisioning available capacity
    Example: 0.08

  - `items.capacitySummary.overFreespace` (number,null)
    Over-provisioning free space capacity
    Example: 0.08

  - `items.capacitySummary.overProvisioning` (number,null)
    Over provisioning ratio
    Example: 0.08

  - `items.capacitySummary.overUsedspace` (number,null)
    Over-provisioning used space capacity
    Example: 0.08

  - `items.capacitySummary.overVsize` (number,null)
    Over Vsize capacity
    Example: 0.08

  - `items.capacitySummary.privateszMetadata` (number,null)
    Private size metadata capacity
    Example: 0.08

  - `items.capacitySummary.privateszSnp` (number,null)
    Private size snap capacity
    Example: 0.08

  - `items.capacitySummary.privateszTot` (number,null)
    Total used space of all the volumes at system level
    Example: 0.08

  - `items.capacitySummary.privateszTotSnp` (number,null)
    Total used space of all the snapshots at system level. It only includes the private space of the snapshots
    Example: 0.08

  - `items.capacitySummary.reduceSavings` (integer,null)
    Savings from data reduction in MiB and this is the combination of compression and dedup savings
    Example: 2

  - `items.capacitySummary.reducibleReduceSavings` (integer,null)
    Data reduction savings in MiB using the reducible data. This savings is the combination of compression and dedup savings.
    Example: 2

  - `items.capacitySummary.reducibleReduceSavingsRatio` (number,null)
    Data reduction savings ratio using the reducible data. This savings is the combination of compression and dedup savings.
    Example: 0.08

  - `items.capacitySummary.thinSavings` (integer,null)
    The space savings from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space.
    Example: 1

  - `items.capacitySummary.thinSavingsRatio` (number,null)
    The space savings ratio from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space.
    Example: 0.08

  - `items.capacitySummary.total` (number,null)
    Total capacity of the system
    Example: 30175232

  - `items.capacitySummary.totalFree` (number,null)
    Total free capacity
    Example: 0.08

  - `items.capacitySummary.totalSavings` (integer,null)
    Total space savings including thin, compression, dedup, clone, zero packing, and snaps in MiB
    Example: 2

  - `items.capacitySummary.totalSavingsRatio` (number,null)
    Total space savings ratio including thin, compression, dedup, clone, zero packing, and snaps
    Example: 0.08

  - `items.capacitySummary.totalUsed` (number,null)
    Total used capacity
    Example: 0.08

  - `items.capacitySummary.unavailable` (number,null)
    Unavailable storage

  - `items.capacitySummary.unavailablePercentage` (number,null)
    Percentage of storage that is unavailable

  - `items.capacitySummary.unusable` (number,null)
    Unusable capacity
    Example: 0.08

  - `items.capacitySummary.usable` (number,null)
    Usable capacity
    Example: 0.08

  - `items.capacitySummary.vvUnused` (number,null)
    VV unused capacity
    Example: 0.08

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.fcCapacitySummary` (object,null)

  - `items.fcUsableCapacitySummary` (object,null)

  - `items.nlCapacitySummary` (object,null)

  - `items.nlUsableCapacitySummary` (object,null)

  - `items.qlcCapacitySummary` (object,null)

  - `items.qlcUsableCapacitySummary` (object,null)

  - `items.resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/capacity-summary"

  - `items.ssdCapacitySummary` (object,null)

  - `items.ssdUsableCapacitySummary` (object,null)

  - `items.systemId` (string,null)
    SystemId/serialNumber of the array.
    Example: "7CE751P312"

  - `items.usableCapacitySummary` (object,null)

  - `items.utilizationSummary` (object,null)

  - `items.utilizationSummary.capacityUsageData` (object,null)

  - `items.utilizationSummary.capacityUsageData.freeSizeMiB` (number,null)
    Free size in MiB
    Example: 7240704

  - `items.utilizationSummary.capacityUsageData.usedSizeMiB` (number,null)
    Used size in MiB
    Example: 3072

  - `items.utilizationSummary.provisionedCapacity` (number,null)
    Provisioned capacity
    Example: 16384

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


