---
title: "GET /private-cloud-business/v1beta1/systems/{systemId}/servers/{serverId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/servers/getsystemserverinfo.md"
scraped_at: "2026-06-07T06:15:37.832121+00:00Z"
---

# Get information about a system's specific server.

Get server details by system id and server id 

Returns information about a specific server on a specific system. Retrieving all of the properties for a server 
can take a long time because the amount of data is large. Use the select query parameter to choose only the 
properties you want to retrieve. 

For example, to get details of the server's id, name, serial number and hypervisor host, use ?select=id,name,serialNumber,hypervisorHost

Endpoint: GET /private-cloud-business/v1beta1/systems/{systemId}/servers/{serverId}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    Unique Identifier of the system, usually a UUID.

  - `serverId` (string, required)
    Unique Identifier of the Server, usually a UUID.

## Query parameters:

  - `select` (string)
    Query parameter listing the properties of Server information to fetch.
    Example: "id,name,serialNumber,hypervisorHost"

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

  - `health` (object)
    Server Health information

  - `health.agentlessManagementService` (string)

  - `health.biosOrHardwareHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.fanHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.fanRedundancy` (string)
    Resource Component Redundancy Status. Indicated as ENUM with following mapping
    Enum: "REDUNDANT", "NONREDUNDANT", "FAILEDREDUNDANT", "ABSENT", "DISABLED", "OFFLINE", "UNAVAILABLEOFFLINE", "STANDBYOFFLINE", "UNKNOWN"

  - `health.hbLastUpdateTimestamp` (string)

  - `health.memoryHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.networkHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.overallServerHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.powerState` (string)

  - `health.powerSuppliesHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.powerSuppliesRedundancy` (string)
    Resource Component Redundancy Status. Indicated as ENUM with following mapping
    Enum: "REDUNDANT", "NONREDUNDANT", "FAILEDREDUNDANT", "ABSENT", "DISABLED", "OFFLINE", "UNAVAILABLEOFFLINE", "STANDBYOFFLINE", "UNKNOWN"

  - `health.processorHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.smartStorageBatteryHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.storageHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `health.temperaturesHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `hypervisorHost` (object)
    id, URI to reference the hypervisor host.

  - `hypervisorHost.hypervisorClusterId` (string)

  - `hypervisorHost.hypervisorClusterName` (string)

  - `hypervisorHost.hypervisorHostIp` (string)

  - `hypervisorHost.id` (string)
    Hypervisor Host details of the Server.

  - `hypervisorHost.name` (string)
    Hypervisor Host Name of the Server.
    Example: "hypervisor-host-name"

  - `hypervisorHost.resourceUri` (string)

  - `hypervisorHost.type` (string)
    Example: "hypervisor-host"

  - `iloFirmwareVersion` (string)
    firmware version of iLO in the server.
    Example: "iLO 5 v2.14"

  - `iloNetworkInfo` (object)
    ILO Network Information.

  - `iloNetworkInfo.gateway` (string)

  - `iloNetworkInfo.iloHostname` (string)
    iLO Hostname

  - `iloNetworkInfo.iloIp` (string)
    iLO Management IP address

  - `iloNetworkInfo.network` (string)

  - `iloNetworkInfo.subnetMask` (string)

  - `iloState` (string)
    state of the iLO in the server.
    Example: "ENABLED"

  - `iloStatus` (string)
    status of the iLO in the server.
    Example: "ON"

  - `indicatorLedStatus` (string)
    iLO LED indication.
    Example: "OFF"

  - `maintenanceMode` (boolean)
    Is the server in maintenance mode?

  - `memoryGib` (string)
    Memory of the server.

  - `model` (string)
    The model of the server.
    Example: "ProLiant DL325 Gen10"

  - `ncmVersion` (string)
    Version of NCM installed on the server.
    Example: "7.0.2-650014"

  - `powerState` (string)
    Server Power state.
    Enum: "ON", "RESET", "UNKNOWN"

  - `processorCount` (string)
    Number of processors in the server.

  - `processorModel` (string)
    Model of the processors in the server.
    Example: "Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz"

  - `serialNumber` (string)
    Server's serial number.
    Example: "MXQ02203VM"

  - `systemId` (string)
    Unique Identifier of the system, usually a UUID.

  - `name` (string)
    A system specified name for the resource.

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


