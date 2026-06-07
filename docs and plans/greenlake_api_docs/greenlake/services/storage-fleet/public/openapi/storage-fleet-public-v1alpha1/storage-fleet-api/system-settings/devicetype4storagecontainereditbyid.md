---
title: "PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4storagecontainereditbyid.md"
scraped_at: "2026-06-07T06:16:20.698938+00:00Z"
---

# Edit storage container of HPE Alletra Storage MP B10000 storage system identified by {id}

Edit storage container of HPE Alletra Storage MP B10000 storage system identified by {id}

Endpoint: PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `vvolscId` (string, required)
    Storage container UID
    Example: "d09b59cd7bd07a4e9559e78dcea07498"

## Request fields (application/json):

  - `comment` (string,null)
    Comment of the Storage Container.
    Example: "Storage Container is for the volume"

  - `growthLimitMiB` (integer,null)
    Specifies that the auto-grow operation is limited to the specified storage amount. The storage amount can be specified in MiB. A size of 0 (default) means no limit is enforced.  To disable auto-grow, set the limit to 1.
    Example: 20

  - `growthSizeMiB` (integer,null)
    Specifies the growth increment size, the amount of logical disk storage created on each auto-grow operation. If the size is non-zero it must be 3675 MiB or greater. The size can be specified in MiB. A size of 0 disables the auto-grow feature.
    Example: 10

  - `growthWarnMiB` (integer,null)
    Specifies that the threshold of used logical disk space, when exceeded, results in a warning alert. The size can be specified in MiB. A size of 0 (default) means no warning limit is enforced. To set the warning for any used space, set the limit to 1.
    Example: 18

  - `name` (string)
    Storage Container Name.
    Example: "<resource_name>"

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


