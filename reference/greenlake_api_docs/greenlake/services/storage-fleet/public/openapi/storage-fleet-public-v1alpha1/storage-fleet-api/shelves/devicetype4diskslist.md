---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4diskslist.md"
scraped_at: "2026-06-07T06:16:11.439136+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 disks identified by {cageId}

Get details of HPE Alletra Storage MP B10000 disks identified by {cageId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `cageId` (string, required)
    cage ID
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter Disk by Key.
    Example: "systemId eq 7CE751P312"

  - `sort` (string)
    oData query to sort Disk by Key.
    Example: "name asc"

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
    Unique Identifier of the resource. Filter
    Example: "d4b13e70924d29afdb77d932f7563ea6"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.admitTime` (object,null)
    admission time of disk

  - `items.admitTime.ms` (integer,null)
    time in millisecond
    Example: 1591599192000

  - `items.admitTime.tz` (string,null)
    timezone
    Example: "Asia/Calcutta"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.capacity` (object,null)
    Capacity of the Disk

  - `items.capacity.allocatedMiB` (integer,null)
    allocated Size in MiB
    Example: 595968

  - `items.capacity.failedMiB` (integer,null)
    failed Size in MiB

  - `items.capacity.freeMiB` (integer,null)
    free Size in MiB
    Example: 1233920

  - `items.capacity.totalMiB` (integer,null)
    total Size in MiB. Filter, Sort
    Example: 595968

  - `items.capacity.unavailableMiB` (integer,null)
    unavailable Size in MiB

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

  - `items.consumableSizeMiB` (integer,null)
    consumable size of disk in MiB
    Example: 1829888

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.devType` (string,null)
    Type of the disk.
    Example: "DEVTYPE_SSD"

  - `items.diskId` (integer,null)
    id of the disk
    Example: 1

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `items.domain` (string,null)
    Domain that the resource belongs to

  - `items.enclosureUid` (string,null)
    Unique Identifier of the enclosure
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `items.fwStatus` (string,null)
    firmware status
    Example: "--"

  - `items.fwVersion` (string,null)
    firmware version
    Example: "3P00"

  - `items.generation` (integer,null)
    generation

  - `items.insertTime` (object,null)
    admission time of disk

  - `items.manufacturing` (object,null)
    Manufacturing information

  - `items.manufacturing.assemblyRev` (string,null)
    Assembly revision
    Example: "002*"

  - `items.manufacturing.checkSum` (string,null)
    Checksum
    Example: "--"

  - `items.manufacturing.hpeModelName` (string,null)
    HPE model name
    Example: "HPE 3PAR 600 2S Node"

  - `items.manufacturing.manufacturer` (string,null)
    Manufacturer.
    Example: "XYRATEX"

  - `items.manufacturing.model` (string,null)
    Model
    Example: "0974244-06"

  - `items.manufacturing.saleablePartNumber` (string,null)
    Saleable part number
    Example: "0974244-06"

  - `items.manufacturing.saleableSerialNumber` (string,null)
    Saleable serial number
    Example: "4UW0002941"

  - `items.manufacturing.serialNumber` (string,null)
    Serial number.
    Example: "PMW0974244G4T88"

  - `items.manufacturing.sparePartNumber` (string,null)
    Spare part number
    Example: "P04031-001"

  - `items.mediaType` (string,null)
    Media Type of the disk
    Example: "MLC"

  - `items.paths` (array,null)
    Disk Loop

  - `items.paths.degraded` (boolean,null)
    degraded loop

  - `items.paths.disabled` (boolean,null)
    disabled loop

  - `items.paths.port` (object,null)
    Port Position

  - `items.paths.port.node` (integer,null)
    node ID

  - `items.paths.port.port` (integer,null)
    port ID
    Example: 2

  - `items.paths.port.slot` (integer,null)
    slot ID

  - `items.paths.primary` (boolean,null)
    primary loop

  - `items.positionLast` (object,null)
    Disk Position

  - `items.positionLast.cage` (integer,null)
    cage ID

  - `items.positionLast.sled` (integer,null)
    sled ID
    Example: 2

  - `items.positionNow` (object,null)
    Disk Position Now

  - `items.positionNow.cage` (integer,null)
    cage ID. Filter, Sort

  - `items.positionNow.sled` (integer,null)
    sled ID.
    Example: 2

  - `items.protocol` (string,null)
    protocol over the disk
    Example: "SAS"

  - `items.rawSizeMiB` (integer,null)
    raw Size of disk in GB
    Example: 1831420

  - `items.readErrors` (object,null)
    Number of errors

  - `items.readErrors.correctable` (integer,null)
    correctable errors

  - `items.readErrors.uncorrectable` (integer,null)
    uncorrectable errors

  - `items.resourceUri` (string,null)
    resourceUri for detailed disk object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/enclosures/0/disks/d4b13e70924d29afdb77d932f7563ea6"

  - `items.sedStatus` (string,null)
    SED Status
    Example: "FIPS Capable"

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.systemId` (string,null)
    SystemId/SerialNumber of the array.
    Example: "7CE751P312"

  - `items.writeErrors` (object,null)
    Number of errors

  - `items.wwn` (string,null)
    unique WWN of the disk. Filter, Sort
    Example: "5002538B10249591"

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


