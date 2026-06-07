---
title: "PATCH /compute-ops-mgmt/v1beta1/ahs-files/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/ahs-files-v1beta1/patch_ahs_file_parse_status_request_v1beta1_by_id.md"
scraped_at: "2026-06-07T06:14:40.601061+00:00Z"
---

# Update the parsing status of an AHS file

This API triggers a patch request to update the parsing status of an AHS file.
The patch request allows updating the existing parsing status of an AHS file from ANALYSIS_PENDING or ANALYSIS_IN_PROGRESS to ANALYSIS_FAILED.

Endpoint: PATCH /compute-ops-mgmt/v1beta1/ahs-files/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique File Identifier (File UUID)

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed.

## Request fields (application/json):

  - `parsingStatus` (object)
    Example: {"status":"ANALYSIS_FAILED"}

  - `parsingStatus.status` (string)
    Status of the file parsing request.
    Enum: "ANALYSIS_FAILED"

## Response 200 fields (application/json):

  - `id` (string)
    Unique file identifier (File UUID) of the ahs-files resource given by the system.
    Example: "017a9224-4d6e-4adb-9c78-321f95c7bb2c"

  - `type` (string)
    Type of the resource

  - `generation` (number)
    Monotonically increasing update counter.
    Example: 2

  - `createdAt` (string)
    Time of ahs-file creation.
    Example: "2024-12-05 10:25:23.302032Z"

  - `updatedAt` (string)
    Time of ahs-file updation.
    Example: "2024-12-05 10:25:46.562205Z"

  - `resourceUri` (string)
    Resource URI of the ahs-file.
    Example: "/compute-ops-mgmt/v1beta1/ahs-files/017a9224-4d6e-4adb-9c78-321f95c7bb2c"

  - `name` (string)
    Name of the AHS file.
    Example: "HPE_MXQ0xxxT3_20250108_Server.ahs"

  - `baseUrl` (string,null)
    AWS S3 bucket pre-signed URL generated while uploading the AHS file.

  - `parameters` (array)
    Key value pairs attributes of parameters list supplied for uploading the AHS file to AWS S3 bucket.
    Example: []

  - `parameters.name` (string)
    The name of this attribute
    Example: "key"

  - `parameters.value` (string)
    The value of this attribute
    Example: "AHS_DISCONNECT/42xx75fcddef11ebaeaea25R6Z73AAE/c924e770-f5f0xxxx/presigned_post.ahs"

  - `parsingStatus` (object)
    file parsing request details

  - `parsingStatus.status` (string)
    Status of the file parsing request.
    Enum: "ANALYSIS_FAILED"

  - `parsingStatus.statusModifiedAt` (string)
    Time of ahs-file status modification
    Example: "2024-12-05 10:25:49.562196Z"

  - `parsingStatus.statusReason` (string,null)
    Reason for the status of the file parsing request.
    Example: "due to intermittent issue. Retry the upload operation (error code: AHSE-101)."

  - `parsingStatus.errorCode` (string)
    Error code for the file parsing request.
    Example: "AHSE-101"

  - `parsingResults` (object)
    file parsing result details
    Example: {}

  - `parsingResults.components` (object,null)
    Dictionary of components parsed.

  - `parsingResults.components.INVENTORY` (object)
    Component name.

  - `parsingResults.components.INVENTORY.csv` (string)
    CSV file name of the inventory details of the server.

  - `parsingResults.components.INVENTORY.json` (string)
    JSON file name of the inventory details of the server.

  - `hardware` (object)
    Server hardware details

  - `hardware.productId` (string)

  - `hardware.serialNumber` (string)

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


