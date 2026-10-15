---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchportgetbyid.md"
scraped_at: "2026-06-07T06:16:15.229494+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Switch Port identified by {switchId} and {id}

Get details of HPE Alletra Storage MP B10000 Switch identified by {switchId} and {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports/{id}
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

  - `device` (string,null)
    Device (either node or IOM) to which the switch port is connected to.
    Example: "node1"

  - `devicePort` (string,null)
    Port on device that the switch port is connected to
    Example: "2:2"

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Switch sw1 port 14"

  - `domain` (string,null)
    Domain that the resource belongs to
    Example: "switch"

  - `enclosure` (string,null)
    Enclosure (cage) to which the switch port is connected to
    Example: "cage1"

  - `generation` (integer,null)
    generation Filter, Sort

  - `ipAddress` (string,null)
    Switch port IP Address
    Example: "16.1.9.2"

  - `macAddress` (string,null)
    MAC address of the switch port
    Example: "90:20:c2:c2:35:00"

  - `portDescription` (string,null)
    Switch port description
    Example: "eth14"

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/switches/9c3c4f29a82fd8d632ff379116fa0b8f/switch-port/8621946048c1cb24bdfc57e9b3b460ac"

  - `sfp` (object,null)
    SFP detail of switch port. This is available from OS version 10.5.0 and above.

  - `sfp.cableLength` (string,null)
    Switch port SFP cable length
    Example: "2.00"

  - `sfp.cableTechnology` (string,null)
    Switch port SFP cable technology
    Example: "active"

  - `sfp.connector` (string,null)
    Switch port SFP connector
    Example: "QSFP28_AOC"

  - `sfp.connectorStatus` (string,null)
    Switch port SFP connector status
    Example: "supported"

  - `sfp.formFactor` (string,null)
    Switch port SFP form factor

  - `sfp.longXcvrDesc` (string,null)
    Switch port SFP long xcvr desc
    Example: "100G QSFP28 2m AOC"

  - `sfp.maxSpeed` (string,null)
    Switch port SFP max speed
    Example: 100000

  - `sfp.propPartNumber` (string,null)
    Switch port SFP part number
    Example: "5400-3937"

  - `sfp.propProductNumber` (string,null)
    Switch port SFP product number
    Example: "JL856A"

  - `sfp.propSerialNumber` (string,null)
    Switch port SFP serial number
    Example: "CN26L1319D"

  - `sfp.vendorName` (string,null)
    Switch port SFP vendor name
    Example: "FINISAR CORP"

  - `sfp.vendorOui` (string,null)
    Switch port SFP vendor OUI
    Example: "00-90-65"

  - `sfp.vendorPartNumber` (string,null)
    Switch port SFP vendor part number
    Example: "FCBN425QE2C02-PR"

  - `sfp.vendorRevision` (string,null)
    Switch port SFP vendor revision
    Example: "A0"

  - `sfp.vendorSerialNumber` (string,null)
    Switch port SFP vendor serial number
    Example: "CN26L13023"

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `switchName` (string,null)
    Switch name.
    Example: "sw1"

  - `switchPortId` (integer,null)
    ID of the resource
    Example: 1

  - `switchUid` (string,null)
    Switch UID
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

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


