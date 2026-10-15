---
title: "GET /backup-recovery/v1beta1/storeonces"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/storeonce/storeonceslist.md"
scraped_at: "2026-06-07T06:14:00.944759+00:00Z"
---

# Get the list of available StoreOnces.

Get the list of all available and registered StoreOnce machines.

Endpoint: GET /backup-recovery/v1beta1/storeonces
Version: 1.1.0
Security: bearer

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)

  - `items.updatedAt` (string, required)

  - `items.resourceUri` (string, required)
    The self reference for this resource.

  - `items.customerId` (string, required)
    The customer application identifier

  - `items.name` (string)
    A system specified name for the resource.

  - `items.dataOrchestrators` (array)

  - `items.dataOrchestrators.id` (string)
    ID of the Data Orchestrator

  - `items.dataOrchestrators.name` (string)
    Name of the Data Orchestrator

  - `items.dataOrchestrators.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.dataOrchestrators.serialNumber` (string)
    Serial number of the Data Orchestrator

  - `items.dataOrchestrators.type` (string)
    Type of the resource

  - `items.dateTime` (object)
    Datetime of StoreOnce.

  - `items.dateTime.methodDateTimeSet` (string)
    Allowed:Ntp, Manual. Method for how data and time is set on the appliance.
    Enum: "NTP", "MANUAL"

  - `items.dateTime.timezone` (string)
    timezone set on the appliance.

  - `items.dateTime.utcDateTime` (string)
    UTC date and time set on the appliance.

  - `items.description` (string)
    More detailed description of the appliance

  - `items.fibreChannel` (object)
    Fibre Channel of StoreOnce

  - `items.fibreChannel.initiators` (array)

  - `items.fibreChannel.initiators.fcid` (string)
    This is the FC identifier as identified by the FC initiator.

  - `items.fibreChannel.initiators.id` (string)
    This is the identifier of the FC initiator as defined by the physical StoreOnce.

  - `items.fibreChannel.initiators.online` (string)
    Indicates if online.

  - `items.fibreChannel.initiators.wwnn` (string)
    WW Node Name

  - `items.fibreChannel.initiators.wwpn` (string)
    WW Port Name

  - `items.health` (object)
    Health of StoreOnce.

  - `items.health.state` (string)
    current state of the StoreOnce
    Enum: "SO_HEALTH_STATE_UNKNOWN", "SO_HEALTH_STATE_OK", "SO_HEALTH_STATE_WARNING", "SO_HEALTH_STATE_CRITICAL", "SO_HEALTH_STATE_REGISTERING", "SO_HEALTH_STATE_ERROR", "SO_HEALTH_STATE_DELETING"

  - `items.health.stateReason` (any)
    Reason for states other than SO_HEALTH_STATE_OK.

  - `items.health.status` (string)
    current connection status of the StoreOnce
    Enum: "SO_HEALTH_STATUS_CONNECTED", "SO_HEALTH_STATUS_DISCONNECTED"

  - `items.health.updatedAt` (string)
    last updated timestamp

  - `items.iscsiInitiatorName` (string)
    The IQN of the iSCSI initiator

  - `items.network` (object)
    Network of StoreOnce.

  - `items.network.dns` (array)

  - `items.network.dns.networkAddress` (string)
    DNS server configured on the appliance.

  - `items.network.hostname` (string)
    IP address or FQDN of the appliance

  - `items.network.nics` (array)

  - `items.network.nics.gateway` (string)
    Gateway associated with the network interface.

  - `items.network.nics.id` (string)
    id of the nic

  - `items.network.nics.networkAddress` (string)
    IP address associated with the network interface.

  - `items.network.nics.networkIndex` (integer)
    Index associated with the network interface for the catalyst gateway.

  - `items.network.nics.networkName` (string)
    Name of the hypervisor network.

  - `items.network.nics.networkType` (string)
    Type of the network
    Enum: "DHCP", "STATIC"

  - `items.network.ntp` (array)

  - `items.network.ntp.networkAddress` (string)
    An IP address or FQDN of the NTP server.

  - `items.serialNumber` (string)
    The serial number of this StoreOnce

  - `items.softwareVersion` (string)
    softwareVersion of StoreOnce

  - `items.storage` (object)
    Storage of StoreOnce.

  - `items.storage.capacityLicensedBytes` (integer)
    Amount of licensed storage capacity.

  - `items.storage.capacityUnlicensedBytes` (integer)
    Amount of configured capacity which has not yet been licensed.

  - `items.storage.configuredStorageBytes` (integer)
    Physical storage which has been added to the StoreOnce and configured.

  - `items.storage.freeBytes` (integer)
    Free bytes left in storage

  - `items.storage.state` (string)
    Current state of the storage.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storage.unconfiguredStorageBytes` (integer)
    Physical storage which has been added to the StoreOnce but not configured.

  - `items.storage.usedBytes` (integer)
    Bytes being used in storage

  - `total` (integer, required)
    Total number of StoreOnces
    Example: 1

  - `count` (integer, required)
    Number of items in the response
    Example: 1

  - `offset` (integer, required)
    Offset of the current result set
    Example: 1

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


