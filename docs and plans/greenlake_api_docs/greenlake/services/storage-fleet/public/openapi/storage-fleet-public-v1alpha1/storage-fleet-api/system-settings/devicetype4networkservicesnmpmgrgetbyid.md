---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrgetbyid.md"
scraped_at: "2026-06-07T06:16:18.538434+00:00Z"
---

# Get a specific SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system

Get a specific SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    ID of the SNMP manager
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource
    Example: "8be9321600cbf18e9c8c96bb3217f610"

  - `type` (string, required)
    The type of resource.
    Example: "snmp-manager-settings"

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1fg"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627533045690

  - `managerIp` (string,null)
    Specify the IP address of the host from which the manager runs
    Example: "15.218.169.163"

  - `notify` (string,null)
    Indicates the trap notification types defined by the HPE deviceType1 MIB
    Enum: "ALL", "NODUP", "STANDARD"

  - `port` (integer,null)
    Specify the port number where the SNMP manager receives traps
    Example: 162

  - `systemId` (string,null)
    SystemId of the storage system
    Example: "4UW0001540"

  - `systemWwn` (string,null)
    WWN of the array
    Example: "2FF70002AC018D94"

  - `user` (string,null)
    Specify the SNMPv3 user name
    Example: "user1"

  - `version` (integer,null)
    Specify the SNMP version supported
    Example: 2

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


