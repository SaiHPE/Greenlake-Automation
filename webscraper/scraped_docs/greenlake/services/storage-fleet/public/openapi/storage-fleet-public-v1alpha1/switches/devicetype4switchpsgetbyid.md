---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ps/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/switches/devicetype4switchpsgetbyid.md"
scraped_at: "2026-06-07T06:16:01.678277+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Switch Power Supplies identified by {switchId} and {id}

Get details of HPE Alletra Storage MP B10000 Switch Power Supplies identified by {switchId} and {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ps/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `switchId` (string, required)
    UID of the switch
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `id` (string, required)
    UID of the switch fan
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

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Fan 5"

  - `domain` (string,null)
    Domain that the resource belongs to
    Example: "switch"

  - `generation` (integer,null)
    generation

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
    Example: "Tray-1/5/1"

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/switches/9c3c4f29a82fd8d632ff379116fa0b8f/switch-ps/8621946048c1cb24bdfc57e9b3b460ac"

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `switchName` (string,null)
    Switch name
    Example: "sw1"

  - `switchPsId` (integer,null)
    ID of the resource
    Example: 1

  - `switchUid` (string,null)
    Switch UID
    Example: "2bc9220b01fae89ef88f10994394b180"

  - `systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

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


