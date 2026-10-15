---
title: "GET /backup-recovery/v1beta1/data-orchestrators"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorlist.md"
scraped_at: "2026-06-07T06:14:01.738400+00:00Z"
---

# Get a list of the Data Orchestrators that are registered with DSCC

This API returns a list of all the Data Orchestrators that are registered with the DSCC 
customer account.

Endpoint: GET /backup-recovery/v1beta1/data-orchestrators
Version: 1.1.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    When listing a large number of Data Orchestrators, the offset query parameter defines
the index of the first Data Orchestrator to include in the response.

Example:
* GET /backup-recovery/v1beta1/data-orchestrators?offset=10

  - `limit` (integer)
    The limit query parameter defines the maximum number of Data Orchestrators to included
in the response.

Example:
* GET /backup-recovery/v1beta1/data-orchestrators?limit=10

  - `sort` (string)
    The sort query is a comma separated list of properties defining the sort order.
The direction indicator may only be either “asc” (ascending) or “desc” (descending). 
If no direction indicator is specified, the default order is ascending.

Sorting is supported on the following properties:
* name
* generation
* connectionState
* serialNumber
* softwareVersion
* status
* state
* stateReason
* id
* platform
* vCpu
* totalMemoryInGiB
* poweredOnAt
* createdAt
* interfaces/network/defaultGateway
* dateTime/methodDateTimeSet
* dateTime/timezone
* ntp/status
* ntp/state
* ntp/stateReason

Example:
* GET /backup-recovery/v1beta1/data-orchestrators?sort=name,generation desc

  - `select` (string)
    The select query parameter is used to define a subset of properties to be included in the response.
Each property to be included should be passed in a comma-separated list.

Example:
* GET /backup-recovery/v1beta1/data-orchestrators?select=id,name,serialNumber

  - `filter` (string)
    The filter query parameter is used to filter the list of on-prem engines returned in the response.
The returned set of resources will match the criteria in the filter query parameter.

A comparision compares a property name to a literal. The comparisons supported are the following:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /backup-recovery/v1beta1/data-orchestrators?filter=connectionState eq 'CONNECTED'
* GET /backup-recovery/v1beta1/data-orchestrators?filter=connectionState eq 'CONNECTED' and status eq 'ERROR'

