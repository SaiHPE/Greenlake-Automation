---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4volumesetssnapshotcreate.md"
scraped_at: "2026-06-07T06:14:35.421956+00:00Z"
---

# Create snapshot for application set identified by {id}

Create snapshot for application set identified by {id}

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets
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

  - `vvNamePattern` (string,null, required)
    name pattern
    Enum: "PARENT_TIMESTAMP", "PARENT_SEC_SINCE_EPOCH"

  - `snapshotName` (string,null, required)
    Name for snapshot. For the HPE Alletra Storage MP B10000 systems, the maximum supported length is 31 characters in OS versions up to 10.4.0. For the OS version 10.4.2 and above, this limit is 248 characters.
    Example: "snapshot_oracle_1611807822"

  - `comment` (string,null)
    Comment if any

  - `expireSecs` (integer,null)
    Expiration time in seconds
    Example: 100

  - `readOnly` (boolean,null)
    Read only or Read/Write

  - `retainSecs` (integer,null)
    Reatain time in seconds
    Example: 86400

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


