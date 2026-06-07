---
title: "POST /events/v1beta1/webhooks/{id}/verify"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhooks/webhookverification.md"
scraped_at: "2026-06-07T06:15:25.221106+00:00Z"
---

# Webhook Verification Endpoint

This endpoint is designed to ensure the webhook URL provided by the user is correct and the server is prepared to receive webhook requests.

Endpoint: POST /events/v1beta1/webhooks/{id}/verify
Version: v1beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Webhook ID

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the webhook.

  - `type` (string, required)
    The type of the resource.

  - `createdAt` (string, required)
    The timestamp when the webhook was created.

  - `updatedAt` (string, required)
    The timestamp when the webhook was last updated

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `paused` (boolean, required)
    Indicates whether the webhook is paused. false means the webhook is not paused.

  - `name` (string, required)
    The name of the webhook.

  - `destination` (string, required)
    The URL where events will be sent.

  - `hpePrincipal` (string, required)
    Security principal subject notation.

  - `authType` (string, required)
    type of authentication (oauth,apikey)

  - `clientId` (string, required)
    ClientId used for generating bearer token for verification

  - `issuerUrl` (string, required)
    The token generating url

  - `createdBy` (string, required)
    The user that created the webhook.

  - `description` (string, required)
    A brief description of the webhook.

  - `resourceUri` (string, required)
    URI to the resource itself (i.e. a self link).

  - `status` (string, required)
    Controlled by System only
    Enum: "ACTIVE", "DISABLED", "PENDING", "WARNING", "ERROR"

  - `dualSecret` (boolean, required)
    Indicates whether the webhook uses dual secret authentication.

  - `batching` (boolean, required)
    Indicates whether the webhook uses batching.

  - `challengeRequestEnabled` (boolean, required)
    If false, no challenge requests will be sent to webhook

  - `stateReason` (string)
    The reason for the current state of the webhook.

  - `endpointRateLimit` (integer,null,integer,null)
    The rate limit (requests per minute) allowed by the webhook endpoint. This value is determined during webhook verification when the endpoint responds with a WebHook-Allowed-Rate header. A value of -1 indicates unlimited rate, positive integers specify requests per minute, and null indicates no rate limit has been specified by the endpoint.

  - `destinationResponse` (object)
    The response from the destination URL.

  - `destinationResponse.statusCode` (integer)
    The HTTP status code returned by the destination.

  - `destinationResponse.message` (string)
    The message returned by the destination.

  - `destinationResponse.requestedRate` (integer,null)
    The rate of events as requested by the destination. Null if not defined.

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


