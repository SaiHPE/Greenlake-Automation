---
title: "GET /backup-recovery/v1beta1/protection-store-gateways"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewayslist.md"
scraped_at: "2026-06-07T06:14:11.194230+00:00Z"
---

# Get a list of the Protection Store Gateways that are registered with DSCC

Gets the list of available Protection Store Gateways

Endpoint: GET /backup-recovery/v1beta1/protection-store-gateways
Version: 1.1.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set

  - `limit` (integer)
    The numbers of items to return

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.

The returned set of resources will match the criteria in the filter query parameter.

A comparison compares a property name to a literal. The comparisons supported are the following:

- “eq” : Is a property equal to value. Valid for number, boolean and string properties
- “gt” : Is a property greater than a value. Valid for number or string timestamp properties
- “lt” : Is a property less than a value. Valid for number or string timestamp properties
- “in” : Is a value in a property (that is an array of strings)

Filters are supported on following attributes:        
- state
- health/state
- health/status

Examples:

- GET ./protection-store-gateways?filter=state eq'PSG_STATE_REGISTERING'
- GET ./protection-store-gateways?filter=health/state eq 'PSG_HEALTH_STATE_UNKNOWN'
- GET ./protection-store-gateways?filter=health/status eq 'PSG_HEALTH_STATUS_CONNECTED'

  - `sort` (string)
    Comma separated list of properties defining the sort order

  - `select` (string)
    The select query parameter is used to limit the properties returned in the GET response.

Multiple properties can be specified to be returned. The server will only return the set of properties requested by the client.

Example:

GET ./protection-store-gateways?select=displayName,state'

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

  - `items.adminUserCiphertext` (string)

  - `items.consoleUri` (string)
    URI for the console screen that displays this resource

  - `items.dataOrchestratorId` (string)
    The id of the Data Orchestrator this Protection Store Gateway is associated with

  - `items.datastoresInfo` (array)

  - `items.datastoresInfo.id` (string)
    UUID string uniquely identifying the datastore.

  - `items.datastoresInfo.resourceUri` (string)
    Reference to resource.

  - `items.datastoresInfo.totalProvisionedDiskInTiB` (number)
    The total size of the PSG provisioned disk(s) on the datastore.

  - `items.displayName` (string)
    The display name of this Protection Store Gateway

  - `items.health` (object)
    Health of Protection Store Gateway.

  - `items.health.state` (string)
    Current state of the Protection Store Gateway
    Enum: "PSG_HEALTH_STATE_UNKNOWN", "PSG_HEALTH_STATE_OK", "PSG_HEALTH_STATE_OFF", "PSG_HEALTH_STATE_WARNING", "PSG_HEALTH_STATE_CRITICAL", "PSG_HEALTH_STATE_DEPLOYING", "PSG_HEALTH_STATE_REGISTERING", "PSG_HEALTH_STATE_INITIALIZING", "PSG_HEALTH_STATE_UPGRADING", "PSG_HEALTH_STATE_UPDATING", "PSG_HEALTH_STATE_ERROR", "PSG_HEALTH_STATE_DELETING"

  - `items.health.stateReason` (string)
    Reason why the Protection Store Gateway is in the current state.  This will not be populated if the state is HEALTH_STATE_OK

  - `items.health.status` (string)
    Current connection status of the Protection Store Gateway
    Enum: "PSG_HEALTH_STATUS_CONNECTED", "PSG_HEALTH_STATUS_DISCONNECTED"

  - `items.health.updatedAt` (string)
    last updated timestamp

  - `items.network` (object)
    Network of Protection Store Gateway.

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
    Index associated with the network interface for the Protection Store Gateway.

  - `items.network.nics.networkName` (string)
    Name of the hypervisor network.

  - `items.network.nics.networkType` (string)
    Type of the network
    Enum: "DHCP", "STATIC"

  - `items.network.nics.subnetMask` (string)
    Subnet mask.

  - `items.network.ntp` (array)

  - `items.network.ntp.networkAddress` (string)
    An IP address or FQDN of the NTP server.

  - `items.network.proxy` (object)

  - `items.network.proxy.credentials` (object)

  - `items.network.proxy.credentials.password` (string)
    Password of proxy server

  - `items.network.proxy.credentials.username` (string)
    Username of proxy server

  - `items.network.proxy.networkAddress` (string)
    An IP address or FQDN to address the proxy server

  - `items.network.proxy.port` (integer)
    Port number of the proxy server

  - `items.override` (object)
    User supplied parameters used to override automatic VM resource configuration with a fixed configuration.
