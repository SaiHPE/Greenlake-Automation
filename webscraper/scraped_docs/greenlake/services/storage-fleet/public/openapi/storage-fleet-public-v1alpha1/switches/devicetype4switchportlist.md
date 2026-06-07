---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/switches/devicetype4switchportlist.md"
scraped_at: "2026-06-07T06:16:01.229095+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Switch ports identified by {switchId}

Get details of HPE Alletra Storage MP B10000 Switch ports identified by {switchId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `switchId` (string, required)
    UID of the switch
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter switch resource by Key.
    Example: "systemWWN eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort switch resource by Key.
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

  - `items.device` (string,null)
    Device (either node or IOM) to which the switch port is connected to
    Example: "node1"

  - `items.devicePort` (string,null)
    Port on device that the switch port is connected to
    Example: "2:2"

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "Switch sw1 port 14"

  - `items.domain` (string,null)
    Domain that the resource belongs to
    Example: "switch"

  - `items.enclosure` (string,null)
    Enclosure (cage) to which the switch port is connected to
    Example: "cage1"

  - `items.generation` (integer,null)

  - `items.ipAddress` (string,null)
    Switch port IP Address
    Example: "16.1.9.2"

  - `items.macAddress` (string,null)
    MAC address of the switch port
    Example: "90:20:c2:c2:35:00"

  - `items.portDescription` (string,null)
    Switch port description
    Example: "eth14"

  - `items.resourceUri` (string,null)
    resourceUri for detailed switch port object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/switch-port/8621946048c1cb24bdfc57e9b3b460ac"

  - `items.sfp` (object,null)
    SFP detail of switch port. This is available from OS version 10.5.0 and above.

  - `items.sfp.cableLength` (string,null)
    Switch port SFP cable length
    Example: "2.00"

  - `items.sfp.cableTechnology` (string,null)
    Switch port SFP cable technology
    Example: "active"

  - `items.sfp.connector` (string,null)
    Switch port SFP connector
    Example: "QSFP28_AOC"

  - `items.sfp.connectorStatus` (string,null)
    Switch port SFP connector status
    Example: "supported"

  - `items.sfp.formFactor` (string,null)
    Switch port SFP form factor

  - `items.sfp.longXcvrDesc` (string,null)
    Switch port SFP long xcvr desc
    Example: "100G QSFP28 2m AOC"

  - `items.sfp.maxSpeed` (string,null)
    Switch port SFP max speed
    Example: 100000

  - `items.sfp.propPartNumber` (string,null)
    Switch port SFP part number
    Example: "5400-3937"

  - `items.sfp.propProductNumber` (string,null)
    Switch port SFP product number
    Example: "JL856A"

  - `items.sfp.propSerialNumber` (string,null)
    Switch port SFP serial number
    Example: "CN26L1319D"

  - `items.sfp.vendorName` (string,null)
    Switch port SFP vendor name
    Example: "FINISAR CORP"

  - `items.sfp.vendorOui` (string,null)
    Switch port SFP vendor OUI
    Example: "00-90-65"

  - `items.sfp.vendorPartNumber` (string,null)
    Switch port SFP vendor part number
    Example: "FCBN425QE2C02-PR"

  - `items.sfp.vendorRevision` (string,null)
    Switch port SFP vendor revision
    Example: "A0"

  - `items.sfp.vendorSerialNumber` (string,null)
    Switch port SFP vendor serial number
    Example: "CN26L13023"

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.switchName` (string,null)
    Switch name.
    Example: "sw1"

  - `items.switchPortId` (integer,null)
    ID of the resource
    Example: 1

  - `items.switchUid` (string,null)
    Switch UID
    Example: "9c3c4f29a82fd8d632ff379116fa0b8f"

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


