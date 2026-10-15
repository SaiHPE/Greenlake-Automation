---
title: "GET /backup-recovery/v1beta1/protection-store-gateways/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaygetbyid.md"
scraped_at: "2026-06-07T06:14:11.202300+00:00Z"
---

# Get details of a Protection Store Gateway within DSCC

Get details of a Protection Store Gateway

Endpoint: GET /backup-recovery/v1beta1/protection-store-gateways/{id}
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

  - `adminUserCiphertext` (string)

  - `consoleUri` (string)
    URI for the console screen that displays this resource

  - `dataOrchestratorId` (string)
    The id of the Data Orchestrator this Protection Store Gateway is associated with

  - `datastoresInfo` (array)

  - `datastoresInfo.id` (string)
    UUID string uniquely identifying the datastore.

  - `datastoresInfo.resourceUri` (string)
    Reference to resource.

  - `datastoresInfo.totalProvisionedDiskInTiB` (number)
    The total size of the PSG provisioned disk(s) on the datastore.

  - `displayName` (string)
    The display name of this Protection Store Gateway

  - `health` (object)
    Health of Protection Store Gateway.

  - `health.state` (string)
    Current state of the Protection Store Gateway
    Enum: "PSG_HEALTH_STATE_UNKNOWN", "PSG_HEALTH_STATE_OK", "PSG_HEALTH_STATE_OFF", "PSG_HEALTH_STATE_WARNING", "PSG_HEALTH_STATE_CRITICAL", "PSG_HEALTH_STATE_DEPLOYING", "PSG_HEALTH_STATE_REGISTERING", "PSG_HEALTH_STATE_INITIALIZING", "PSG_HEALTH_STATE_UPGRADING", "PSG_HEALTH_STATE_UPDATING", "PSG_HEALTH_STATE_ERROR", "PSG_HEALTH_STATE_DELETING"

  - `health.stateReason` (string)
    Reason why the Protection Store Gateway is in the current state.  This will not be populated if the state is HEALTH_STATE_OK

  - `health.status` (string)
    Current connection status of the Protection Store Gateway
    Enum: "PSG_HEALTH_STATUS_CONNECTED", "PSG_HEALTH_STATUS_DISCONNECTED"

  - `health.updatedAt` (string)
    last updated timestamp

  - `network` (object)
    Network of Protection Store Gateway.

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
    Index associated with the network interface for the Protection Store Gateway.

  - `network.nics.networkName` (string)
    Name of the hypervisor network.

  - `network.nics.networkType` (string)
    Type of the network
    Enum: "DHCP", "STATIC"

  - `network.nics.subnetMask` (string)
    Subnet mask.

  - `network.ntp` (array)

  - `network.ntp.networkAddress` (string)
    An IP address or FQDN of the NTP server.

  - `network.proxy` (object)

  - `network.proxy.credentials` (object)

  - `network.proxy.credentials.password` (string)
    Password of proxy server

  - `network.proxy.credentials.username` (string)
    Username of proxy server

  - `network.proxy.networkAddress` (string)
    An IP address or FQDN to address the proxy server

  - `network.proxy.port` (integer)
    Port number of the proxy server

  - `override` (object)
    User supplied parameters used to override automatic VM resource configuration with a fixed configuration.
If 0 is returned for the values then no override has been configured.

  - `override.cpu` (number)
    Number of vCPU cores.
    Example: 8

  - `override.ramInGiB` (number)
    Amount of RAM in GiB.
    Example: 24

  - `override.storageInTiB` (number)
    Total storage capacity (TiB) of the Protection Store Gateway.
    Example: 2

  - `remoteAccessEnabled` (boolean)

  - `remoteAccessStationId` (string)
    The station ID (SID) that is required for remote desktop access

  - `serialNumber` (string)
    The serial number of this Protection Store Gateway

  - `size` (object)
    User supplied parameters used to size the Protection Store Gateway.

  - `size.maxInCloudDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the Cloud Protection Stores.
    Example: 2

  - `size.maxInCloudRetentionDays` (number)
    The maximum retention period for cloud backups in days.
    Example: 2

  - `size.maxOnPremDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the On-Prem Protection Store.
    Example: 2

  - `size.maxOnPremRetentionDays` (number)
    The maximum retention period for local backups in days.
    Example: 2

  - `softwareVersion` (string)
    Software version of the Protection Store Gateway

  - `state` (string)
    State of Protection Store Gateway.
    Enum: "PSG_STATE_QUERYING_CATALOGUE", "PSG_STATE_DEPLOYING", "PSG_STATE_DEPLOYED", "PSG_STATE_DEPLOYED_ERROR", "PSG_STATE_REGISTERING", "PSG_STATE_REGISTERED", "PSG_STATE_REGISTERED_ERROR", "PSG_STATE_OK", "PSG_STATE_DELETING", "PSG_STATE_ERROR", "PSG_STATE_POWERING_ON", "PSG_STATE_DELETING_STORES", "PSG_STATE_DELETING_UNREGISTERING", "PSG_STATE_DELETING_VM_SHUTTING_DOWN", "PSG_STATE_DELETING_VM_DELETING", "PSG_STATE_DEPLOYING_STORAGE", "PSG_STATE_UPDATING_STORAGE_MOD", "PSG_STATE_UPDATING_STORAGE_DEL", "PSG_STATE_UPDATING_STORAGE_ADD", "PSG_STATE_UPDATING", "PSG_STATE_VM_POWERING_ON", "PSG_STATE_VM_SHUTTING_DOWN", "PSG_STATE_VM_RESTARTING", "PSG_STATE_OK_OFF", "PSG_STATE_UNKNOWN", "PSG_STATE_VM_CREATING_NIC", "PSG_STATE_VM_UPDATING_RESOURCES", "PSG_STATE_CONFIGURING_RESOURCES", "PSG_STATE_REBOOTING_AFTER_RESTORE", "PSG_STATE_REBOOTED_AFTER_RESTORE"

  - `supportUserCiphertext` (string)

  - `vmId` (string)
    Id of the VM

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


