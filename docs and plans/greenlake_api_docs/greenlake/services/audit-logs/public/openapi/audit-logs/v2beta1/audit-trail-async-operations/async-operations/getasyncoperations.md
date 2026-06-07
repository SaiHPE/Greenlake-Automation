---
title: "GET /audit-log/v2beta1/async-operations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-async-operations/async-operations/getasyncoperations.md"
scraped_at: "2026-06-07T06:16:38.656248+00:00Z"
---

# Get the list of async operations.

This endpoint retrieves the list of asynchronous audit log publish operations related to a specific workspace. Users can filter the operations based on their status using the filter query parameter.
A valid service identity workspace-scoped access token is required to access this API.

Rate limits:
- 1,000 requests per minute

Endpoint: GET /audit-log/v2beta1/async-operations
Version: v2beta1
Security: Bearer

## Query parameters:

  - `filter` (string)
    Filter operations based on their status. Supported status values are:
 * INITIALIZED
 * RUNNING
 * SUCCEEDED
 * FAILED

  - `limit` (integer)
    How many items to return at one time (max 100)

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Unique identifier for the async operation.

  - `items.type` (string, required)
    Type of the async operation.
    Enum: "/audit-log/async-operation"

  - `items.generation` (integer, required)
    The generation number of the async operation.

  - `items.sourceResourceUri` (string, required)
    URI reference to the resource or resource collection that initiated the operation.

  - `items.progressPercent` (integer, required)
    Percentage of the operation that has been completed.

  - `items.state` (string, required)
    State of the publish operation.
    Enum: "INITIALIZED", "RUNNING", "SUCCEEDED", "FAILED"

  - `items.createdAt` (string, required)
    Time at which the operation was created.

  - `items.updatedAt` (string, required)
    Time at which the record was last updated.

  - `items.startedAt` (string, required)
    Time at which the operation entered the RUNNING state.

  - `items.endedAt` (string, required)
    Time at which the operation completed in the SUCCEEDED or FAILED state.

  - `items.logMessages` (array, required)
    List of progress update objects, which may be empty.

  - `items.logMessages.message` (string)
    Progress update message.

  - `items.logMessages.timestamp` (string)
    Timestamp of the progress update.

  - `items.suggestedPollingIntervalSeconds` (number, required)
    Number of seconds recommended for clients to poll for updates.

  - `items.error` (object)
    Error Object which MUST be populated if the operation reaches the FAILED state.

  - `items.error.code` (string)
    Error code.

  - `items.error.message` (string)
    Error message.

  - `count` (integer, required)
    Number of items returned in the response.

  - `total` (integer, required)
    Total number of items matching the query.

  - `offset` (integer)
    Zero-based offset of the first item in the response.

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)
    Additional detailed information about the error.

  - `errorDetails.type` (string, required)
    Error type

  - `errorDetails.issues` (array, required)
    List of bad request issues

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.

  - `errorDetails.issues.subject` (string, required)
    The specific issue key. For example, if the source property is field, the subject is the dot-separated property name the issue is about

  - `errorDetails.issues.description` (string)
    A human-readable description of the issue.

## Response 429 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)
    Additional detailed information about the error.

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


