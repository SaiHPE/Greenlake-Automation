---
title: "GET /events/v1beta1/service-managers/{serviceManagerId}/api-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-uiapi/subscriptions/getapigroups.md"
scraped_at: "2026-06-07T06:15:26.753597+00:00Z"
---

# Get API Groups for a specific Service Manager

Endpoint: GET /events/v1beta1/service-managers/{serviceManagerId}/api-groups
Version: v1beta1
Security: Bearer

## Path parameters:

  - `serviceManagerId` (string, required)
    ID of the Service Manager

## Query parameters:

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 200.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the API Group

  - `items.name` (string, required)
    The name of the API Group

  - `items.type` (string, required)
    The type of the resource.

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.createdAt` (string, required)
    The date and time the ApiGroup created.

  - `items.updatedAt` (string, required)
    The timestamp when the ApiGroup was last updated

  - `count` (integer, required)

  - `offset` (integer, required)

  - `total` (integer, required)

## Response 404 fields (application/json):

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


