---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/storage-pools/devicetype4storagepoolgetbyid.md"
scraped_at: "2026-06-07T06:14:24.464057+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 storage-pool identified by {id}

Get details of HPE Alletra Storage MP B10000 storage-pool identified by {id}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/storage-pools/{id}
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

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `type` (string, required)
    type
    Example: "string"

  - `alert` (object,null)
    Information for posted alerts

  - `alert.fail` (string)
    Alert when there is a growth failure for admin/data space
    Example: "--"

  - `alert.limit` (string)
    Alert corresponding to limit for admin/data space
    Example: "--"

  - `alert.warn` (string)
    Alert corresponding to warning for admin/data space
    Example: "--"

  - `alert.warnPercent` (number)
    Alert corresponding to warning percentage for admin/data space
    Example: 2

  - `allocationSettings` (object,null)
    Device allocation settings such as RAID and device type information

  - `allocationSettings.chunkletPosPref` (string,null)
    Chunklets position
    Example: "Position1"

  - `allocationSettings.deviceSpeed` (object,null)
    Device speed

  - `allocationSettings.deviceSpeed.text` (string,null)

  - `allocationSettings.deviceSpeed.value` (integer,null)

  - `allocationSettings.deviceType` (string,null)
    Device type
    Example: "DEVICE_TYPE_SSD"

  - `allocationSettings.diskFilter` (string,null)
    Disk filter
    Example: "test"

  - `allocationSettings.ha` (object,null)
    Requested High Availability setting

  - `allocationSettings.ha.default` (string,null)

  - `allocationSettings.ha.key` (string,null)

  - `allocationSettings.raidType` (string,null)
    RAID type
    Example: "RAID_SIX"

  - `allocationSettings.requestedHa` (object,null)
    Requested High Availability setting

  - `allocationSettings.setSize` (string,null)
    Set size
    Example: "6 data, 2 parity"

  - `allocationSettings.stepSize` (number)
    Step size
    Example: -1

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `baseSizeMiB` (integer)
    Number of LD MiB used in base virtual volumes
    Example: 67584

  - `baseSizePrivateMiB` (number)
    Number of LD MiB private to individual base virtual volumes, not shared by deduplication
    Example: 1215872

  - `baseSizeRawMiB` (number)
    Number of physical (raw) MiB used in base virtual volumes
    Example: 90111

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

  - `compactRatio` (number,null)
    Ratio between the virtual sizes of all volumes in the CPG and the amount of disk space they are currently using. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 5.722643930878938

  - `compressRatio` (number)
    Ratio between the amount of data written to Dedup Volumes and the amount that is not duplicated. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 4.233684210526316

  - `compressSavings` (integer,null)
    The space savings in MiB by compressing data
    Example: 1

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `dataReduceRatio` (number)
    Ratio between the amount written to all volumes in the CPG and the amount of disk space used after compression and deduplication
    Example: 2.25

  - `dedupCapable` (boolean)
    Indicates whether the CPG supports dedup
    Example: true

  - `dedupRatio` (number)
    Ratio between the amount of data written to Dedup Volumes and the amount that is not duplicated. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 2.2464644143676713

  - `dedupSavings` (integer,null)
    Savings from dedup in MiB
    Example: 1

  - `dedupVersion` (object,null)
    Version of Dedup that is being used by volumes in the CPG

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "CPG Vega_7_test"

  - `domain` (string)
    Name of the domain that the CPG belongs to
    Example: "testdomain"

  - `freeForAllocationMiB` (number)
    Estimated free space for volume allocation (MiB)
    Example: 4141056

  - `freeSizeMiB` (number)
    Number of LD MiB allocated and available in the CPG. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 44672

  - `freeSizeRawMiB` (number)
    Number of physical (raw) MiB allocated and available in the CPG. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 16896

  - `generation` (integer,null)
    generation

  - `hostWrt` (integer,null)
    Host writes in MiB
    Example: 1

  - `name` (string)
    Name of the resource
    Example: "Vega_7_test"

  - `nonReducibleData` (integer,null)
    Amount of data that could not be reduced
    Example: 2

  - `numberOfSnapRc` (number,null)
    Number of VVs used for Remote copy snapshot CPG usage
    Example: 5

  - `numberOfTdVv` (number)
    Number of TDVVs using the CPG
    Example: 14

  - `numberOfTpVv` (number)
    Number of TPVVs using the CPG
    Example: 1062

  - `numberOfUserRc` (number)
    Number of VVs used for Remote copy user CPG usage
    Example: 5

  - `overProvRatio` (number)
    Ratio between the virtual sizes of all volumes and the amount of used and free disk spaces. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 0.58

  - `reduceSavings` (integer,null)
    Savings from data reduction in MiB and this is the combination of compression and dedup savings
    Example: 2

  - `reducibleReduceSavings` (integer,null)
    Data reduction savings in MiB using the reducible data. This savings is the combination of compression and dedup savings.
    Example: 2

  - `reducibleReduceSavingsRatio` (number,null)
    Data reduction savings ratio using the reducible data. This savings ratio is the combination of compression and dedup savings.
    Example: 0.08

  - `resourceUri` (string)
    resourceUri for detailed storage-pool object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE809P009/storage-pools/8fdba044f8d90c7922c17b9340b65178"

  - `saGrow` (object,null)
    CPG grow information

  - `saGrow.args` (string)
    The admin/data LD creation arguments used by the CPG when growing new LDs
    Example: "-p -devtype SSD"

  - `saGrow.limitMiB` (number)
    Limit size in MiB beyond which the admin/data space will not grow
    Example: 10

  - `saGrow.sizeMiB` (number)
    Amount of admin/data LD storage in MiB created on each auto-grow
    Example: 12

  - `saGrow.warnMiB` (number)
    Size in MiB of the admin/data space at which a warning alert is generated
    Example: 10

  - `sdGrow` (object,null)
    CPG grow information

  - `sharedSizeMiB` (number)
    Number of LD MiB shared between volumes via deduplication
    Example: 512

  - `snapSizePrivateMiB` (number)
    Number of LD MiB private to individual snapshot virtual volumes, not shared by deduplication. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 526848

  - `snapSizeRawMiB` (number)
    Number of physical (raw) MiB used in snapshot virtual volumes. Updated in Cloud Data Store at most once per 30 minutes.
    Example: 56831

  - `snapSpaceAdmin` (object,null)
    snapSpace information

  - `snapSpaceAdmin.ldCount` (number)
    Number of Logical Disks
    Example: 4

  - `snapSpaceAdmin.totalMiB` (number)
    Total logical capacity (MiB)
    Example: 83968

  - `snapSpaceAdmin.totalRawMiB` (number)
    Total physical (raw) capacity (MiB)
    Example: 251904

  - `snapSpaceAdmin.usedMiB` (number)
    Used logical capacity (MiB)
    Example: 75008

  - `snapSpaceAdmin.usedRawMiB` (number)
    Used physical (raw) capacity (MiB)
    Example: 225024

  - `snapSpaceData` (object,null)
    snapSpace information

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `storagePoolId` (number)
    Numeric ID of the resource
    Example: 4

  - `systemId` (string)
    SystemID of the array
    Example: "7CE809P009"

  - `thinSavings` (integer,null)
    The space savings from a fully allocated virtual volume (CPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space.
    Example: 1

  - `thinSavingsRatio` (number,null)
    The space savings ratio from a fully allocated virtual volume (FPVV) to a thinly allocated VV (TPVV). This ratio is got by dividing the Provisioned size by host written space.
    Example: 0.08

  - `totalReservedMiB` (number)
    Total amount of space reserved by CPG  (MiB)
    Example: 1806336

  - `totalSavings` (integer,null)
    Total space savings including thin, compression, dedup, clone, zero packing, and snaps, in MiB
    Example: 2

  - `totalSavingsRatio` (number,null)
    Total space savings ratio including thin, compression, dedup, clone, zero packing, and snaps
    Example: 0.08

  - `totalSizeMiB` (integer)
    Total logical capacity in the user/snapshot space (MiB)
    Example: 122880

  - `totalSizeRawMiB` (number)
    Total physical (raw) MiB in the user/snapshot space
    Example: 163839

  - `userSpace` (object,null)
    snapSpace information

  - `volumesCount` (integer,null)
    Number of volumes in the CPG.
    Example: 5

  - `warnPercent` (number)
    Allocation warning percentage
    Example: 5

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


