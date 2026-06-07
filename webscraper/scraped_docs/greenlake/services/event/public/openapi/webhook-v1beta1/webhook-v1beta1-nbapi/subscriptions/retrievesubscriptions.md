---
title: "GET /events/v1beta1/subscriptions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/subscriptions/retrievesubscriptions.md"
scraped_at: "2026-06-07T06:15:24.648887+00:00Z"
---

# Get all subscriptions for a webhook

Retrieves a list of subscriptions associated to webhooks, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.  Filtering: Following are the supported filter parameters &#58; webhookId

Endpoint: GET /events/v1beta1/subscriptions
Version: v1beta1
Security: Bearer

## Query parameters:

  - `filter` (string, required)
    Filter subscriptions events using an OData V4 formatted filter string.

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 10.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `items` (array, required)
    An array of subscription objects, each representing a unique subscription.

  - `items.id` (string, required)
    Unique identifier of the subscription.

  - `items.type` (string, required)
    The type of the resource.

  - `items.serviceManager` (string, required)
    The service manager name.

  - `items.eventType` (string, required)
    The subscription type name.

  - `items.resourceUri` (string, required)
    URI to the subscription.

  - `items.webhook` (object, required)
    The response schema for WebhookSubscription.

  - `items.webhook.resourceUri` (string, required)
    URI to the webhook

  - `items.hpePrincipal` (string, required)
    Security principal subject notation.

  - `items.apiGroup` (string, required)
    The name of the publisher.

  - `items.createdBy` (string, required)
    The user that created the subscription.

  - `items.createdAt` (string, required)
    The date and time the subscription is created.

  - `items.updatedAt` (string, required)
    The last date and time the subscription is updated.

  - `items.generation` (integer, required)
    Monotonically increasing update counter to track the subscription version.

  - `items.updatedBy` (string, required)
    The user that updated the subscription.

  - `items.friendlyName` (string, required)
    UI friendly title for the event Type.

  - `items.description` (string)
    The subscription description.

  - `items.eventFilter` (string)
    The filter to apply to events.

  - `count` (integer, required)
    The number of subscription objects returned in the items array for the current request.

  - `offset` (integer, required)
    The zero-based index in the complete list of retrieved subscriptions that marks the beginning of the response.

  - `total` (integer, required)
    The total number of subscriptions available in the system that match the provided query or filters.

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


