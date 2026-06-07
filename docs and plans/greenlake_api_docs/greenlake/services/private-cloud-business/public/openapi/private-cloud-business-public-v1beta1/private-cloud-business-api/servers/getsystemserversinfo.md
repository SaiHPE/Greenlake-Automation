---
title: "GET /private-cloud-business/v1beta1/systems/{id}/servers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/servers/getsystemserversinfo.md"
scraped_at: "2026-06-07T06:15:37.769987+00:00Z"
---

# Get information about the specified system's servers.

Get server information by system id 

Returns details about the servers for the specified system id. Retrieving all of the properties for all servers 
in a system can take a long time because the amount of data is large. Use the  'select' query parameter to choose 
only the properties you want to retrieve.

For example, to get the server id, name, serial number and hypervisor host, use ?select=id,name,serialNumber,hypervisorHost

Endpoint: GET /private-cloud-business/v1beta1/systems/{id}/servers
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    Unique Identifier of the system, usually a UUID.

## Query parameters:

  - `select` (string)
    Query parameter listing the properties of Server information to fetch.
    Example: "id,name,serialNumber,hypervisorHost"

  - `offset` (integer)
    Use offset in conjunction with limit for paging, e.g.: offset=30&&limit=10. Offset is the number of items from the beginning of the result set to the first item included in the response.
    Example: 30

  - `limit` (integer)
    Use limit in conjunction with offset for paging, e.g.: offset=30&&limit=10. Limit is the maximum number of items to include in the response.
    Example: 10

  - `filter` (string)
    The expression to filter responses.
    Example: "health/overallHealth eq OK"

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified the
default order is ascending.
    Example: "id desc,name asc"

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

  - `items.health` (object)
    Server Health information

  - `items.health.agentlessManagementService` (string)

  - `items.health.biosOrHardwareHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.fanHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.fanRedundancy` (string)
    Resource Component Redundancy Status. Indicated as ENUM with following mapping
    Enum: "REDUNDANT", "NONREDUNDANT", "FAILEDREDUNDANT", "ABSENT", "DISABLED", "OFFLINE", "UNAVAILABLEOFFLINE", "STANDBYOFFLINE", "UNKNOWN"

  - `items.health.hbLastUpdateTimestamp` (string)

  - `items.health.memoryHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.networkHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.overallServerHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.powerState` (string)

  - `items.health.powerSuppliesHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.powerSuppliesRedundancy` (string)
    Resource Component Redundancy Status. Indicated as ENUM with following mapping
    Enum: "REDUNDANT", "NONREDUNDANT", "FAILEDREDUNDANT", "ABSENT", "DISABLED", "OFFLINE", "UNAVAILABLEOFFLINE", "STANDBYOFFLINE", "UNKNOWN"

  - `items.health.processorHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.smartStorageBatteryHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.storageHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.health.temperaturesHealth` (string)
    Resource Component Health Status. Indicated as ENUM with following mapping
    Enum: "OK", "WARNING", "CRITICAL", "MISSING", "UNKNOWN"

  - `items.hypervisorHost` (object)
    id, URI to reference the hypervisor host.

  - `items.hypervisorHost.hypervisorClusterId` (string)

  - `items.hypervisorHost.hypervisorClusterName` (string)

  - `items.hypervisorHost.hypervisorHostIp` (string)

  - `items.hypervisorHost.id` (string)
    Hypervisor Host details of the Server.

  - `items.hypervisorHost.name` (string)
    Hypervisor Host Name of the Server.
    Example: "hypervisor-host-name"

  - `items.hypervisorHost.resourceUri` (string)

  - `items.hypervisorHost.type` (string)
    Example: "hypervisor-host"

  - `items.iloFirmwareVersion` (string)
    firmware version of iLO in the server.
    Example: "iLO 5 v2.14"

  - `items.iloNetworkInfo` (object)
    ILO Network Information.

  - `items.iloNetworkInfo.gateway` (string)

  - `items.iloNetworkInfo.iloHostname` (string)
    iLO Hostname

  - `items.iloNetworkInfo.iloIp` (string)
    iLO Management IP address

  - `items.iloNetworkInfo.network` (string)

  - `items.iloNetworkInfo.subnetMask` (string)

  - `items.iloState` (string)
    state of the iLO in the server.
    Example: "ENABLED"

  - `items.iloStatus` (string)
    status of the iLO in the server.
    Example: "ON"

  - `items.indicatorLedStatus` (string)
    iLO LED indication.
    Example: "OFF"

  - `items.maintenanceMode` (boolean)
    Is the server in maintenance mode?

  - `items.memoryGib` (string)
    Memory of the server.

  - `items.model` (string)
    The model of the server.
    Example: "ProLiant DL325 Gen10"

  - `items.ncmVersion` (string)
    Version of NCM installed on the server.
    Example: "7.0.2-650014"

  - `items.powerState` (string)
    Server Power state.
    Enum: "ON", "RESET", "UNKNOWN"

  - `items.processorCount` (string)
    Number of processors in the server.

  - `items.processorModel` (string)
    Model of the processors in the server.
    Example: "Intel(R) Xeon(R) Gold 6130 CPU @ 2.10GHz"

  - `items.serialNumber` (string)
    Server's serial number.
    Example: "MXQ02203VM"

  - `items.systemId` (string)
    Unique Identifier of the system, usually a UUID.

  - `items.name` (string)
    A system specified name for the resource.

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


