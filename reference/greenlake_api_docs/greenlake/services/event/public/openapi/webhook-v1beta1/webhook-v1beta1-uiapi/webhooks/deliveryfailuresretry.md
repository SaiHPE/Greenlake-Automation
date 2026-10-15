---
title: "POST /events/v1beta1/webhooks/{id}/delivery-failures/{failureId}/retry"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-uiapi/webhooks/deliveryfailuresretry.md"
scraped_at: "2026-06-07T06:15:26.373779+00:00Z"
---

# Retry webhook delivery failures

This endpoint is dedicated to retry delivery failures for a specific webhook.

Endpoint: POST /events/v1beta1/webhooks/{id}/delivery-failures/{failureId}/retry
Version: v1beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Webhook ID

  - `failureId` (string, required)
    Webhook Failure ID

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier of the delivery failure.

  - `type` (string, required)
    The type of the resource.

  - `httpResponseCode` (integer, required)
    HTTP Error Code returned by the destination

  - `resourceUri` (string, required)
    URI to the delivery failure.

  - `requestHeaders` (object, required)
    Headers included in the webhook's request.

  - `requestBody` (object, required)
    The body of the request from the webhook.

  - `responseHeaders` (object, required)
    Headers included in the webhook's response.

  - `responseBody` (string, required)
    The body of the response from the webhook.

  - `createdAt` (string, required)
    The date and time the webhook failure happened.

  - `updatedAt` (string, required)
    The timestamp when the delivery failure was last updated

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `failureId` (string, required)
    Unique identifier of the delivery failure.

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


