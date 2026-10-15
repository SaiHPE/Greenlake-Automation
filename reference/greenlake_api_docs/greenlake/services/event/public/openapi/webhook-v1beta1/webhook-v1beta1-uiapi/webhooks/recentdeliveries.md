---
title: "GET /events/v1beta1/webhooks/{id}/recent-deliveries"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-uiapi/webhooks/recentdeliveries.md"
scraped_at: "2026-06-07T06:15:26.360328+00:00Z"
---

# Fetch recent webhook deliveries

This endpoint is dedicated to retrieve detailed information about recent deliveries for a specific webhook.

Endpoint: GET /events/v1beta1/webhooks/{id}/recent-deliveries
Version: v1beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Webhook ID

## Query parameters:

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 200.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `items` (array, required)
    An array of failure response objects that detail each failed delivery attempt associated with a specific webhook.

  - `items.id` (string, required)
    Unique identifier of the delivery. For batch deliveries, this is the batch ID; for single deliveries, the cloudevent ID.

  - `items.type` (string, required)
    The type of the resource.

  - `items.httpResponseCode` (integer, required)
    HTTP Error Code returned by the destination

  - `items.createdAt` (string, required)
    The date and time the webhook delivery happened.

  - `items.requestHeaders` (object, required)
    Headers included in the webhook's request.

  - `items.requestBody` (object, required)
    A single object payload.

  - `items.responseBody` (string, required)
    The body of the response from the webhook.

  - `items.status` (string, required)
    Controlled by System only
    Enum: "SUCCESS", "FAILURE"

  - `items.retryStatus` (string, required)
    Indicates whether the delivery can be retried
    Enum: "NORETRY", "RETRY"

  - `items.updatedAt` (string, required)
    The timestamp when the delivery was last updated

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.description` (string, required)
    Human-readable description of the delivery. For single event deliveries, this is the event type. For batch deliveries, this is a string like "Batch of 10 events".

  - `items.resourceUri` (string)
    URI to the delivery failure.

  - `items.responseHeaders` (object)
    Headers included in the webhook's response.

  - `items.subject` (string)
    The cloud event subject.

  - `items.failureId` (string)
    Unique identifier of the delivery failure.

  - `count` (integer, required)
    The number of failure response objects contained in the items array for the current response.

  - `offset` (integer, required)
    The zero-based index in the complete list of failures that marks the start of the current set of data.

  - `total` (integer, required)
    The total number of delivery failures recorded in the system that match the provided query or filters.

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


