---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosure-cards"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurecardlist.md"
scraped_at: "2026-06-07T06:16:11.102115+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {systemId}

Get details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosure-cards
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter enclosure resource by Key.
    Example: "systemWWN eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort enclosure resource by Key.
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
    Unique Identifier of the resource. Filter
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

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
    Example: "string"

  - `items.dcsdata` (object,null)

  - `items.dcsdata.fwStatus` (string,null)

  - `items.dcsdata.fwVersion` (string,null)

  - `items.dcsdata.master` (boolean,null)

  - `items.displayname` (string,null)
    Enclosure Display name

  - `items.domain` (string,null)
    Domain that the resource belongs to

  - `items.elementStatusCode` (string,null)
    Enclosure status code

  - `items.enclosureCardId` (integer,null)
    ID of enclosure card.

  - `items.enclosureId` (integer,null)
    Example: 1

  - `items.enclosureName` (string,null)
    Name of the enclosure. Filter, Sort

  - `items.enclosureType` (string)
    Enclosure Type.
    Enum: "ENCLOSURE_UNKNOWN", "ENCLOSURE_DC0", "ENCLOSURE_DC1", "ENCLOSURE_DC2", "ENCLOSURE_DC3", "ENCLOSURE_DC4", "ENCLOSURE_DCS1", "ENCLOSURE_DCS2", "ENCLOSURE_DCN1", "ENCLOSURE_DCS3", "ENCLOSURE_DCS4", "ENCLOSURE_DCS5", "ENCLOSURE_DCS6", "ENCLOSURE_DCS7", "ENCLOSURE_DCS8", "ENCLOSURE_DCN2", "ENCLOSURE_DCN3", "ENCLOSURE_DCN4", "ENCLOSURE_DCS9", "ENCLOSURE_DCS10", "ENCLOSURE_DCS11", "ENCLOSURE_DCN5", "ENCLOSURE_DCS12", "ENCLOSURE_DCN6", "ENCLOSURE_DCN7", "ENCLOSURE_10000", "ENCLOSURE_DCF1", "ENCLOSURE_DCF2", "ENCLOSURE_10001"

  - `items.enclosureUid` (string,null)
    Parent UID of the resource. Filter
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `items.failIndicator` (boolean,null)

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.isNodeCard` (boolean,null)

  - `items.locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `items.locateSevenSegDisplay` (string,null)
    Seven segment display on enclosure card when locate is on

  - `items.loopA` (boolean,null)

  - `items.loopB` (boolean,null)

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

  - `items.name` (string,null)
    Name of the resource. Filter, Sort
    Example: "SASB"

  - `items.resourceUri` (string,null)
    resourceUri for detailed enclosure card object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f/enclosure-cards/8621946048c1cb24bdfc57e9b3b460ac"

  - `items.safeToRemove` (boolean,null)

  - `items.sevenSegDisplay` (string,null)
    Seven segment display

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

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


