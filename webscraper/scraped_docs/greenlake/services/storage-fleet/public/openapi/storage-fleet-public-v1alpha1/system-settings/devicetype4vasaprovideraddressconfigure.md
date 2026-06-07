---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasaprovider"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4vasaprovideraddressconfigure.md"
scraped_at: "2026-06-07T06:16:06.265436+00:00Z"
---

# Configure IP addresses for VASA Provider High Availability (VPHA) on a HPE Alletra Storage MP B10000 storage system

Add a VASA Provider IP address on the specified node. After associating the VASA Provider (VP) to the specific node then this information is used to start second instance of the VP to achieve VPHA. This configuration will provide high availability of the connection between storage device and vSphere client and minimize service downtime during failures. Applicable for HPE Alletra Storage MP B10000 storage system with 10.5.0 version and later.

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasaprovider
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `configVpAddress` (array, required)
    List of nodeIds and Ipaddress to be configured for VASA Provider. Applicable for HPE Alletra Storage MP B10000 storage system with 10.5.0 version and later.

  - `configVpAddress.ipv4Address` (string)
    IP Address of the Vasa Provider
    Example: "16.172.189.110"

  - `configVpAddress.ipv4NetMask` (string)
    Netmask of the Vasa Provider
    Example: "255.255.254.0"

  - `configVpAddress.ipv6Address` (string)
    IPV6 Address of the Vasa Provider
    Example: "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

  - `configVpAddress.ipv6PrefixLen` (string)
    IPV6 Prefix length of the Vasa Provider
    Example: "64"

  - `configVpAddress.nodeId` (string)
    Node ID of the Vasa Provider Address to be configured
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


