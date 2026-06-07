---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networksettingsassociate.md"
scraped_at: "2026-06-07T06:16:17.034345+00:00Z"
---

# Post Network-Settings details for an HPE Alletra Storage MP B10000 storage system

Post Network-Settings details for an HPE Alletra Storage MP B10000 storage system

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `dnsAddresses` (array,null)
    Dns address of the system

  - `ipv4Address` (string,null)
    ipv4 address of the system

  - `ipv4Gateway` (string,null)
    ipv4 gateway of the system

  - `ipv4SubnetMask` (string,null)
    NetMask for IPV4 address

  - `ipv6Address` (string,null)
    IPV6 address of the system

  - `ipv6Gateway` (string,null)
    IPV6 address of the system

  - `ipv6PrefixLen` (string,null)
    IPV6 Prefix length

  - `proxyParams` (object,null)
    Proxy Setting details for a device

  - `proxyParams.authenticationRequired` (string,null)
    Is authentication required. Allowed values are enabled or disabled

  - `proxyParams.proxyPort` (integer,null)
    Proxy Server Port. Allowed values are 1-65535

  - `proxyParams.proxyProtocol` (string,null)
    Supported proxy protocols are HTTP, SOCKS4 and SOCKS5.

  - `proxyParams.proxyServer` (string,null)
    Proxy server IP address

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

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


