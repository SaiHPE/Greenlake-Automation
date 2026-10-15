---
title: "GET /wellness/v2/async-operations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/async-operations/getasyncoperation.md"
scraped_at: "2026-06-07T06:16:34.218479+00:00Z"
---

# Get asynchronous operation details

Retrieves asynchronous operation details identified with a specific ID.

Endpoint: GET /wellness/v2/async-operations/{id}
Version: v2
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The asynchronous operation id returned in an ansychronous API response.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the asynchronous operation given by the system.

  - `type` (string, required)
    The type of the resource.

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `createdAt` (string, required)
    The time at which this asynchronous operation is submitted.

  - `updatedAt` (string, required)
    The time at which this asynchronous operation is last updated.

  - `startedAt` (string, required)
    Time at which the operation entered the RUNNING state.

  - `endedAt` (string, required)
    Time at which the operation completed (entered a SUCCEEDED, FAILED, or CANCELLED state).

  - `sourceResourceUri` (string, required)
    URI reference to the resource that initiated the operation.

  - `state` (string, required)
    State of the operation.
    Enum: "INITIALIZED", "RUNNING", "PAUSED", "TIMEDOUT", "SUCCEEDED", "FAILED"

  - `logMessages` (any, required)

  - `progressPercent` (integer, required)
    Percent progress of the operation as an integer value of 0 to 100.

  - `error` (any, required)

  - `suggestedPollingIntervalSeconds` (integer)
    Number of seconds recommended for clients to poll for updates.

  - `timeoutMinutes` (integer)
    Number of minutes after the last update before the operation moves into the TIMEDOUT state.

  - `results` (any)

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 404 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code


## Response 429 fields
