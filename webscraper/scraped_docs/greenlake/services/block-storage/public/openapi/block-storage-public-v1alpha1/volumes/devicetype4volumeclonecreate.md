---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/clone"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4volumeclonecreate.md"
scraped_at: "2026-06-07T06:14:28.473312+00:00Z"
---

# Create a clone volume identified by {id} for HPE Alletra Storage MP B10000 systems.

Create a clone volume identified by {id} for HPE Alletra Storage MP B10000 systems.

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/clone
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID(volumeuid) of the storage system
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Request fields (application/json):

  - `destinationVolume` (string, required)
    Name of the destination volume.
    Example: "destinationVol1"

  - `offlineClone` (object,null)
    Offline clone of a volume.

  - `offlineClone.createVolume` (object,null)
    Create a new volume for clone.

  - `offlineClone.createVolume.destinationCpg` (string,null)
    Name of the User CPG
    Example: "SSD_r6"

  - `offlineClone.enableResync` (boolean,null)
    Specify to save a snapshot for fast resynchronization.
    Example: true

  - `offlineClone.useExistingVolume` (boolean,null)
    Specify to use existing volume or create a new volume for clone.
    Example: true

  - `online` (boolean,null)
    Create an online or offline clone of a volume.
    Example: true

  - `onlineClone` (object,null)
    Online clone of a volume.

  - `onlineClone.autoLun` (boolean,null)
    Specify to use auto lun number.
    Example: true

  - `onlineClone.hostGroupId` (string,null)
    Unique identifier of host group.
    Example: "fd3244ef7f1ab8bd16500c7a41bdf8f8"

  - `onlineClone.lun` (integer,null)
    LUN of volume.

  - `onlineClone.nvmeTransportType` (string,null)
    Transport type of the protocol. Configuration of the transport type is only supported for NVMe protocol starting from the system OS version 10.3.0 and the default transport type value is FC.
    Example: "TCP"

  - `priority` (string,null)
    Priority of the task for clone volume. Defualts to MEDIUM.
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


