---
title: "PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4editproximitysettings.md"
scraped_at: "2026-06-07T06:14:26.787784+00:00Z"
---

# Change proximity settings of hosts where volume sets are exported identified by {id} and {systemId} from HPE Alletra Storage MP B10000

Change proximity settings of hosts where volume sets are exported identified by {id} and {systemId} from HPE Alletra Storage MP B10000

Endpoint: PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Request fields (application/json):

  - `hostGroups` (array)

  - `hostGroups.hostGroupName` (string, required)
    Name of the host group for which proximity setting is getting changed. This is the host group which is present in device.
    Example: "tstHostGroup"

  - `hostGroups.proximity` (string, required)
    Host group proximity setting for Active Peer Persistence configuration. Supported values are - PRIMARY, SECONDARY and ALL. This is applicable when all the systems in the replication configuration has the OS version 10.5.0 or later
    Enum: "PRIMARY", "SECONDARY", "ALL"

  - `hosts` (array)

  - `hosts.hostName` (string, required)
    Name of the host for which proximity setting is getting changed. This is the host which is present in device.
    Example: "tstHost"

  - `hosts.proximity` (string, required)
    Host proximity setting for Active Peer Persistence configuration. Supported values are - PRIMARY, SECONDARY and ALL
    Enum: "PRIMARY", "SECONDARY", "ALL"

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


