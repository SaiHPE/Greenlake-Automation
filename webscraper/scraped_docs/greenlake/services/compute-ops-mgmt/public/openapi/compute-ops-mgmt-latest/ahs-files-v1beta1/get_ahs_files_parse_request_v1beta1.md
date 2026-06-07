---
title: "GET /compute-ops-mgmt/v1beta1/ahs-files"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/ahs-files-v1beta1/get_ahs_files_parse_request_v1beta1.md"
scraped_at: "2026-06-07T06:14:58.159208+00:00Z"
---

# List of all AHS files

Retrieves the status of the AHS file parsing request.

Endpoint: GET /compute-ops-mgmt/v1beta1/ahs-files
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `items` (array, required)
    Array of ahs file parsing status responses.

  - `items.id` (string)
    Unique file identifier (File UUID) of the ahs-files resource given by the system.
    Example: "017a9224-4d6e-4adb-9c78-321f95c7bb2c"

  - `items.type` (string)
    Type of the resource

  - `items.generation` (number)
    Monotonically increasing update counter.
    Example: 1

  - `items.createdAt` (string)
    Time of ahs-file creation.
    Example: "2024-12-05 10:25:23.302032Z"

  - `items.updatedAt` (string)
    Time of ahs-file updation.
    Example: "2024-12-05 10:25:46.562205Z"

  - `items.resourceUri` (string)
    Resource URI of the ahs-file.
    Example: "/compute-ops-mgmt/v1beta1/ahs-files/017a9224-4d6e-4adb-9c78-321f95c7bb2c"

  - `items.name` (string)
    Name of the AHS file.
    Example: "HPE_MXQ0xxxT3_20250108_Server.ahs"

  - `items.baseUrl` (string,null,string,null)
    AWS S3 bucket pre-signed URL generated while uploading the AHS file.

  - `items.parameters` (array)
    Key value pairs attributes of parameters list supplied for uploading the AHS file to AWS S3 bucket.
    Example: "[]"

  - `items.parameters.name` (string)
    The name of this attribute
    Example: "key"

  - `items.parameters.value` (string)
    The value of this attribute
    Example: "AHS_DISCONNECT/42xx75fcddef11ebaeaea25R6Z73AAE/c924e770-f5f0xxxx/presigned_post.ahs"

  - `items.parsingStatus` (object)
    file parsing request details

  - `items.parsingStatus.status` (string)
    Status of the file parsing request.
    Enum: "ANALYSIS_PENDING", "ANALYSIS_IN_PROGRESS", "ANALYSIS_SUCCESS", "ANALYSIS_FAILED"

  - `items.parsingStatus.statusReason` (string,null,string,null)
    Reason for the status of the file parsing request.

  - `items.parsingStatus.statusModifiedAt` (string)
    Time of ahs-file status modification
    Example: "2024-12-05 10:25:49.562196Z"

  - `items.parsingStatus.errorCode` (string)
    Error code for the file parsing request.

  - `items.parsingResults` (object)
    file parsing result details

  - `items.parsingResults.components` (object,null,object,null)
    Dictionary of components parsed.

  - `items.parsingResults.components.INVENTORY` (object,object)
    Component name.

  - `items.parsingResults.components.INVENTORY.csv` (string)
    CSV file name of the inventory details of the server.
    Example: "MXQ0xxxT3-20241205-1025-SERVER_INVENTORY.csv"

  - `items.parsingResults.components.INVENTORY.json` (string)
    JSON file name of the inventory details of the server.
    Example: "MXQ0xxxT3-20241205-1025-SERVER_INVENTORY.json"

  - `items.hardware` (object)
    Server hardware details

  - `items.hardware.productId` (string)
    Example: "P2xx99-B21"

  - `items.hardware.serialNumber` (string)
    Example: "MXQ0xxxT3"

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


