---
title: "PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-rcip"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/ports/devicetype4rcipportedit.md"
scraped_at: "2026-06-07T06:15:56.860393+00:00Z"
---

# Edit rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Edit rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-rcip
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the port
    Example: "d0fcfe2ff572f44e5beb0a9712c76d5d"

## Request fields (application/json):

  - `gatewayAddress` (string,null)
    Gateway address to edit to for IPv4 address
    Example: "255.255.255.0"

  - `gatewayAddressV6` (string,null)
    Gateway address to edit to for IPv6 address
    Example: "FE80::1"

  - `ipAddress` (string,null)
    IPv4 address to edit to
    Example: "192.168.193.21"

  - `ipAddressV6` (string,null)
    IPv6 address to edit to
    Example: "2001:db8:abcd:12:ffff:ffff:ffff:ff16"

  - `mtu` (string)
    MTU to edit to. Possible Values: "1500", "9000"
    Example: "1500"

  - `netMask` (string,null)
    NetMask address to edit to for IPv4 address
    Example: "255.255.255.0"

  - `netMaskV6` (string,null)
    NetMask address to edit to for IPv6 address
    Example: "64"

  - `speedConfigured` (string,null)
    Configured speed. Possible Values: auto, "1", "2", "4", "8", "16", "32"
    Example: "1"

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


