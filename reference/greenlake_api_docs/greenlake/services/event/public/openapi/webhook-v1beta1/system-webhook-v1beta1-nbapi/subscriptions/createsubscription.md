---
title: "POST /events/v1beta1/system-subscriptions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/system-webhook-v1beta1-nbapi/subscriptions/createsubscription.md"
scraped_at: "2026-06-07T06:15:20.255119+00:00Z"
---

# Create a new subscription

Register a new subscription to start receiving event notifications through the configured webhook

Endpoint: POST /events/v1beta1/system-subscriptions
Version: v1beta1
Security: Bearer

## Request fields (application/json):

  - `eventType` (string, required)
    The type of event to subscribe. [Events Standard](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/events/)

  - `webhook` (object, required)
    A reference to a specific webhook resource, providing a link (URI) directly to the referenced webhook.

  - `webhook.resourceUri` (string, required)
    URI to the webhook

## Response 201 fields (application/json):

  - `id` (string, required)
    Unique identifier of the subscription.

  - `type` (string, required)
    The type of the resource.

  - `eventType` (string, required)
    The subscription type name.

  - `resourceUri` (string, required)
    URI to the subscription.

  - `webhook` (object, required)
    The response schema for WebhookSubscription.

  - `webhook.resourceUri` (string, required)
    URI to the webhook

  - `hpePrincipal` (string, required)
    Security principal subject notation.

  - `generation` (integer, required)
    Monotonically increasing update counter to track the subscription version.

  - `createdBy` (string, required)
    The user that created the subscription.

  - `createdAt` (string, required)
    The date and time the subscription is created.

  - `updatedAt` (string, required)
    The last date and time the subscription is updated.

  - `updatedBy` (string, required)
    The user that updated the subscription.

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


