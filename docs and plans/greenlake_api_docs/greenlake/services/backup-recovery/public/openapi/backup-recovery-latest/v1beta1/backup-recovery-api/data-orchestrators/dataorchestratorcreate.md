---
title: "POST /backup-recovery/v1beta1/data-orchestrators"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratorcreate.md"
scraped_at: "2026-06-07T06:14:13.643246+00:00Z"
---

# Register a new Data Orchestrator with DSCC

This API is used to register a new Data Orchestrator with the DSCC customer account.

To register the Data Orchestrator, the unique Activation Code that 
is displayed on the Data Orchestrator must be provided.

Endpoint: POST /backup-recovery/v1beta1/data-orchestrators
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `activationCode` (string, required)
    Enter the Activation Code displayed on the Data Orchestrator.

  - `displayName` (string)
    User-defined name given to the Data Orchestrator by the customer.

## Response 201 fields (application/json):

  - `id` (string, required)
    UUID identifying a Data Orchestrator.

  - `type` (string, required)
    backup-recovery/data-orchestrator

  - `connectionState` (string)
    Connection state of Data Orchestrator to DSCC.
    Enum: "CONNECTED", "DISCONNECTED"

  - `consoleUri` (string)
    The 'self' reference for this resource in the console.

  - `customerId` (string)
    The customer application identifier

  - `displayName` (string)
    User-defined name given to Data Orchestrator.
    Example: "Data Orchestrator 1"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `name` (string)
    Name given to Data Orchestrator.
    Example: "Data Orchestrator 1"

  - `resourceUri` (string)
    The self reference for this resource.

  - `serialNumber` (string)
    Data Orchestrator serial number.

  - `softwareVersion` (string)
    Data Orchestrator software version.

  - `state` (string)
    Enum: "OK", "UPGRADING", "UPDATING", "RESTORING", "RECOVERING", "UNKNOWN", "DEGRADED"

  - `stateReason` (string)
    Reason for the Data Orchestrator being in the current state. This will be empty when the Data Orchestrator is in an OK state.

  - `status` (string)
    Enum: "OK", "WARNING", "ERROR"

  - `upTimeInSeconds` (integer)
    Returns the number of seconds since Data Orchestrator was powered on. Returns 0 if Data Orchestrator is DISCONNECTED from DSCC.

  - `createdAt` (string)
    UTC time when the Data Orchestrator was activated.
    Example: "2019-07-21T17:32:28Z"

  - `dateTime` (object)
    This details the current date and time of the Data Orchestrator, how the current date and time is determined, as well as the user specified timezone. The date and time will have either been explicitly set by the user, determined from a configured NTP server or synchronized with the Data Orchestrator VM host.

  - `dateTime.methodDateTimeSet` (string)
    Method for how data and time is set on the Data Orchestrator.
    Enum: "NTP", "VM_HOST"

  - `dateTime.timezone` (string)
    Time zone in which the Data Orchestrator is deployed.
    Example: "Europe/London, Australia/Sydney, Asia/Tokyo, America/NewYork"

  - `interfaces` (object)

  - `interfaces.network` (object)

  - `interfaces.network.defaultGateway` (string)
    IP address or FQDN of the default gateway.
    Example: "172.29.233.254"

  - `interfaces.network.hostname` (string)
    IP address or FQDN of the Data Orchestrator.
    Example: "atlas.hpe.com"

  - `interfaces.network.nameServers` (array)
    List of configured DNS servers configured on the Data Orchestrator.

  - `interfaces.network.nameServers.networkAddress` (string)
    IP address or FQDN of DNS server.
    Example: "172.29.232.103"

  - `interfaces.network.nic` (array)
    List of network interfaces configured on the Data Orchestrator. Note that this information will not include any loopback interfaces.

  - `interfaces.network.nic.addressType` (string)
    Indicates whether the address is assigned statically or via DHCP.
    Enum: "DHCP", "STATIC"

  - `interfaces.network.nic.enabled` (boolean)
    Indicates whether the interface is enabled or disabled.

  - `interfaces.network.nic.name` (string)
    Name of the network interface.
    Example: "ens160"

  - `interfaces.network.nic.networkAddress` (string)
    IP address associated with the network interface.
    Example: "172.29.232.100"

  - `interfaces.network.nic.state` (string)
    Indicates whether the interface is up or down.
    Enum: "UP", "DOWN"

  - `interfaces.network.nic.staticRoutes` (array)
    List of static routes.

  - `interfaces.network.nic.staticRoutes.gateway` (string)
    IP address or FQDN of gateway.
    Example: "172.29.233.254"

  - `interfaces.network.nic.staticRoutes.networkAddress` (string)
    IP address associated with the static route.
    Example: "172.29.232.105"

  - `interfaces.network.nic.staticRoutes.subnetMask` (string)
    Subnet mask associated with the static route.
    Example: "255.255.255.0"

  - `interfaces.network.nic.subnetMask` (string)
    Subnet mask.
    Example: "255.255.255.0"

  - `interfaces.network.proxy` (object)

  - `interfaces.network.proxy.credentials` (object)

  - `interfaces.network.proxy.credentials.username` (string)

  - `interfaces.network.proxy.networkAddress` (string)
    An IP address or FQDN to address the proxy server
    Example: "http://proxy.mydomain.com"

  - `interfaces.network.proxy.port` (integer)
    Port number of the proxy server

  - `interfaces.network.searchDomains` (array)
    List of search domains.
    Example: ["mydomain.com"]

  - `lastUpdateCheckTime` (string)
    UTC time when a software update check was last performed.
    Example: "2019-07-21T17:32:28Z"

  - `latestRecoveryPoint` (string)
    UTC time when Data Orchestrator catalogue was last protected.
    Example: "2019-07-21T17:32:28Z"

  - `ntp` (object)

  - `ntp.ntpServers` (array)
    NTP servers against which the Data Orchestrator should synchronize.

  - `ntp.ntpServers.networkAddress` (string)
    An IP address or FQDN of the NTP server.
    Example: "pool.ntp.org"

  - `ntp.stateReason` (string)
    Reason for the current state of the NTP configuration.

  - `platform` (string)
    Hypervisor platform.
    Enum: "VMWARE_ESXI"

  - `poweredOnAt` (string)
    UTC time when Data Orchestrator was last powered on.
    Example: "2019-07-21T17:32:28Z"

  - `totalMemoryInGiB` (integer)
    Total RAM configured for the Data Orchestrator in GiB.

  - `updatedAt` (string)
    UTC time when the Data Orchestrator was last updated.
    Example: "2019-07-21T17:32:28Z"

  - `vCpu` (integer)
    Number of virtual CPUs configured for the Data Orchestrator.

  - `adminUserCiphertext` (string)
    Ciphertext to allow HPE Support to authenticate with the Data Orchestrator with unrestricted admin privileges.

  - `infosightEnabled` (boolean)
    The Data Orchestrator is sending telemetry to InfoSight.

  - `remoteAccessEnabled` (boolean)
    HPE Support can remotely access the Data Orchestrator for the purposes of debug. For HPE Support to authenticate, the ciphertext must be shared by the user.

  - `remoteAccessStationId` (string)
    An identifier that HPE Support can use to remotely access the Data Orchestrator.

  - `supportUserCiphertext` (string)
    Ciphertext to allow HPE Support to authenticate with the Data Orchestrator with restricted support privileges.

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

## Response 412 fields (application/json):

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


