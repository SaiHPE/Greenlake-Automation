---
title: "GET /internal-events/v1beta1/subscriptions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-internal-api/subscriptions/getallsubscriptions.md"
scraped_at: "2026-06-07T06:15:23.313625+00:00Z"
---

# Get all subscriptions

Retrieves a list of subscriptions, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.

Endpoint: GET /internal-events/v1beta1/subscriptions
Version: v1beta1
Security: Bearer

## Query parameters:

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 200.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier of the subscription.

  - `workspaceId` (string, required)

  - `resourceUri` (string, required)
    URI to the subscription.

  - `eventType` (string, required)
    The eventType assosciated with subscriptions

  - `hpePrincipal` (string, required)
    Security principal subject notation.

  - `createdBy` (string, required)
    The user that created the subscription.

  - `createdAt` (string, required)
    The date and time the subscription is created.

  - `updatedBy` (string, required)
    The user that updated the subscription.

  - `updatedAt` (string, required)
    The last date and time the subscription is updated.

  - `generation` (integer, required)
    Monotonically increasing update counter to track the subscription version.

  - `status` (string, required)
    status of the webhook
    Enum: "enabled", "disabled"

  - `eventFilter` (string)
    The filter to apply to events. [Filtering Standard](https://developer.greenlake.hpe.com/docs/greenlake/standards/ratified/api/query_parameters/#filtering)

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    Unique identifier for the instance of this error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    Unique identifier for the instance of this error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 403 fields (application/json):

  - `errorCode` (string, required)
    Unique identifier for the instance of this error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 429 fields (application/json):

  - `errorCode` (string, required)
    Unique identifier for the instance of this error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique identifier for the instance of this error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code


