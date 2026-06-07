---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{parentSnapshotId}/snapshots/{childSnapshotId}/restore"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/snapshots/devicetype4restoresnapshotofsnapshot.md"
scraped_at: "2026-06-07T06:14:30.557752+00:00Z"
---

# Restore a child snapshot identified by {childSnapshotId} to a read-write parent snapshot identified by {parentSnapshotId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Restore a child snapshot identified by {childSnapshotId} to a read-write parent snapshot identified by {parentSnapshotId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{parentSnapshotId}/snapshots/{childSnapshotId}/restore
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `parentSnapshotId` (string, required)
    UID of the read-write parent snapshot
    Example: "b7c4e6593f51d0b98f0e40d7e6df04fd"

  - `childSnapshotId` (string, required)
    UID of the child snapshot to be restored
    Example: "c7c4e6593f51d0b98f0e40d7e6df04fd"

## Request fields (application/json):

  - `priority` (string,null)
    Priority of the task for promoting the snapshot. Defualts to PRIORITYTYPE_MED.
    Enum: "PRIORITYTYPE_HIGH", "PRIORITYTYPE_MED", "PRIORITYTYPE_LOW"

  - `target` (string,null)
    Target read-write parent snapshot name to which the child snapshot need to be promoted.
    Example: "snapshot-rw"

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


