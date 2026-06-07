---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchesgetbyid.md"
scraped_at: "2026-06-07T06:16:14.700787+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Switch identified by {id}

Get details of HPE Alletra Storage MP B10000 Switch identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the switch
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

  - `activeIpAddress` (string,null)
    Switch active IP Address
    Example: "16.1.9.251"

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

  - `dhcpServers` (array,null)

  - `dhcpServers.status` (string,null)
    DHCP status
    Example: "operational"

  - `dhcpServers.vrfName` (string,null)
    DHCP VRF Name
    Example: "inband"

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Switch sw2"

  - `domain` (string,null)
    Domain that the resource belongs to
    Example: "switch"

  - `fanState` (object,null)
    State of the resource

  - `fanState.detailed` (array,null)
    Array of the detailed states of the resource

  - `fanState.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `fwVersion` (string,null)
    Switch firmware version
    Example: "GL.10.11.0001"

  - `generation` (integer,null)
    generation

  - `locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `macAddress` (string,null)
    MAC address of the switch
    Example: "90:20:c2:c2:35:00"

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

  - `mode` (string,null)
    Switch mode
    Example: "online"

  - `name` (string,null)
    Name of the resource.
    Example: "sw1"

  - `primaryPath` (string,null)
    Switch primary path state
    Example: "Active"

  - `ps1State` (object,null)
    State of the resource

  - `ps2State` (object,null)
    State of the resource

  - `resourceUri` (string,null)
    resourceUri for detailed enclosure object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/enclosures/9c3c4f29a82fd8d632ff379116fa0b8f/enclosure-cards/8621946048c1cb24bdfc57e9b3b460ac"

  - `secondaryPath` (string,null)
    Switch secondary path state
    Example: "Inactive"

  - `state` (object,null)
    State of the resource

  - `switchFans` (object,null)

  - `switchFans.items` (array,null)

  - `switchFans.items.localizedSpeedA` (object,null)
    Switch fan localized speed

  - `switchFans.items.localizedSpeedA.default` (string,null)
    default value of switch fan localized speed
    Example: "Normal"

  - `switchFans.items.localizedSpeedA.key` (string,null)
    key of switch fan localized speed
    Example: "SWITCH_FAN_SPEED_NORMAL"

  - `switchFans.items.localizedSpeedB` (object,null)
    Switch fan localized speed

  - `switchFans.items.speedA` (string,null)
    Switch fan speed
    Example: "normal"

  - `switchFans.items.speedB` (string,null)
    Switch fan speed
    Example: "normal"

  - `switchFans.items.stateA` (object,null)
    State of the resource

  - `switchFans.items.stateB` (object,null)
    State of the resource

  - `switchFans.items.switchFanId` (integer,null)
    ID of the resource
    Example: 1

  - `switchFans.items.switchName` (string,null)
    Switch name
    Example: "sw1"

  - `switchFans.items.switchUid` (string,null)
    Switch UID
    Example: "2bc9220b01fae89ef88f10994394b180"

  - `switchFans.items.systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

  - `switchId` (integer,null)
    ID of the resource
    Example: 1

  - `switchPort` (object,null)

  - `switchPowerSupplies` (object,null)

  - `temperatureDetail` (string,null)
    Switch mode
    Example: "online"

  - `temperatureState` (object,null)
    State of the resource

  - `vlans` (array,null)

  - `vlans.operationalState` (string,null)
    Status of vlan
    Example: "ok"

  - `vlans.vlanId` (integer,null)
    Vlan ID
    Example: 1

  - `vlans.vlanName` (string,null)
    Vlan Name
    Example: "DEFAULT_VLAN_1"

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