Filtering is supported with the following attributes:
* id
* name
* interfaces/network/hostname
* serialNumber
* status
* state
* connectionState 
* softwareVersion

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    UUID identifying a Data Orchestrator.

  - `items.type` (string, required)
    backup-recovery/data-orchestrator

  - `items.connectionState` (string)
    Connection state of Data Orchestrator to DSCC.
    Enum: "CONNECTED", "DISCONNECTED"

  - `items.consoleUri` (string)
    The 'self' reference for this resource in the console.

  - `items.customerId` (string)
    The customer application identifier

  - `items.displayName` (string)
    User-defined name given to Data Orchestrator.
    Example: "Data Orchestrator 1"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.name` (string)
    Name given to Data Orchestrator.
    Example: "Data Orchestrator 1"

  - `items.resourceUri` (string)
    The self reference for this resource.

  - `items.serialNumber` (string)
    Data Orchestrator serial number.

  - `items.softwareVersion` (string)
    Data Orchestrator software version.

  - `items.state` (string)
    Enum: "OK", "UPGRADING", "UPDATING", "RESTORING", "RECOVERING", "UNKNOWN", "DEGRADED"

  - `items.stateReason` (string)
    Reason for the Data Orchestrator being in the current state. This will be empty when the Data Orchestrator is in an OK state.

  - `items.status` (string)
    Enum: "OK", "WARNING", "ERROR"

  - `items.upTimeInSeconds` (integer)
    Returns the number of seconds since Data Orchestrator was powered on. Returns 0 if Data Orchestrator is DISCONNECTED from DSCC.

  - `items.createdAt` (string)
    UTC time when the Data Orchestrator was activated.
    Example: "2019-07-21T17:32:28Z"

  - `items.dateTime` (object)
    This details the current date and time of the Data Orchestrator, how the current date and time is determined, as well as the user specified timezone. The date and time will have either been explicitly set by the user, determined from a configured NTP server or synchronized with the Data Orchestrator VM host.

  - `items.dateTime.methodDateTimeSet` (string)
    Method for how data and time is set on the Data Orchestrator.
    Enum: "NTP", "VM_HOST"

  - `items.dateTime.timezone` (string)
    Time zone in which the Data Orchestrator is deployed.
    Example: "Europe/London, Australia/Sydney, Asia/Tokyo, America/NewYork"

  - `items.interfaces` (object)

  - `items.interfaces.network` (object)

  - `items.interfaces.network.defaultGateway` (string)
    IP address or FQDN of the default gateway.
    Example: "172.29.233.254"

  - `items.interfaces.network.hostname` (string)
    IP address or FQDN of the Data Orchestrator.
    Example: "atlas.hpe.com"

  - `items.interfaces.network.nameServers` (array)
    List of configured DNS servers configured on the Data Orchestrator.

  - `items.interfaces.network.nameServers.networkAddress` (string)
    IP address or FQDN of DNS server.
    Example: "172.29.232.103"

  - `items.interfaces.network.nic` (array)
    List of network interfaces configured on the Data Orchestrator. Note that this information will not include any loopback interfaces.

  - `items.interfaces.network.nic.addressType` (string)
    Indicates whether the address is assigned statically or via DHCP.
    Enum: "DHCP", "STATIC"

  - `items.interfaces.network.nic.enabled` (boolean)
    Indicates whether the interface is enabled or disabled.

  - `items.interfaces.network.nic.name` (string)
    Name of the network interface.
    Example: "ens160"

  - `items.interfaces.network.nic.networkAddress` (string)
    IP address associated with the network interface.
    Example: "172.29.232.100"

  - `items.interfaces.network.nic.state` (string)
    Indicates whether the interface is up or down.
    Enum: "UP", "DOWN"

  - `items.interfaces.network.nic.staticRoutes` (array)
    List of static routes.

  - `items.interfaces.network.nic.staticRoutes.gateway` (string)
    IP address or FQDN of gateway.
    Example: "172.29.233.254"

  - `items.interfaces.network.nic.staticRoutes.networkAddress` (string)
    IP address associated with the static route.
    Example: "172.29.232.105"

  - `items.interfaces.network.nic.staticRoutes.subnetMask` (string)
    Subnet mask associated with the static route.
    Example: "255.255.255.0"

  - `items.interfaces.network.nic.subnetMask` (string)
    Subnet mask.
    Example: "255.255.255.0"

  - `items.interfaces.network.proxy` (object)

  - `items.interfaces.network.proxy.credentials` (object)

  - `items.interfaces.network.proxy.credentials.username` (string)

  - `items.interfaces.network.proxy.networkAddress` (string)
    An IP address or FQDN to address the proxy server
    Example: "http://proxy.mydomain.com"

  - `items.interfaces.network.proxy.port` (integer)
    Port number of the proxy server

  - `items.interfaces.network.searchDomains` (array)
    List of search domains.
    Example: ["mydomain.com"]

  - `items.lastUpdateCheckTime` (string)
    UTC time when a software update check was last performed.
    Example: "2019-07-21T17:32:28Z"

  - `items.latestRecoveryPoint` (string)
    UTC time when Data Orchestrator catalogue was last protected.
    Example: "2019-07-21T17:32:28Z"

  - `items.ntp` (object)

  - `items.ntp.ntpServers` (array)
    NTP servers against which the Data Orchestrator should synchronize.

  - `items.ntp.ntpServers.networkAddress` (string)
    An IP address or FQDN of the NTP server.
    Example: "pool.ntp.org"

  - `items.ntp.stateReason` (string)
    Reason for the current state of the NTP configuration.

  - `items.platform` (string)
    Hypervisor platform.
    Enum: "VMWARE_ESXI"

  - `items.poweredOnAt` (string)
    UTC time when Data Orchestrator was last powered on.
    Example: "2019-07-21T17:32:28Z"

  - `items.totalMemoryInGiB` (integer)
    Total RAM configured for the Data Orchestrator in GiB.

  - `items.updatedAt` (string)
    UTC time when the Data Orchestrator was last updated.
    Example: "2019-07-21T17:32:28Z"

  - `items.vCpu` (integer)
    Number of virtual CPUs configured for the Data Orchestrator.

  - `items.adminUserCiphertext` (string)
    Ciphertext to allow HPE Support to authenticate with the Data Orchestrator with unrestricted admin privileges.

  - `items.infosightEnabled` (boolean)
    The Data Orchestrator is sending telemetry to InfoSight.

  - `items.remoteAccessEnabled` (boolean)
    HPE Support can remotely access the Data Orchestrator for the purposes of debug. For HPE Support to authenticate, the ciphertext must be shared by the user.

  - `items.remoteAccessStationId` (string)
    An identifier that HPE Support can use to remotely access the Data Orchestrator.

  - `items.supportUserCiphertext` (string)
    Ciphertext to allow HPE Support to authenticate with the Data Orchestrator with restricted support privileges.

  - `count` (integer, required)
    Number of items in the response (for paginated responses)

  - `offset` (integer)
    The offset query parameter specified in the request.

  - `total` (integer)
    Total items returned.

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


