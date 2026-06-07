---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4disksgetbyid.md"
scraped_at: "2026-06-07T06:16:11.411917+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 disk identified by {cageId} and {id}

Get details of HPE Alletra Storage MP B10000 disk identified by {cageId} and {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `cageId` (string, required)
    cage ID
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `id` (string, required)
    UID of the disk
    Example: "d4b13e70924d29afdb77d932f7563ea6"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource
    Example: "d4b13e70924d29afdb77d932f7563ea6"

  - `type` (string, required)
    type
    Example: "string"

  - `admitTime` (object,null)
    admission time of disk

  - `admitTime.ms` (integer,null)
    time in millisecond
    Example: 1591599192000

  - `admitTime.tz` (string,null)
    timezone
    Example: "Asia/Calcutta"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `capacity` (object,null)
    Capacity of the Disk

  - `capacity.allocatedMiB` (integer,null)
    allocated Size in MiB
    Example: 595968

  - `capacity.failedMiB` (integer,null)
    failed Size in MiB

  - `capacity.freeMiB` (integer,null)
    free Size in MiB
    Example: 1233920

  - `capacity.totalMiB` (integer,null)
    total Size in MiB.
    Example: 595968

  - `capacity.unavailableMiB` (integer,null)
    unavailable Size in MiB

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

  - `consumableSizeMiB` (integer,null)
    consumable size of disk in MiB
    Example: 1829888

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `devType` (string,null)
    Type of the disk
    Example: "DEVTYPE_SSD"

  - `diskId` (integer,null)
    id of the disk
    Example: 1

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `domain` (string,null)
    Domain that the resource belongs to

  - `enclosureUid` (string,null)
    Unique Identifier of the enclosure
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `fwStatus` (string,null)
    firmware status
    Example: "--"

  - `fwVersion` (string,null)
    firmware version
    Example: "3P00"

  - `generation` (integer,null)
    generation

  - `insertTime` (object,null)
    admission time of disk

  - `manufacturing` (object,null)
    Manufacturing information

  - `manufacturing.assemblyRev` (string,null)
    Assembly revision
    Example: "002*"

  - `manufacturing.checkSum` (string,null)
    Checksum
    Example: "--"

  - `manufacturing.hpeModelName` (string,null)
    HPE model name
    Example: "HPE 3PAR 600 2S Node"

  - `manufacturing.manufacturer` (string,null)
    Manufacturer.
    Example: "XYRATEX"

  - `manufacturing.model` (string,null)
    Model
    Example: "0974244-06"

  - `manufacturing.saleablePartNumber` (string,null)
    Saleable part number
    Example: "0974244-06"

  - `manufacturing.saleableSerialNumber` (string,null)
    Saleable serial number
    Example: "4UW0002941"

  - `manufacturing.serialNumber` (string,null)
    Serial number.
    Example: "PMW0974244G4T88"

  - `manufacturing.sparePartNumber` (string,null)
    Spare part number
    Example: "P04031-001"

  - `mediaType` (string,null)
    Media Type of the disk
    Example: "MLC"

  - `paths` (array,null)
    Disk Loop

  - `paths.degraded` (boolean,null)
    degraded loop

  - `paths.disabled` (boolean,null)
    disabled loop

  - `paths.port` (object,null)
    Port Position

  - `paths.port.node` (integer,null)
    node ID

  - `paths.port.port` (integer,null)
    port ID
    Example: 2

  - `paths.port.slot` (integer,null)
    slot ID

  - `paths.primary` (boolean,null)
    primary loop

  - `positionLast` (object,null)
    Disk Position

  - `positionLast.cage` (integer,null)
    cage ID

  - `positionLast.sled` (integer,null)
    sled ID
    Example: 2

  - `positionNow` (object,null)
    Disk Position Now

  - `protocol` (string,null)
    protocol over the disk
    Example: "SAS"

  - `rawSizeMiB` (integer,null)
    raw Size of disk in GB
    Example: 1831420

  - `readErrors` (object,null)
    Number of errors

  - `readErrors.correctable` (integer,null)
    correctable errors

  - `readErrors.uncorrectable` (integer,null)
    uncorrectable errors

  - `resourceUri` (string,null)
    resourceUri for detailed disk object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/enclosures/0/disks/d4b13e70924d29afdb77d932f7563ea6"

  - `sedStatus` (string,null)
    SED Status
    Example: "FIPS Capable"

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `systemId` (string,null)
    SystemId / SerialNumber of the array
    Example: "7CE751P312"

  - `writeErrors` (object,null)
    Number of errors

  - `wwn` (string,null)
    unique WWN of the disk
    Example: "5002538B10249591"

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


