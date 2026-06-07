---
title: "GET /audit-log/v2beta1/async-operations/{operation-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-async-operations/async-operations/getasyncoperationstatus.md"
scraped_at: "2026-06-07T06:16:38.707535+00:00Z"
---

# Get the status of the audit log publish operation.

This endpoint retrieves the status of an asynchronous audit log publish operation.
The operation-id is the unique identifier returned when the audit log was published.
A valid service identity token is required to access this API.

Rate limits:
- 1,000 requests per minute

Endpoint: GET /audit-log/v2beta1/async-operations/{operation-id}
Version: v2beta1
Security: Bearer

## Path parameters:

  - `operation-id` (string, required)
    The async operation id to get the status of the publish log operation.

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier for the async operation.

  - `type` (string, required)
    Type of the async operation.
    Enum: "/audit-log/async-operation"

  - `generation` (integer, required)
    The generation number of the async operation.

  - `sourceResourceUri` (string, required)
    URI reference to the resource or resource collection that initiated the operation.

  - `progressPercent` (integer, required)
    Percentage of the operation that has been completed.

  - `state` (string, required)
    State of the publish operation.
    Enum: "INITIALIZED", "RUNNING", "SUCCEEDED", "FAILED"

  - `createdAt` (string, required)
    Time at which the operation was created.

  - `updatedAt` (string, required)
    Time at which the record was last updated.

  - `startedAt` (string, required)
    Time at which the operation entered the RUNNING state.

  - `endedAt` (string, required)
    Time at which the operation completed in the SUCCEEDED or FAILED state.

  - `logMessages` (array, required)
    List of progress update objects, which may be empty.

  - `logMessages.message` (string)
    Progress update message.

  - `logMessages.timestamp` (string)
    Timestamp of the progress update.

  - `suggestedPollingIntervalSeconds` (number, required)
    Number of seconds recommended for clients to poll for updates.

  - `error` (object)
    Error Object which MUST be populated if the operation reaches the FAILED state.

  - `error.code` (string)
    Error code.

  - `error.message` (string)
    Error message.

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

## Response 404 fields (application/json):

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

  - `errorDetails.source` (string, required)
    Source of the error, typically the API group

  - `errorDetails.metadata` (object, required)
    Additional key value pairs that provide information about this error.

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


