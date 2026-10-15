---
title: "PATCH /events/v1beta1/webhooks/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/updatewebhook.md"
scraped_at: "2026-06-07T06:15:23.802583+00:00Z"
---

# Update a webhook by ID

Update an existing webhook's settings, such as its name, description, destination, etc

Endpoint: PATCH /events/v1beta1/webhooks/{id}
Version: v1beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Webhook ID

## Request fields (application/merge-patch+json):

  - `name` (string)
    The name of the webhook.

  - `description` (string)
    A brief description of the webhook.

  - `destination` (string)
    The URL where events will be sent.

  - `secret` (string)
    A secret for verifying the authenticity of incoming requests.

  - `secondarySecret` (string)
    A secret for verifying the authenticity of incoming requests.

  - `paused` (boolean)
    Indicates whether the webhook is paused. false means the webhook is not paused.

  - `authType` (string)
    Authentication Type Oauth or APIKey
    Enum: "Oauth", "APIKey", ""

  - `clientId` (string)
    Client Id used for Oauth authnetication

  - `clientSecret` (string)
    Client Secret used for Oauth Authentication

  - `issuerUrl` (string)
    Token issuer endpoint

  - `apiKey` (string)
    Api Key used for authentication from client endpoint

  - `batching` (boolean)
    Indicates whether the webhook uses batching.

  - `challengeRequestEnabled` (boolean)
    If set to false, no challenge requests will be sent to webhook

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

  - `endpointRateLimit` (integer,null)
    The rate limit (requests per minute) allowed by the webhook endpoint. This value is determined during webhook verification when the endpoint responds with a WebHook-Allowed-Rate header. A value of -1 indicates unlimited rate, positive integers specify requests per minute, and null indicates no rate limit has been specified by the endpoint.

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


