---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/shelves/devicetype4enclosuresledsgetbyid.md"
scraped_at: "2026-06-07T06:15:58.590727+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Enclosure Sled identified by {enclosureId} and {id}

Get details of HPE Alletra Storage MP B10000 Enclosure Sled identified by {enclosureId} and {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `enclosureId` (string, required)
    UID of the enclosure
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `id` (string, required)
    UID of the enclosure sled
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

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

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

  - `dc4data` (object,null)

  - `dc4data.hplLed` (string,null)
    LED state.
    Enum: "LED_UNKNOWN", "LED_OFF", "LED_GREEN", "LED_GREEN_BLNK", "LED_AMBER", "LED_AMBER_BLNK", "LED_BLUE", "LED_BLUE_BLNK"

  - `dc4data.left` (boolean,null)

  - `dc4data.right` (boolean,null)

  - `dc4data.systemLed` (string,null)
    LED state.
    Enum: "LED_UNKNOWN", "LED_OFF", "LED_GREEN", "LED_GREEN_BLNK", "LED_AMBER", "LED_AMBER_BLNK", "LED_BLUE", "LED_BLUE_BLNK", null

  - `diskCount` (integer,null)
    Number of disks present
    Example: 1

  - `displayname` (string,null)
    Enclosure Display name

  - `domain` (string,null)
    Domain that the resource belongs to

  - `elementStatusCode` (string,null)
    Enclosure status code

  - `enclosureId` (integer)
    Example: 1

  - `enclosureName` (string,null)
    Name of the enclosure

  - `enclosureType` (string)
    Enclosure Type.
    Enum: "ENCLOSURE_UNKNOWN", "ENCLOSURE_DC0", "ENCLOSURE_DC1", "ENCLOSURE_DC2", "ENCLOSURE_DC3", "ENCLOSURE_DC4", "ENCLOSURE_DCS1", "ENCLOSURE_DCS2", "ENCLOSURE_DCN1", "ENCLOSURE_DCS3", "ENCLOSURE_DCS4", "ENCLOSURE_DCS5", "ENCLOSURE_DCS6", "ENCLOSURE_DCS7", "ENCLOSURE_DCS8", "ENCLOSURE_DCN2", "ENCLOSURE_DCN3", "ENCLOSURE_DCN4", "ENCLOSURE_DCS9", "ENCLOSURE_DCS10", "ENCLOSURE_DCS11", "ENCLOSURE_DCN5", "ENCLOSURE_DCS12", "ENCLOSURE_DCN6", "ENCLOSURE_DCN7", "ENCLOSURE_10000", "ENCLOSURE_DCF1", "ENCLOSURE_DCF2", "ENCLOSURE_10001"

  - `enclosureUid` (string,null)
    Parent UID of the resource.
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `failIndicator` (boolean,null)

  - `generation` (integer,null)
    generation

  - `locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

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
    Example: "SASB"

  - `okIndicator` (boolean,null)

  - `portBypassA` (boolean,null)

  - `portBypassB` (boolean,null)

  - `power` (boolean,null)

  - `predFailIndicator` (boolean,null)

  - `protocol` (string,null)
    Example: "SAS"

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f/enclosure-sleds/8621946048c1cb24bdfc57e9b3b460ac"

  - `safeToRemove` (boolean,null)

  - `sledId` (integer,null)
    Numeric ID of the resource

  - `stateLoopA` (object,null)
    State of the resource

  - `stateLoopA.detailed` (array,null)
    Array of the detailed states of the resource

  - `stateLoopA.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `stateLoopB` (object,null)
    State of the resource

  - `systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

  - `wwn` (string,null)
    Example: "5000C500997AB7B0"

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


