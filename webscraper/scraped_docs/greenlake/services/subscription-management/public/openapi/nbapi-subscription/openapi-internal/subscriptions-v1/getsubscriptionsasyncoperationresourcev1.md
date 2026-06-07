---
title: "GET /subscriptions/v1/async-operations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/getsubscriptionsasyncoperationresourcev1.md"
scraped_at: "2026-06-07T06:15:52.890204+00:00Z"
---

# Get progress or status of async operations in subscriptions

Use this API call to find the status of the asynchronous add and update subscriptions API calls.  An asynchronous resource is  generated to track the status of an asynchronous operation. An asynchronous  resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT)  will no longer be accessible 24 hours after reaching the terminal state. An  asynchronous resource is set to the TIMEOUT state if the resource  has been in an INITIALIZED or RUNNING state for a period greater than the  timeout set. If an asynchronous operation resource coming from an asynchronous  request consists of multiple subscriptions, a breakdown of succeeded  subscriptions and failed subscriptions, if there are any, is returned  as the response. In this case, the subscription key identifies each subscription.Note: You need view permissions for the Devices and  Subscription service to invoke this API endpoint.  Rate limits are enforced on this API endpoint, and 30 requests per minute are supported per workspace. The API endpoint returns 429 if this threshold is breached.

Endpoint: GET /subscriptions/v1/async-operations/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier returned by an asynchronous API operation.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the asynchronous operation.
    Example: "3292c36d-30ef-4£26-823b-76b5d213b670"

  - `type` (string, required)
    The type of the resource.
    Example: "subscriptions/asyncOperation"

  - `status` (string)
    The current status of the asynchronous operation.
    Enum: "INITIALIZED", "RUNNING", "FAILED", "SUCCEEDED", "TIMEDOUT", "PAUSED"

  - `startedAt` (string)
    Time the asynchronous operation started.

  - `endedAt` (string)
    Time the asynchronous operation ended.

  - `progressPercent` (integer)
    Percentage completion of the asynchronous operation.

  - `suggestedPollingIntervalSeconds` (integer)
    The suggested time to wait (in minutes) before calling the operation again.

  - `timeoutMinutes` (integer)
    The number of minutes before the operation will time out.

  - `result` (object)
    An array that provides information on successful or unsuccessful operations.

  - `resultType` (string)
    Relates individual subscriptions to a result category that indicates successfull or unsuccessful operations

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetail` (array)

  - `errorDetail.type` (string, required)
    The type of error details.

  - `errorDetail.issues` (array, required)
    An array of bad request issues.

  - `errorDetail.issues.source` (string)
    The source of the error.

  - `errorDetail.issues.subject` (string)
    The specific issue key.

  - `errorDetail.issues.description` (string)
    A brief explanation of the error.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