If 0 is returned for the values then no override has been configured.

  - `items.override.cpu` (number)
    Number of vCPU cores.
    Example: 8

  - `items.override.ramInGiB` (number)
    Amount of RAM in GiB.
    Example: 24

  - `items.override.storageInTiB` (number)
    Total storage capacity (TiB) of the Protection Store Gateway.
    Example: 2

  - `items.remoteAccessEnabled` (boolean)

  - `items.remoteAccessStationId` (string)
    The station ID (SID) that is required for remote desktop access

  - `items.serialNumber` (string)
    The serial number of this Protection Store Gateway

  - `items.size` (object)
    User supplied parameters used to size the Protection Store Gateway.

  - `items.size.maxInCloudDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the Cloud Protection Stores.
    Example: 2

  - `items.size.maxInCloudRetentionDays` (number)
    The maximum retention period for cloud backups in days.
    Example: 2

  - `items.size.maxOnPremDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the On-Prem Protection Store.
    Example: 2

  - `items.size.maxOnPremRetentionDays` (number)
    The maximum retention period for local backups in days.
    Example: 2

  - `items.softwareVersion` (string)
    Software version of the Protection Store Gateway

  - `items.state` (string)
    State of Protection Store Gateway.
    Enum: "PSG_STATE_QUERYING_CATALOGUE", "PSG_STATE_DEPLOYING", "PSG_STATE_DEPLOYED", "PSG_STATE_DEPLOYED_ERROR", "PSG_STATE_REGISTERING", "PSG_STATE_REGISTERED", "PSG_STATE_REGISTERED_ERROR", "PSG_STATE_OK", "PSG_STATE_DELETING", "PSG_STATE_ERROR", "PSG_STATE_POWERING_ON", "PSG_STATE_DELETING_STORES", "PSG_STATE_DELETING_UNREGISTERING", "PSG_STATE_DELETING_VM_SHUTTING_DOWN", "PSG_STATE_DELETING_VM_DELETING", "PSG_STATE_DEPLOYING_STORAGE", "PSG_STATE_UPDATING_STORAGE_MOD", "PSG_STATE_UPDATING_STORAGE_DEL", "PSG_STATE_UPDATING_STORAGE_ADD", "PSG_STATE_UPDATING", "PSG_STATE_VM_POWERING_ON", "PSG_STATE_VM_SHUTTING_DOWN", "PSG_STATE_VM_RESTARTING", "PSG_STATE_OK_OFF", "PSG_STATE_UNKNOWN", "PSG_STATE_VM_CREATING_NIC", "PSG_STATE_VM_UPDATING_RESOURCES", "PSG_STATE_CONFIGURING_RESOURCES", "PSG_STATE_REBOOTING_AFTER_RESTORE", "PSG_STATE_REBOOTED_AFTER_RESTORE"

  - `items.supportUserCiphertext` (string)

  - `items.vmId` (string)
    Id of the VM

  - `count` (integer, required)
    Number of items in the response (for paginated responses)

  - `limit` (integer)
    The limit specified in the query parameter.
    Example: 1

  - `offset` (integer)
    The offset specified in the query parameter.

  - `total` (integer)
    The total count of objects in the result set.

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


