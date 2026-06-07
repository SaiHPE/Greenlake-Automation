---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosuresgetbyid.md"
scraped_at: "2026-06-07T06:16:12.405114+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Enclosure identified by {id}

Get details of HPE Alletra Storage MP B10000 Enclosure identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the enclosure
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource.
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `type` (string, required)
    type
    Example: "string"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `chainPosLoopA` (integer,null)

  - `chainPosLoopB` (integer,null)

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

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `dcsdata` (object,null)

  - `dcsdata.fwStatus` (string,null)

  - `dcsdata.fwVersion` (string,null)

  - `detailedState` (string,null)

  - `displayname` (string,null)
    Enclosure Display name

  - `domain` (string,null)
    Domain that the resource belongs to

  - `enclosureId` (integer,null)
    Numeric ID of the resource

  - `enclosureType` (string)
    Enclosure Type.
    Enum: "ENCLOSURE_UNKNOWN", "ENCLOSURE_DC0", "ENCLOSURE_DC1", "ENCLOSURE_DC2", "ENCLOSURE_DC3", "ENCLOSURE_DC4", "ENCLOSURE_DCS1", "ENCLOSURE_DCS2", "ENCLOSURE_DCN1", "ENCLOSURE_DCS3", "ENCLOSURE_DCS4", "ENCLOSURE_DCS5", "ENCLOSURE_DCS6", "ENCLOSURE_DCS7", "ENCLOSURE_DCS8", "ENCLOSURE_DCN2", "ENCLOSURE_DCN3", "ENCLOSURE_DCN4", "ENCLOSURE_DCS9", "ENCLOSURE_DCS10", "ENCLOSURE_DCS11", "ENCLOSURE_DCN5", "ENCLOSURE_DCS12", "ENCLOSURE_DCN6", "ENCLOSURE_DCN7", "ENCLOSURE_10000", "ENCLOSURE_DCF1", "ENCLOSURE_DCF2", "ENCLOSURE_10001"

  - `errors` (array,null)
    Errors occurred in enclosure

  - `errors.alarmCode` (string,null)
    Alarm code

  - `errors.alarmText` (string,null)

  - `errors.iom` (string)

  - `failIndicator` (boolean,null)

  - `failRequested` (boolean,null)

  - `formFactor` (string,null)
    Example: "SFF"

  - `generation` (integer,null)
    generation

  - `locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `location` (string,null)
    Location of the resource

  - `loopSplit` (boolean,null)
    Example: true

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

  - `name` (string,null)
    Name of the resource.
    Example: "cage1"

  - `nodeWwn` (string,null)
    WWn of the node resource
    Example: "50050CC106233428"

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f"

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `subType` (string,null)
    Enclosure sub type

  - `systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

  - `warnIndicator` (boolean,null)

  - `warnRequested` (boolean,null)

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


