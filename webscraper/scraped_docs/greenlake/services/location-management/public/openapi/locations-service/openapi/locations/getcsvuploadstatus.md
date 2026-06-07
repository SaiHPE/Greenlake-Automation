---
title: "GET /locations/v1/locations/async-operation/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service/openapi/locations/getcsvuploadstatus.md"
scraped_at: "2026-06-07T06:15:29.689312+00:00Z"
---

# Retrieve a CSV upload status

Return status information for a CSV location upload by using the async location ID as a parameter.

Endpoint: GET /locations/v1/locations/async-operation/{id}
Version: v1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique indentifier of the async operation location ID. For example, 945e70ec-b043-4cad-9ed0-069c06fdb8af.

## Response 200 fields (application/json):

  - `id` (string, required)
    CSV upload operation generated ID.

  - `result` (object, required)

  - `result.totalCount` (integer)

  - `result.succeededCount` (integer)
    Number of locations created successfully.

  - `result.failedCount` (integer)
    The number of failed location creations.

  - `result.failedRecords` (array)

  - `result.failedRecords.error` (object)

  - `result.failedRecords.error.message` (string)

  - `result.failedRecords.error.statusCode` (integer)

  - `result.failedRecords.name` (string)

  - `result.succeededRecords` (array)

  - `result.succeededRecords.id` (string)
    The location ID created from a CSV upload.

  - `result.succeededRecords.name` (string)
    The location name created from a CSV upload.

  - `result.errorMessage` (string)

  - `type` (string, required)
    The type of the resource.

  - `status` (string)
    The status of the CSV upload operation.
    Enum: "INITIALIZED", "IN_PROGRESS", "SUCCEEDED", "FAILED"

  - `startedAt` (string)
    The date and time the CSV upload operation started.

  - `endedAt` (string)
    The date and time the CSV upload operation ended.

  - `progressPercent` (integer)
    Progress percentage of the CSV upload operation.

  - `suggestedPollingIntervalSeconds` (integer)
    The polling interval of the CSV upload operation.

  - `timeoutMinutes` (integer)

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    Unique error code identifier (e.g., HPE_GL_LM_BAD_REQUEST).

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error for debugging purposes.

  - `httpStatusCode` (string, required)
    HTTP equivalent status code.

  - `errorDetails` (array)
    Additional details about the error.

  - `errorDetails.type` (string)
    Type of error detail (e.g., hpe.greenlake.metadata).

  - `errorDetails.source` (string)
    Source of the error (e.g., hpe.greenlake.lm).

  - `errorDetails.metadata` (object)
    Additional metadata about the error.

  - `errorDetails.metadata.error` (string)
    Detailed error message.

## Response 404 fields (application/json):

  - `errorCode` (string, required)
    Unique error code identifier (e.g., HPE_GL_LM_BAD_REQUEST).

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error for debugging purposes.

  - `httpStatusCode` (string, required)
    HTTP equivalent status code.

  - `errorDetails` (array)
    Additional details about the error.

  - `errorDetails.type` (string)
    Type of error detail (e.g., hpe.greenlake.metadata).

  - `errorDetails.source` (string)
    Source of the error (e.g., hpe.greenlake.lm).

  - `errorDetails.metadata` (object)
    Additional metadata about the error.

  - `errorDetails.metadata.error` (string)
    Detailed error message.

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique error code identifier (e.g., HPE_GL_LM_BAD_REQUEST).

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error for debugging purposes.

  - `httpStatusCode` (string, required)
    HTTP equivalent status code.

  - `errorDetails` (array)
    Additional details about the error.

  - `errorDetails.type` (string)
    Type of error detail (e.g., hpe.greenlake.metadata).

  - `errorDetails.source` (string)
    Source of the error (e.g., hpe.greenlake.lm).

  - `errorDetails.metadata` (object)
    Additional metadata about the error.

  - `errorDetails.metadata.error` (string)
    Detailed error message.


