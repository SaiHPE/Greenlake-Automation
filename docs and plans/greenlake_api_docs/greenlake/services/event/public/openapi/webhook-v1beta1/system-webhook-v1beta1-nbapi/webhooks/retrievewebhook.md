---
title: "GET /events/v1beta1/system-webhooks/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/system-webhook-v1beta1-nbapi/webhooks/retrievewebhook.md"
scraped_at: "2026-06-07T06:15:20.196545+00:00Z"
---

# Get a webhook by ID

Retrieve detailed information about a specific webhook by its unique identifier

Endpoint: GET /events/v1beta1/system-webhooks/{id}
Version: v1beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Webhook ID

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the webhook.

  - `name` (string, required)
    The name of the webhook.

  - `type` (string, required)
    The type of the resource.

  - `destination` (string, required)
    The URL where events will be sent.

  - `hpePrincipal` (string, required)
    Security principal subject notation.

  - `resourceUri` (string, required)
    URI to the resource itself (i.e. a self link).

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `createdBy` (string, required)
    The user that created the webhook.

  - `createdAt` (string, required)
    The timestamp when the webhook was created.

  - `updatedBy` (string, required)
    The user that updated the webhook.

  - `updatedAt` (string, required)
    The timestamp when the webhook was last updated

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

## Response 404 fields (application/json):

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


