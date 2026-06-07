---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/clone"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4snapshotclonecreate.md"
scraped_at: "2026-06-07T06:14:27.561776+00:00Z"
---

# Create a clone of a snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000 systems.

Create a clone of a snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000 systems.

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/clone
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `snapshotId` (string, required)
    UID of the snapshots
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Request fields (application/json):

  - `destinationVolume` (string, required)
    Name of the destination volume.
    Example: "destinationVol1"

  - `autoLun` (boolean,null)
    Secify to use auto lun number.
    Example: true

  - `destinationCpg` (string,null)
    Name of the User CPG
    Example: "SSD_r6"

  - `hostGroupId` (string,null)
    Unique identifier of host group.
    Example: "fd3244ef7f1ab8bd16500c7a41bdf8f8"

  - `lun` (integer,null)
    LUN of volume.

  - `priority` (string,null)
    Priority of the task for clone of a snashot. Defualts to MEDIUM.
    Enum: "PRIORITYTYPE_HIGH", "PRIORITYTYPE_MED", "PRIORITYTYPE_LOW"

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


