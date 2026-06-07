---
title: "PATCH /events/v1beta1/subscriptions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-uiapi/subscriptions/updatesubscription.md"
scraped_at: "2026-06-07T06:15:27.321944+00:00Z"
---

# Update subscription with specific IDs

Update all subscription identified by the given IDs.

Endpoint: PATCH /events/v1beta1/subscriptions
Version: v1beta1
Security: Bearer

## Request fields (application/merge-patch+json):

  - `subscriptionId` (string, required)
    Subscription Id to update.

  - `eventType` (string, required)
    The type of event to subscribe. [Events Standard](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/events/)

  - `webhook` (object, required)
    A reference to a specific webhook resource, providing a link (URI) directly to the referenced webhook.

  - `webhook.resourceUri` (string, required)
    URI to the webhook

  - `eventFilter` (string)
    The filter to apply to events.

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier of the subscription.

  - `type` (string, required)
    The type of the resource.

  - `serviceManager` (string, required)
    The service manager name.

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

  - `apiGroup` (string, required)
    The name of the publisher.

  - `createdBy` (string, required)
    The user that created the subscription.

  - `createdAt` (string, required)
    The date and time the subscription is created.

  - `updatedAt` (string, required)
    The last date and time the subscription is updated.

  - `generation` (integer, required)
    Monotonically increasing update counter to track the subscription version.

  - `updatedBy` (string, required)
    The user that updated the subscription.

  - `friendlyName` (string, required)
    UI friendly title for the event Type.

  - `description` (string)
    The subscription description.

  - `eventFilter` (string)
    The filter to apply to events.

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


