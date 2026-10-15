---
title: "PATCH /backup-recovery/v1beta1/data-orchestrators/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/data-orchestrators/dataorchestratormodify.md"
scraped_at: "2026-06-07T06:14:14.164697+00:00Z"
---

# Modify the configuration of a Data Orchestrator

This API allows the configuration of the Data Orchestrator to be modified.

This configuration options include:
* Network
* Date & Time

Endpoint: PATCH /backup-recovery/v1beta1/data-orchestrators/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    id of the Data Orchestrator.

## Request fields (application/merge-patch+json):

  - `dateTime` (object)
    These attributes are used to configure the Data Orchestrator date and time.

  - `dateTime.methodDateTimeSet` (string)
    Method for how data and time is set on the Data Orchestrator.
    Enum: "NTP", "VM_HOST"

  - `dateTime.timezone` (string)
    Timezone
    Example: "Europe/London, Australia/Sydney, Asia/Tokyo, America/NewYork"

  - `displayName` (string)
    User-defined name given to the Data Orchestrator.
    Example: "Data Orchestrator 1"

  - `network` (object)

  - `network.defaultGateway` (string)
    IP address or FQDN of default gateway.
    Example: "172.29.233.254"

  - `network.hostname` (string)
    IP address or FQDN of the Data Orchestrator.
    Example: "data-orchestrator.mydomain.com"

  - `network.nameServers` (array)
    List of configured DNS servers configured on the Data Orchestrator.

  - `network.nameServers.networkAddress` (string)
    IP address or FQDN of DNS server.
    Example: "172.29.232.103"

  - `network.nic` (array)

  - `network.nic.addressType` (string)
    Indicates whether the address is assigned statically or via DHCP.
    Enum: "DHCP", "STATIC"

  - `network.nic.enabled` (boolean)
    Indicates whether the interface is enabled or disabled.

  - `network.nic.name` (string)
    Name of the network interface.
    Example: "ens160"

  - `network.nic.networkAddress` (string)
    IP address associated with the network interface.
    Example: "172.29.232.100"

  - `network.nic.staticRoutes` (array)
    List of static routes.

  - `network.nic.staticRoutes.gateway` (string)
    IP address or FQDN of gateway.
    Example: "172.29.233.254"

  - `network.nic.staticRoutes.networkAddress` (string)
    IP address associated with the static route.
    Example: "172.29.232.105"

  - `network.nic.staticRoutes.subnetMask` (string)
    Subnet mask associated with the static route.
    Example: "255.255.255.0"

  - `network.nic.subnetMask` (string)
    Subnet mask.
    Example: "255.255.255.0"

  - `network.proxy` (object)

  - `network.proxy.credentials` (object)
    Credentials for the proxy server if required.

  - `network.proxy.credentials.password` (string)

  - `network.proxy.credentials.username` (string)

  - `network.proxy.networkAddress` (string)
    An IP address or FQDN to address the proxy server.
    Example: "http://proxy.mydomain.com"

  - `network.proxy.port` (integer)
    Port number of the proxy server.

  - `network.searchDomains` (array)
    List of search domains.
    Example: ["mydomain.com"]

  - `ntp` (object)

  - `ntp.ntpServers` (array)
    NTP servers

  - `ntp.ntpServers.networkAddress` (string)
    An IP address or FQDN of the NTP server.
    Example: "pool.ntp.org"

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


