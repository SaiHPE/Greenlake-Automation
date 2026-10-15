---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/shelves/devicetype4enclosurecardsgetbyid.md"
scraped_at: "2026-06-07T06:15:57.879437+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Enclosure Card identified by {enclosureId} and {id}

Get details of HPE Alletra Storage MP B10000 Enclosure Card identified by {enclosureId} and {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards/{id}
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
    UID of the enclosure card
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

  - `dcsdata` (object,null)

  - `dcsdata.fwStatus` (string,null)

  - `dcsdata.fwVersion` (string,null)

  - `dcsdata.master` (boolean,null)

  - `displayname` (string,null)
    Enclosure Display name

  - `domain` (string,null)
    Domain that the resource belongs to

  - `elementStatusCode` (string,null)
    Enclosure status code

  - `enclosureCardBootDrives` (object,null)

  - `enclosureCardBootDrives.count` (integer)
    Number of items
    Example: 1

  - `enclosureCardBootDrives.items` (array,null)

  - `enclosureCardBootDrives.items.enclosureCardId` (integer,null)
    ID of enclosure card.

  - `enclosureCardBootDrives.items.enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card.

  - `enclosureCardBootDrives.items.enclosureId` (integer,null)
    ID of the enclosure
    Example: 9

  - `enclosureCardBootDrives.items.enclosureUid` (string,null)
    Unique Identifier of the enclosure

  - `enclosureCardBootDrives.items.euiWwn` (string,null)
    EUI/WWN

  - `enclosureCardBootDrives.items.fwVersion` (string,null)
    Firmware version

  - `enclosureCardBootDrives.items.generation` (integer,null)
    generation

  - `enclosureCardBootDrives.items.manufacturing` (object,null)
    Manufacturing information

  - `enclosureCardBootDrives.items.manufacturing.assemblyRev` (string,null)
    Assembly revision
    Example: "002*"

  - `enclosureCardBootDrives.items.manufacturing.checkSum` (string,null)
    Checksum
    Example: "--"

  - `enclosureCardBootDrives.items.manufacturing.hpeModelName` (string,null)
    HPE model name
    Example: "HPE 3PAR 600 2S Node"

  - `enclosureCardBootDrives.items.manufacturing.manufacturer` (string,null)
    Manufacturer.
    Example: "XYRATEX"

  - `enclosureCardBootDrives.items.manufacturing.model` (string,null)
    Model
    Example: "0974244-06"

  - `enclosureCardBootDrives.items.manufacturing.saleablePartNumber` (string,null)
    Saleable part number
    Example: "0974244-06"

  - `enclosureCardBootDrives.items.manufacturing.saleableSerialNumber` (string,null)
    Saleable serial number
    Example: "4UW0002941"

  - `enclosureCardBootDrives.items.manufacturing.serialNumber` (string,null)
    Serial number.
    Example: "PMW0974244G4T88"

  - `enclosureCardBootDrives.items.manufacturing.sparePartNumber` (string,null)
    Spare part number
    Example: "P04031-001"

  - `enclosureCardBootDrives.items.path` (string,null)
    path

  - `enclosureCardBootDrives.items.sedStatus` (string,null)
    SED state of disk

  - `enclosureCardBootDrives.items.sizeMiB` (integer,null)
    Size in MiB

  - `enclosureCardBootDrives.items.slot` (integer,null)
    Slot this boot drive reside in

  - `enclosureCardBootDrives.items.systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

  - `enclosureCardBootDrives.offset` (integer,null)
    page offset
    Example: 1

  - `enclosureCardBootDrives.total` (integer)
    Total items
    Example: 1

  - `enclosureCardCpu` (object,null)

  - `enclosureCardFan` (object,null)

  - `enclosureCardMem` (object,null)

  - `enclosureCardPci` (object,null)

  - `enclosureCardTpm` (object,null)

  - `enclosureId` (integer,null)
    Example: 1

  - `enclosureName` (string,null)
    Name of the enclosure.

  - `enclosureType` (string)
    Enclosure Type.
    Enum: "ENCLOSURE_UNKNOWN", "ENCLOSURE_DC0", "ENCLOSURE_DC1", "ENCLOSURE_DC2", "ENCLOSURE_DC3", "ENCLOSURE_DC4", "ENCLOSURE_DCS1", "ENCLOSURE_DCS2", "ENCLOSURE_DCN1", "ENCLOSURE_DCS3", "ENCLOSURE_DCS4", "ENCLOSURE_DCS5", "ENCLOSURE_DCS6", "ENCLOSURE_DCS7", "ENCLOSURE_DCS8", "ENCLOSURE_DCN2", "ENCLOSURE_DCN3", "ENCLOSURE_DCN4", "ENCLOSURE_DCS9", "ENCLOSURE_DCS10", "ENCLOSURE_DCS11", "ENCLOSURE_DCN5", "ENCLOSURE_DCS12", "ENCLOSURE_DCN6", "ENCLOSURE_DCN7", "ENCLOSURE_10000", "ENCLOSURE_DCF1", "ENCLOSURE_DCF2", "ENCLOSURE_10001"

  - `enclosureUid` (string,null)
    Parent UID of the resource.
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

  - `failIndicator` (boolean,null)

  - `isNodeCard` (boolean,null)

  - `locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `locateSevenSegDisplay` (string,null)
    Seven segment display on enclosure card when locate is on

  - `loopA` (boolean,null)

  - `loopB` (boolean,null)

  - `name` (string,null)
    Name of the resource.
    Example: "SASB"

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f/enclosure-cards/8621946048c1cb24bdfc57e9b3b460ac"

  - `safeToRemove` (boolean,null)

  - `sevenSegDisplay` (string,null)
    Seven segment display

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

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


