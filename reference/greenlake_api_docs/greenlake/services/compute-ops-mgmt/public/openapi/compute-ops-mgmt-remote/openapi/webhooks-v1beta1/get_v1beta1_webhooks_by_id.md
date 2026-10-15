---
title: "GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/webhooks-v1beta1/get_v1beta1_webhooks_by_id.md"
scraped_at: "2026-06-07T06:14:55.806833+00:00Z"
---

# Get a webhook

Retrieve a single webhook by webhook ID.

Endpoint: GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}
Version: latest
Security: Bearer

## Path parameters:

  - `webhook_id` (string, required)
    Webhook ID

## Response 200 fields (application/json):

  - `name` (string)
    The name associated with the webhook.
    Example: "Server Webhook"

  - `id` (string)
    Unique webhook identifier.
    Example: "36e00ac2-16fb-4dd5-8495-7e6df82fc15e"

  - `type` (string)
    The type of the resource.

  - `generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `createdAt` (string)
    Time of the webhook's creation in UTC.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `updatedAt` (string)
    Time of the webhook's last update in UTC.
    Example: "2022-03-11T01:06:30.799489+00:00"

  - `destination` (string)
    User configurable https endpoint that is able to receive HTTP GET and POST requests.
    Example: "https://example.com/webhookDestination"

  - `eventFilter` (string)
    The OData configuration of events to receive. For more information, expand the Event Webhook section and refer to Filtering.
    Example: "type eq 'compute-ops/server'"

  - `state` (string)
    The state is managed by both Compute Ops Management and the user. If the handshake fails or deliveries are consistently failing this will be set to DISABLED by the system.
* DISABLED - Set by the user to disable the endpoint without losing configuration. Additionally can be set by the System when the handshake fails or multiple 4xx/5xx responses are received. Events are not sent while in this state.
* ENABLED - Shows that the user has enabled the endpoint. Can only be set to ENABLED by the user which will cause the webhook to re-initiate the verification handshake, even if it has succeeded in the past.
    Enum: "DISABLED", "ENABLED"

  - `status` (string)
    The current status of the webhook. This status is controlled by Compute Ops Management and is read-only for the user.
* DISABLED - This is a result of the webhook's state being set to DISABLED by the user.
* ACTIVE - Acknowledgment of the endpoint has succeeded, will send any events matching the webhook's eventFilter to the destination.
* PENDING - Handshake process has begun but acknowledgement has not yet completed for the endpoint.
* WARNING - Indicates an issue with webhook communications. Either there have been multiple recent failed deliveries or the endpoint has failed the handshake. Look at the webhook's statusReason for more information.
* ERROR - Multiple 4xx or 5xx responses have been received from the endpoint. Reaching this status will disable the webhook.
    Enum: "DISABLED", "ACTIVE", "PENDING", "WARNING", "ERROR"

  - `statusReason` (string)
    A description of the last status change.
    Example: "Created"

  - `resourceUri` (string)
    The URI of this resource.
    Example: "/compute-ops-mgmt/v1beta1/webhooks/b870f080-6448-48c5-b23a-d04f2d489174"

  - `deliveriesUri` (string)
    The URI for the deliveries associated with this resource.
    Example: "/compute-ops-mgmt/v1beta1/webhooks/b870f080-6448-48c5-b23a-d04f2d489174/deliveries"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


