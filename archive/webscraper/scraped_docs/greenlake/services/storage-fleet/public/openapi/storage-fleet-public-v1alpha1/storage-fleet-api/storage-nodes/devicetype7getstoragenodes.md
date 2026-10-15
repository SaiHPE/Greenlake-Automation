---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-nodes/devicetype7getstoragenodes.md"
scraped_at: "2026-06-07T06:16:12.963777+00:00Z"
---

# Get all storage nodes of a HPE Alletra Storage MP X10000 system

Get all storage nodes of a HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes
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

  - `filter` (string)
    Lucene query to filter StorageNodes by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004007"

  - `sort` (string)
    Data query to sort StorageNodes resource by Key.
    Example: "name desc"

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
    Identifier for the Storage Node. Filter, Sort
    Example: "default.node-1"

  - `items.type` (string, required)
    The type of the resource.
    Example: "string"

  - `items.assemblySerialNumber` (string,null)
    Assembly SerialNumber of Storage Node.
    Example: "NSIRNP6ZAP90LO"

  - `items.customerId` (string,null)
    CustomerId. Filter
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.enclosureSerialNumber` (string,null)
    Enclosure serial number. Filter
    Example: "USM2437VYZ"

  - `items.generation` (integer,null)
    generation. Filter, Sort
    Example: 1690454688

  - `items.serialNumber` (string,null)
    SerialNumber of Storage Node. Filter, Sort
    Example: "StorageNode9801"

  - `items.systemId` (string,null)
    System Id of the Storage Node. Filter, Sort
    Example: "4UN042PTDW"

  - `items.apiVersion` (string,null)
    apiVersion
    Example: "sc.hpe.com/v1"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.backendPorts` (array,null)

  - `items.backendPorts.deviceName` (string,null)
    Device Name
    Example: "Online"

  - `items.backendPorts.nicSlot` (integer,null)
    Nic Slot.
    Example: 4

  - `items.backendPorts.portNumber` (integer,null)
    Nic Slot.
    Example: 4465

  - `items.clusterId` (string,null)
    Id of the Storage system
    Example: "4ab3ad16-770e-4db8-b6a3-5ae267420f86"

  - `items.clusterRef` (string,null)
    Reference of the Storage system
    Example: "/api/sc.hpe.com/v1/default/storage/system-1"

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

  - `items.coreDnsName` (string,null)
    Core DNS Name
    Example: "node-NDBAEL2BHT17DI.node.local"

  - `items.enclosureId` (string,null)
    enclosur Id of the node
    Example: "59409cc2-77d4-4a32-b979-59a9fa339fc1"

  - `items.enclosureRef` (string,null)
    enclosureRef
    Example: "/api/sc.hpe.com/v1/default/enclosure-1/Enclosure"

  - `items.frontendPorts` (array,null)

  - `items.kind` (string,null)
    kind of object
    Example: "FleetOsNode"

  - `items.location` (string,null)
    location of the resource in enclosure.
    Example: "0"

  - `items.partNumber` (string,null)
    partNumber
    Example: "HFSCURHF897"

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.status` (object,null)

  - `items.status.auditPolicy` (object,null)
    Audit Policy.

  - `items.status.auditPolicy.fwdThreshold` (integer,null)
    Message level at or above at which audit events are forwarded.
    Example: 4

  - `items.status.auditPolicy.servers` (array,null)

  - `items.status.auditPolicy.servers.port` (integer,null)
    Remote syslog server port
    Example: 1514

  - `items.status.auditPolicy.servers.protocol` (string,null)
    Transport protocol to use. Supported value is only {"TCP"}.
    Example: "TLS"

  - `items.status.auditPolicy.servers.target` (string,null)
    Remote syslog server address. Value of target could be Name or IP address
    Example: "10.1.1.0"

  - `items.status.backendNics` (array,null)

  - `items.status.backendNics.operationalState` (string,null)
    Operational State of the NIC details.
    Example: "Online"

  - `items.status.backendNics.portStatuses` (array,null)
    The status of the ports in this NIC.

  - `items.status.backendNics.portStatuses.assignmentMode` (string,null)
    Assignment mode
    Example: "Static"

  - `items.status.backendNics.portStatuses.gateway` (string,null)
    Gateway
    Example: "192.168.0.254"

  - `items.status.backendNics.portStatuses.ipAddress` (string,null)
    IP address
    Example: "192.168.0.254"

  - `items.status.backendNics.portStatuses.macAddress` (string,null)
    MAC address
    Example: "32:d1:c5:62:5d:d8"

  - `items.status.backendNics.portStatuses.maxSpeed` (string,null)
    Max speed
    Example: "mock"

  - `items.status.backendNics.portStatuses.mtu` (integer,null)
    MTU size
    Example: 1600

  - `items.status.backendNics.portStatuses.name` (string,null)
    Name
    Example: "mockName"

  - `items.status.backendNics.portStatuses.operationalState` (string,null)
    Operational state
    Example: "Offline"

  - `items.status.backendNics.portStatuses.speed` (string,null)
    Speed
    Example: "mock"

  - `items.status.backendNics.portStatuses.subnet` (string,null)
    Subnet
    Example: "255.255.255.0"

  - `items.status.backendNics.s3RdmaCapable` (boolean,null)
    Indicates NIC capability to support S3 RDMA.
    Example: true

  - `items.status.backendNics.slotNumber` (integer,null)
    Slot Number
    Example: 1

  - `items.status.conditions` (array,null)
    conditions

  - `items.status.conditions.lastTransitionTime` (string,null)
    lastTransitionTime.
    Example: "2023-07-26T21:15:27Z"

  - `items.status.conditions.message` (string,null)
    message.
    Example: "Pending update, DNS updated successfully, Proxy updated successfully, AuditPolicy updated successfully, AutoSupport updated successfully, Node Reconciled successfully"

  - `items.status.conditions.observedGeneration` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 3

  - `items.status.conditions.reason` (string,null)
    reason
    Example: "SuccessfulUpdate"

  - `items.status.conditions.status` (string,null)
    status.
    Example: "True"

  - `items.status.conditions.type` (string)
    type.
    Example: "Ready"

  - `items.status.dnsServers` (array,null)
    List of dns server

  - `items.status.faultLedState` (string,null)
    The current state of the FaultLED.
    Example: "15.213.204.163"

  - `items.status.frontendNics` (array,null)

  - `items.status.healthLedState` (string,null)
    The current state of the HealthLED.
    Example: "Off"

  - `items.status.hostname` (string,null)
    hostname
    Example: "c0n2"

  - `items.status.jbofConnectivityStatuses` (array,null)

  - `items.status.jbofConnectivityStatuses.jbofRef` (string,null)
    Jbof reference.
    Example: "/cm/jbof-0"

  - `items.status.jbofConnectivityStatuses.overallStatus` (string,null)
    overall Status.
    Example: "connected"

  - `items.status.jbofConnectivityStatuses.pathConnectionStatuses` (array,null)

  - `items.status.jbofConnectivityStatuses.pathConnectionStatuses.connectionStatus` (string,null)
    Connection Status.
    Example: "Connected"

  - `items.status.jbofConnectivityStatuses.pathConnectionStatuses.targetAddress` (string,null)
    Target Ip Address
    Example: "Online"

  - `items.status.lastModifiedTime` (string,null)
    UTC Time at which the status for this object was last updated.
    Example: "2023-07-26T21:15:27Z"

  - `items.status.managementInterface` (object,null)
    The configuration for the  network interface

  - `items.status.operationalState` (string,null)
    Operational state of the Node
    Example: "Online"

  - `items.status.osVersion` (string,null)
    The target Hex OS software version for the node
    Example: "0.0.4870.0-1037280"

  - `items.status.outboundProxy` (object,null)

  - `items.status.outboundProxy.port` (integer,null)
    The TCP port number to which proxy requests should be sent.
    Example: 3200

  - `items.status.outboundProxy.server` (string,null)
    The IPv4 Address or fully qualified domain name of the Outbound Proxy Server.
    Example: "192.34.12.3"

  - `items.status.ready` (boolean,null)
    Used to determine when a controller has brought its resource into compliance with the specification. When a resource is created, by default, its status.ready attribute should be initiatlized to False, then changed to True when the current status of the resource matches its specification.
    Example: true

  - `items.status.strongPasswordMode` (object,null)
    Strong Password mode details

  - `items.status.strongPasswordMode.expiryTime` (string,null)
    Expiry time of the password
    Example: "T23:55:00+00:00"

  - `items.status.strongPasswordMode.mode` (string,null)
    Mode of the password
    Example: "Ciphertext"

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


