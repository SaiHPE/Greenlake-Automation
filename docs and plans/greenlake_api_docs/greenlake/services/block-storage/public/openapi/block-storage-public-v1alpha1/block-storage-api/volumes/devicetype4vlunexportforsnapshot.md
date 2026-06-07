---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/export"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volumes/devicetype4vlunexportforsnapshot.md"
scraped_at: "2026-06-07T06:14:36.642767+00:00Z"
---

# Export vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Export vlun for snapshot identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/export
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

  - `hostGroupIds` (array,null, required)
    HostGroups

  - `autoLun` (boolean,null)
    Auto Lun
    Example: true

  - `lun` (array,null)
    Custom LUN Id for multiple host groups

  - `lun.hostGroupId` (string)
    Host group Id
    Example: "cb17544e9347145d22a0fac608831053"

  - `lun.lun` (integer)
    Logical Unit Number
    Example: 34

  - `lun.nvmeTransportType` (string,null)
    Transport type of the protocol. Configuration of the transport type is only supported for NVMe protocol starting from the system OS version 10.3.0 and the default transport type value is FC.
    Example: "TCP"

  - `maxAutoLun` (integer,null)
    Number of volumes.
    Example: 1

  - `noVcn` (boolean,null)
    No VCN
    Example: true

  - `override` (boolean,null)
    Override
    Example: true

  - `proximity` (string)
    Host proximity setting for Active Peer Persistence configuration. Supported values are - PRIMARY, SECONDARY and ALL. Default proximity is PRIMARY.
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


