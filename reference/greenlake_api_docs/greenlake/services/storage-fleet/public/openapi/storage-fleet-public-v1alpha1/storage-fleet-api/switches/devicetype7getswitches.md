---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype7getswitches.md"
scraped_at: "2026-06-07T06:16:15.589684+00:00Z"
---

# Get all switches of a HPE Alletra Storage MP X10000 system

Get all switches of a HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the storage system
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `filter` (string)
    Lucene query to filter Switches by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004007"

  - `sort` (string)
    Data query to sort Switch resource by Key.
    Example: "id desc"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier of the Storage system Switch. Filter, Sort
    Example: "default.switch-0"

  - `items.type` (string, required)
    Type of the resource.
    Example: "switch"

  - `items.apiVersion` (string,null)
    API version of the resource.
    Example: "sc.hpe.com/v1"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.clusterId` (string,null)
    The unique identifier of the Storage system to which the Switch belongs.
    Example: "123abcd4-5e67-890f-g123-4hi5j67kl8m9"

  - `items.clusterRef` (string,null)
    The URI of the Storage system to which the Switch belongs.
    Example: "/api/sc.hpe.com/v1/default/switch/switch-1"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    Customer ID for the Storage system Switch. Filter, Sort
    Example: "ab1c23456d78901e23fghijk456lm7no"

  - `items.generation` (integer,null)
    Generation. Filter, Sort
    Example: 1692945579

  - `items.kind` (string,null)
    Kind of the resource.
    Example: "Switch"

  - `items.numberOfPorts` (integer,null)
    Number of ports in the Switch.
    Example: 32

  - `items.partNumber` (string,null)
    Part number of the Switch. Filter
    Example: "AB123C"

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.serialNumber` (string,null)
    Serial number of the Switch. Filter, Sort
    Example: "AB1234C5D6"

  - `items.status` (object,null)
    Status of the Switch.

  - `items.status.conditions` (array,null)
    Conditions representing recent changes to the state of the Switch resource.

  - `items.status.conditions.lastTransitionTime` (string,null)
    Time of the last event.
    Example: "2023-08-24T07:14:03Z"

  - `items.status.conditions.message` (string,null)
    Describes the transition state.
    Example: "Successfully created and assigned to the Storage system"

  - `items.status.conditions.observedGeneration` (integer,null)
    Observed Generation.
    Example: 2

  - `items.status.conditions.reason` (string,null)
    Contains a programmatic identifier indicating the reason for the condition's last transition.
    Example: "SuccessfulCreate"

  - `items.status.conditions.status` (string,null)
    Status of the event.
    Example: "True"

  - `items.status.conditions.type` (string)
    Type of condition.
    Example: "Assigned"

  - `items.status.fanState` (string,null)
    Overall state of the Switch's fans.
    Example: "Ok"

  - `items.status.firmwareVersion` (string,null)
    Current firmware version for the backend fabric Switch.
    Example: "MOCK.1.0"

  - `items.status.internalNtpEnabledState` (string,null)
    Current state of NTP services in the Switch. If enabled, the Switch syncs time with the internalNtpServer and communicates that info to its DHCP clients (JBOFs).

  - `items.status.internalNtpServer` (string,null)
    The IP address or name of the NTP server the Switch can use for time syncing.

  - `items.status.lastModifiedTime` (string,null)
    UTC Time at which the status of this Switch was last updated.
    Example: "2023-08-24T07:14:33Z"

  - `items.status.locatorLedState` (string,null)
    State of the locator LED on the Switch.
    Example: "Off"

  - `items.status.macAddress` (string,null)
    MAC address of the Management Port.
    Example: "00:00:5e:00:53:00"

  - `items.status.managementIpAddress` (string,null)
    Current IP address of the management interface of the backend fabric Switch.
    Example: "192.168.1.1"

  - `items.status.operationalState` (string,null)
    State of the Switch.
    Example: "Good"

  - `items.status.powerSupplyOneState` (string,null)
    State of power supply One.
    Example: "Ok"

  - `items.status.powerSupplyZeroState` (string,null)
    State of power supply Zero.
    Example: "Ok"

  - `items.status.ready` (boolean,null)
    Status.
    Example: true

  - `items.status.switchFans` (array,null)
    Information about each fan in the Switch.

  - `items.status.switchFans.name` (string,null)
    Name of the fan.
    Example: "Tray-1/1/0"

  - `items.status.switchFans.speed` (string,null)
    A string description of fan speed.
    Example: "normal"

  - `items.status.switchFans.status` (string,null)
    Status of the fan.
    Example: "ok"

  - `items.status.switchId` (string,null)
    Switch ID.
    Example: "sw1"

  - `items.status.switchPorts` (array,null)
    Information about each port in the Switch.

  - `items.status.switchPorts.ipAddress` (string,null)
    IP Address of the port's neighbor.
    Example: "192.168.1.1"

  - `items.status.switchPorts.macAddress` (string,null)
    MAC Address of the port's neighbor.
    Example: "00:00:5e:00:53:01"

  - `items.status.switchPorts.name` (string,null)
    Individual port name.
    Example: "1/1/1"

  - `items.status.switchPorts.portDescription` (string,null)
    Description to identify neighbor port.
    Example: "eth1"

  - `items.status.switchPorts.state` (string,null)
    State of the port.
    Example: "ok"

  - `items.status.switchPorts.systemName` (string,null)
    System name to identify neighbor node/jbof.
    Example: "system#01"

  - `items.status.temperatureState` (string,null)
    State of the internal temperature of the Switch.
    Example: "Normal"

  - `items.status.usage` (string,null)
    Usage of the Switch.
    Example: "internal"

  - `items.systemId` (string,null)
    Identifier of the Storage system to which the Switch belongs. Filter, Sort
    Example: "1AB234CDEF"

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

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


