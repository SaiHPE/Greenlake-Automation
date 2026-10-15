---
title: "GET /wellness/v2/async-operations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/async-operations/getallasyncoperations.md"
scraped_at: "2026-06-07T06:16:35.141589+00:00Z"
---

# Get a list of asynchronous operations

Retrieves a list of all asynchronous operations organized in descending order based on their creation time. This ensures the most recent asynchronous operations are presented first.
__Pagination__&#58; This endpoint exclusively supports cursor-based pagination. __Filtering__&#58; The following are the supported filter parameters&#58;
* state&mdash; The state filter parameter only supports the eq operator and its value should be a valid string.
* createdAt
* updatedAt
* endedAt
* startedAt

Endpoint: GET /wellness/v2/async-operations
Version: v2
Security: Bearer

## Query parameters:

  - `filter` (string)
    The filter query parameter is used to filter a set of resources. The returned set of resources matches the criteria in the filter query parameter. The value of the filter query parameter is a subset of OData V4 filter expressions consisting of simple comparison operations joined by logical operators.

  - `limit` (integer)
    Specifies the number of asynchronous operations to be returned.

  - `next` (string)
    Specifies the ID, which acts as the pagination cursor for the next page of asynchronous operations.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Primary identifier for the asynchronous operation given by the system.

  - `items.type` (string, required)
    The type of the resource.

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.createdAt` (string, required)
    The time at which this asynchronous operation is submitted.

  - `items.updatedAt` (string, required)
    The time at which this asynchronous operation is last updated.

  - `items.startedAt` (string, required)
    Time at which the operation entered the RUNNING state.

  - `items.endedAt` (string, required)
    Time at which the operation completed (entered a SUCCEEDED, FAILED, or CANCELLED state).

  - `items.sourceResourceUri` (string, required)
    URI reference to the resource that initiated the operation.

  - `items.state` (string, required)
    State of the operation.
    Enum: "INITIALIZED", "RUNNING", "PAUSED", "TIMEDOUT", "SUCCEEDED", "FAILED"

  - `items.logMessages` (any, required)

  - `items.progressPercent` (integer, required)
    Percent progress of the operation as an integer value of 0 to 100.

  - `items.error` (any, required)

  - `items.suggestedPollingIntervalSeconds` (integer)
    Number of seconds recommended for clients to poll for updates.

  - `items.timeoutMinutes` (integer)
    Number of minutes after the last update before the operation moves into the TIMEDOUT state.

  - `items.results` (any)

  - `count` (integer, required)
    Number of items (asynchronous operations) returned.

  - `next` (string, required)
    The asynchronous operation ID acts as the pagination cursor for the next page of resources.

  - `total` (integer, required)
    Total number of items (asynchronous operation) for the current filter criteria.

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
