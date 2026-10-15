---
title: "GET /events/v1beta1/system-webhooks"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/system-webhook-v1beta1-nbapi/webhooks/retrievewebhooks.md"
scraped_at: "2026-06-07T06:15:20.193318+00:00Z"
---

# Get all webhooks

Retrieves a list of webhooks, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.

Endpoint: GET /events/v1beta1/system-webhooks
Version: v1beta1
Security: Bearer

## Query parameters:

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 200.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the webhook.

  - `items.name` (string, required)
    The name of the webhook.

  - `items.type` (string, required)
    The type of the resource.

  - `items.destination` (string, required)
    The URL where events will be sent.

  - `items.hpePrincipal` (string, required)
    Security principal subject notation.

  - `items.resourceUri` (string, required)
    URI to the resource itself (i.e. a self link).

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.createdBy` (string, required)
    The user that created the webhook.

  - `items.createdAt` (string, required)
    The timestamp when the webhook was created.

  - `items.updatedBy` (string, required)
    The user that updated the webhook.

  - `items.updatedAt` (string, required)
    The timestamp when the webhook was last updated

  - `count` (integer, required)

  - `offset` (integer, required)

  - `total` (integer, required)

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


