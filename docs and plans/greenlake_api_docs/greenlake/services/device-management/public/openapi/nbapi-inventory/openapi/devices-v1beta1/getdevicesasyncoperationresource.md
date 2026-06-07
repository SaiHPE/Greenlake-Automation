---
title: "GET /devices/v1beta1/async-operations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v1beta1/getdevicesasyncoperationresource.md"
scraped_at: "2026-06-07T06:15:19.342169+00:00Z"
---

# Get progress or status of async operations in devices (deprecated)

The add and update device APIs are asynchronous. Use this API to find the status of the asynchronous add and update operations.  An asynchronous resource tracks the status of an asynchronous operation. An asynchronous resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT) will no longer be accessible 24 hours after reaching the terminal state.  The TIMEOUT state indicates that the operation was in an INITIALIZED or RUNNING state for a period greater than the timeout set. If an asynchronous operation resource coming from an asynchronous request consists of multiple devices, a breakdown of succeeded devices and failed devices, if there are any, will be returned as the response. In this case, the device serial number identifies each device. NOTE: You need view permissions for the Devices and Subscription service to invoke this API. Rate limits are enforced on this API. 90 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

Endpoint: GET /devices/v1beta1/async-operations/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier of an asynchronous API operation.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the device.
    Example: "3292c36d-30ef-4f26-823b-76b5d213b670"

  - `type` (string, required)
    The type of the resource
    Example: "devices/asyncOperation"

  - `status` (string)
    The current status of an asynchronous operation.
    Enum: "INITIALIZED", "RUNNING", "FAILED", "SUCCEEDED", "TIMEDOUT", "PAUSED"

  - `startedAt` (string)
    Date and time the asynchronous operation began in UTC format.

  - `endedAt` (string)
    Date and time the asynchronous operation ended in UTC format.

  - `progressPercent` (integer)
    A number that indicates how close to completion the asynchronous operation is.

  - `suggestedPollingIntervalSeconds` (integer)
    The suggested time to wait (in minutes) before calling the operation again.

  - `timeoutMinutes` (integer)
    The number of minutes it took for the operation to time out.

  - `result` (object)
    An array that provides information on successful or unsuccessful operations.

  - `resultType` (string)
    Relates individual devices to a result type. A result type declares if an operation was successful or unsuccessful.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `badRequestErrorDetails` (array)

  - `badRequestErrorDetails.type` (string, required)
    The type of error details.

  - `badRequestErrorDetails.issues` (array, required)
    An array of request issues.

  - `badRequestErrorDetails.issues.source` (string)
    The part of the request with an issue.

  - `badRequestErrorDetails.issues.subject` (string)
    The issue key.

  - `badRequestErrorDetails.issues.description` (string)
    An explanation of the issue.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `serverErrorDetails` (array)

  - `serverErrorDetails.type` (string, required)

  - `serverErrorDetails.retryAfterSeconds` (integer, required)


