---
title: "GET /reporting/v1/async-operations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi-latest/v1/report-mgmt/async-operations/paths/~1reporting~1v1~1async-operations~1%7Bid%7D/get.md"
scraped_at: "2026-06-07T06:16:42.415152+00:00Z"
---

# Asynchronous operation details

Retrieve information about asynchronous operations within the reporting service. Provide the unique identifier of the operation in the parameter to monitor the progress of asynchronous tasks.  This API returns the following attributes:

  - status—Indicates the current status of the asynchronous task.
  - startedAt—Specifies the timestamp when the operation was initiated.
  - endedAt—Indicates the timestamp when the operation was completed.
  - logMessages—Provides a list of progress updates for the asynchronous operation.
  - progressPercent—Represents the progress of the operation as a percentage value ranging from 0 to 100.
  - sourceResourceUri—References the source URI that triggered the asynchronous task.
  - results—The results array provides a link to /reporting/v1/statuses/{id} to get the complete details of the report status.

Endpoint: GET /reporting/v1/async-operations/{id}
Version: v1
Security: BearerAuth

## Path parameters:

  - `id` (string, required)
    The unique identifier returned by an asynchronous API call.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 200 fields (application/json):

  - `id` (string, required)
    The primary identifier for the resource.

  - `type` (string, required)
    The type of the resource.

  - `state` (string, required)
    The state of the operation.

  - `logMessages` (array, required)
    List of progress update objects. This array can be empty.

  - `logMessages.timestamp` (string)
    The date and time the log messag was created.

  - `logMessages.message` (string)
    The log message describing the progress update.

  - `progressPercent` (integer, required)
    Percent progress of the operation as an integer value of 0 to 100.

  - `sourceResourceUri` (string, required)
    The URI reference to the resource or resource collection that initiated the operation

  - `startedAt` (string)
    The date and time the operation entered the RUNNING state.

  - `endedAt` (string)
    The date and time the operation completed in the SUCCEEDED, FAILED, or CANCELLED states.

  - `results` (array)
    List of references to resources (other than the source resource) which were created, updated, or deleted during the operation.

  - `results.resourceUri` (string)
    URI to the effected resources.

  - `results.name` (string)
    The name of the effect resource.

  - `error` (object)

  - `error.message` (string)
    User-friendly error message

  - `error.timestamp` (string)
    The date and time the error message was created.

  - `error.debugId` (string)
    Unique identifier for the instance of this error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_AUTHORIZATION_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Not authorized to get async operation details"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_FORBIDDEN_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Incorrect permission to retrieve report of id = \"1fa85f64-5434-9980-b3fc-3c963f44fgh9\""

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 404

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_NOT_FOUND_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Invalid id: 4ca85f64-9878-1234-b3fc-2c963f66afy7"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Failed to retrieve async operation details"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"


