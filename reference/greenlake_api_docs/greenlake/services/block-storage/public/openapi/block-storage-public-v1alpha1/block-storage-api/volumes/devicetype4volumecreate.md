---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volumes/devicetype4volumecreate.md"
scraped_at: "2026-06-07T06:14:37.357696+00:00Z"
---

# Create a new volume for an HPE Alletra Storage MP B10000 storage system

Create a new volume for an HPE Alletra Storage MP B10000 storage system

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `name` (string, required)
    Name of the volume. For the HPE Alletra Storage MP B10000 systems, the maximum supported length is 31 characters in OS versions up to 10.4.0. For the OS version 10.4.2 and above, this limit is 255 characters.
    Example: "<resource_name>"

  - `userCpg` (string, required)
    User CPG
    Example: "SSD_r6"

  - `sizeMib` (integer, required)
    Size of the volume to be created.
    Example: 16384

  - `comments` (string,null)
    test
    Example: "test"

  - `count` (integer,null)
    Volumes count
    Example: 2

  - `dataReduction` (boolean,null)
    Data Reduction
    Example: true

  - `ransomware` (boolean,null)
    This attribute enables/disables ransomware detection on the volume. By Default, it is set to false. This applies to the HPE Alletra Storage MP B10000 systems running OS version 10.5.0 and later.

  - `snapshotAllocWarning` (integer,null)
    Snapshot Alloc Warning
    Example: 5

  - `userAllocWarning` (integer,null)
    User Alloc Warning
    Example: 5

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


