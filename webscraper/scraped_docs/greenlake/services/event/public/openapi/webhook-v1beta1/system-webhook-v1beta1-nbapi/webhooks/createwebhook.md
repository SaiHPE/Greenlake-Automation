---
title: "POST /events/v1beta1/system-webhooks"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/system-webhook-v1beta1-nbapi/webhooks/createwebhook.md"
scraped_at: "2026-06-07T06:15:20.101508+00:00Z"
---

# Register a new webhook

This endpoint allows clients to create a new webhook to establish a callback mechanism for key events on GLCP services.

Endpoint: POST /events/v1beta1/system-webhooks
Version: v1beta1
Security: Bearer

## Request fields (application/json):

  - `name` (string, required)
    The name of the webhook.

  - `destination` (string, required)
    The URL where events will be sent.

## Response 201 fields (application/json):

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

## Response 422 fields (application/json):

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


