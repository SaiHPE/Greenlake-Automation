---
title: "GET /backup-recovery/v1beta1/storeonces/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/storeonce/storeoncegetbyid.md"
scraped_at: "2026-06-07T06:14:12.813552+00:00Z"
---

# Get details of a StoreOnce.

Get all the details and information of registered StoreOnce.

Endpoint: GET /backup-recovery/v1beta1/storeonces/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the object
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

## Response 200 fields (application/json):

  - `id` (string, required)
    An identifier for the resource, usually a UUID.

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)

  - `updatedAt` (string, required)

  - `resourceUri` (string, required)
    The self reference for this resource.

  - `customerId` (string, required)
    The customer application identifier

  - `name` (string)
    A system specified name for the resource.

  - `dataOrchestrators` (array)

  - `dataOrchestrators.id` (string)
    ID of the Data Orchestrator

  - `dataOrchestrators.name` (string)
    Name of the Data Orchestrator

  - `dataOrchestrators.resourceUri` (string)
    The 'self' reference for this resource.

  - `dataOrchestrators.serialNumber` (string)
    Serial number of the Data Orchestrator

  - `dataOrchestrators.type` (string)
    Type of the resource

  - `dateTime` (object)
    Datetime of StoreOnce.

  - `dateTime.methodDateTimeSet` (string)
    Allowed:Ntp, Manual. Method for how data and time is set on the appliance.
    Enum: "NTP", "MANUAL"

  - `dateTime.timezone` (string)
    timezone set on the appliance.

  - `dateTime.utcDateTime` (string)
    UTC date and time set on the appliance.

  - `description` (string)
    More detailed description of the appliance

  - `fibreChannel` (object)
    Fibre Channel of StoreOnce

  - `fibreChannel.initiators` (array)

  - `fibreChannel.initiators.fcid` (string)
    This is the FC identifier as identified by the FC initiator.

  - `fibreChannel.initiators.id` (string)
    This is the identifier of the FC initiator as defined by the physical StoreOnce.

  - `fibreChannel.initiators.online` (string)
    Indicates if online.

  - `fibreChannel.initiators.wwnn` (string)
    WW Node Name

  - `fibreChannel.initiators.wwpn` (string)
    WW Port Name

  - `health` (object)
    Health of StoreOnce.

  - `health.state` (string)
    current state of the StoreOnce
    Enum: "SO_HEALTH_STATE_UNKNOWN", "SO_HEALTH_STATE_OK", "SO_HEALTH_STATE_WARNING", "SO_HEALTH_STATE_CRITICAL", "SO_HEALTH_STATE_REGISTERING", "SO_HEALTH_STATE_ERROR", "SO_HEALTH_STATE_DELETING"

  - `health.stateReason` (any)
    Reason for states other than SO_HEALTH_STATE_OK.

  - `health.status` (string)
    current connection status of the StoreOnce
    Enum: "SO_HEALTH_STATUS_CONNECTED", "SO_HEALTH_STATUS_DISCONNECTED"

  - `health.updatedAt` (string)
    last updated timestamp

  - `iscsiInitiatorName` (string)
    The IQN of the iSCSI initiator

  - `network` (object)
    Network of StoreOnce.

  - `network.dns` (array)

  - `network.dns.networkAddress` (string)
    DNS server configured on the appliance.

  - `network.hostname` (string)
    IP address or FQDN of the appliance

  - `network.nics` (array)

  - `network.nics.gateway` (string)
    Gateway associated with the network interface.

  - `network.nics.id` (string)
    id of the nic

  - `network.nics.networkAddress` (string)
    IP address associated with the network interface.

  - `network.nics.networkIndex` (integer)
    Index associated with the network interface for the catalyst gateway.

  - `network.nics.networkName` (string)
    Name of the hypervisor network.

  - `network.nics.networkType` (string)
    Type of the network
    Enum: "DHCP", "STATIC"

  - `network.ntp` (array)

  - `network.ntp.networkAddress` (string)
    An IP address or FQDN of the NTP server.

  - `serialNumber` (string)
    The serial number of this StoreOnce

  - `softwareVersion` (string)
    softwareVersion of StoreOnce

  - `storage` (object)
    Storage of StoreOnce.

  - `storage.capacityLicensedBytes` (integer)
    Amount of licensed storage capacity.

  - `storage.capacityUnlicensedBytes` (integer)
    Amount of configured capacity which has not yet been licensed.

  - `storage.configuredStorageBytes` (integer)
    Physical storage which has been added to the StoreOnce and configured.

  - `storage.freeBytes` (integer)
    Free bytes left in storage

  - `storage.state` (string)
    Current state of the storage.
    Enum: "OK", "ERROR", "WARNING"

  - `storage.unconfiguredStorageBytes` (integer)
    Physical storage which has been added to the StoreOnce but not configured.

  - `storage.usedBytes` (integer)
    Bytes being used in storage

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

## Response 404 fields (application/json):

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


