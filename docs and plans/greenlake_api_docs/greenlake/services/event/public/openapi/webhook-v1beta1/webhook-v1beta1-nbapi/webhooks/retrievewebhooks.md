---
title: "GET /events/v1beta1/webhooks"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/retrievewebhooks.md"
scraped_at: "2026-06-07T06:15:23.723573+00:00Z"
---

# Get all webhooks

Retrieves a list of webhooks, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.

Endpoint: GET /events/v1beta1/webhooks
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

  - `items.type` (string, required)
    The type of the resource.

  - `items.createdAt` (string, required)
    The timestamp when the webhook was created.

  - `items.updatedAt` (string, required)
    The timestamp when the webhook was last updated

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.paused` (boolean, required)
    Indicates whether the webhook is paused. false means the webhook is not paused.

  - `items.name` (string, required)
    The name of the webhook.

  - `items.destination` (string, required)
    The URL where events will be sent.

  - `items.hpePrincipal` (string, required)
    Security principal subject notation.

  - `items.authType` (string, required)
    type of authentication (oauth,apikey)

  - `items.clientId` (string, required)
    ClientId used for generating bearer token for verification

  - `items.issuerUrl` (string, required)
    The token generating url

  - `items.createdBy` (string, required)
    The user that created the webhook.

  - `items.description` (string, required)
    A brief description of the webhook.

  - `items.resourceUri` (string, required)
    URI to the resource itself (i.e. a self link).

  - `items.status` (string, required)
    Controlled by System only
    Enum: "ACTIVE", "DISABLED", "PENDING", "WARNING", "ERROR"

  - `items.dualSecret` (boolean, required)
    Indicates whether the webhook uses dual secret authentication.

  - `items.batching` (boolean, required)
    Indicates whether the webhook uses batching.

  - `items.challengeRequestEnabled` (boolean, required)
    If false, no challenge requests will be sent to webhook

  - `items.stateReason` (string)
    The reason for the current state of the webhook.

  - `items.endpointRateLimit` (integer,null)
    The rate limit (requests per minute) allowed by the webhook endpoint. This value is determined during webhook verification when the endpoint responds with a WebHook-Allowed-Rate header. A value of -1 indicates unlimited rate, positive integers specify requests per minute, and null indicates no rate limit has been specified by the endpoint.

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


