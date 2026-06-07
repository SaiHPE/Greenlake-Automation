---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switcheslist.md"
scraped_at: "2026-06-07T06:16:14.740176+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Switches

Get details of HPE Alletra Storage MP B10000 Switches

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches
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

  - `items.activeIpAddress` (string,null)
    Switch active IP Address
    Example: "16.1.9.251"

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

  - `items.dhcpServers` (array,null)

  - `items.dhcpServers.status` (string,null)
    DHCP status
    Example: "operational"

  - `items.dhcpServers.vrfName` (string,null)
    DHCP VRF Name
    Example: "inband"

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "Switch sw2"

  - `items.domain` (string,null)
    Domain that the resource belongs to
    Example: "switch"

  - `items.fanState` (object,null)
    State of the resource

  - `items.fanState.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.fanState.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.fwVersion` (string,null)
    Switch firmware version
    Example: "GL.10.11.0001"

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `items.macAddress` (string,null)
    MAC address of the switch
    Example: "90:20:c2:c2:35:00"

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

  - `items.mode` (string,null)
    Switch mode
    Example: "online"

  - `items.name` (string,null)
    Name of the resource. Filter
    Example: "sw1"

  - `items.primaryPath` (string,null)
    Switch primary path state
    Example: "Active"

  - `items.ps1State` (object,null)
    State of the resource

  - `items.ps2State` (object,null)
    State of the resource

  - `items.resourceUri` (string,null)
    resourceUri for detailed switch object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/switches/8621946048c1cb24bdfc57e9b3b460ac"

  - `items.secondaryPath` (string,null)
    Switch secondary path state
    Example: "Inactive"

  - `items.state` (object,null)
    State of the resource

  - `items.switchId` (integer,null)
    ID of the resource
    Example: 1

  - `items.systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

  - `items.temperatureDetail` (string,null)
    Switch mode
    Example: "online"

  - `items.temperatureState` (object,null)
    State of the resource

  - `items.vlans` (array,null)

  - `items.vlans.operationalState` (string,null)
    Status of vlan
    Example: "ok"

  - `items.vlans.vlanId` (integer,null)
    Vlan ID
    Example: 1

  - `items.vlans.vlanName` (string,null)
    Vlan Name
    Example: "DEFAULT_VLAN_1"

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


