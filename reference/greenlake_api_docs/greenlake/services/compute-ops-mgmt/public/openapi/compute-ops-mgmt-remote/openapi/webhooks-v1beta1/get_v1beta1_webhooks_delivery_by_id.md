---
title: "GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries/{delivery_id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/webhooks-v1beta1/get_v1beta1_webhooks_delivery_by_id.md"
scraped_at: "2026-06-07T06:14:56.276619+00:00Z"
---

# Get details for a specific delivery

Retrieve details for a specific delivery using the ID.

Endpoint: GET /compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries/{delivery_id}
Version: latest
Security: Bearer

## Path parameters:

  - `webhook_id` (string, required)
    Webhook ID

  - `delivery_id` (string, required)
    Delivery ID

## Response 200 fields (application/json):

  - `webhookId` (string)
    The ID of the webhook that this delivery request belongs to.
    Example: "75aa2a04-7349-11ee-b962-0242ac120002"

  - `id` (string)
    Unique identifier for the delivery.
    Example: "36e00ac2-16fb-4dd5-8495-7e6df82fc15e"

  - `resourceUri` (string)
    URI of the delivery itself. Used to retrieve this specific delivery resource.
    Example: "/compute-ops-mgmt/v1beta1/webhooks/96239cb5-6a1d-444c-8dfe-1e2ff05b4f05/deliveries/96239cb5-6a1d-444c-8dfe-1e2ff05b4f06"

  - `type` (string)
    The type of the delivery resource.

  - `generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `createdAt` (string)
    Time of delivery resource creation in UTC.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `updatedAt` (string)
    Time of the last delivery resource update in UTC.
    Example: "2022-03-11T01:06:30.799489+00:00"

  - `eventType` (string)
    The Compute Ops Management resource type that changed which triggered an event being sent to the webhook's endpoint. Also contains the operation taken on that resource.
    Example: "compute-ops/jobs:CREATE"

  - `eventTime` (integer)
    Timestamp from the event message that was sent to the webhook's endpoint in UTC.
    Example: "2023-11-30T15:06:01Z"

  - `requestTimestamp` (string)
    Timestamp of when the request to the webhook's endpoint was made in UTC.
    Example: "2023-10-25T15:05:02Z"

  - `responseTimestamp` (string)
    Timestamp of when the response from webhook's endpoint was received in UTC.
    Example: "2023-11-30T15:06:01Z"

  - `destination` (string)
    The webhook's destination endpoint URL where the request was sent.
    Example: "https://example.com/webhookDestination"

  - `statusCode` (string)
    HTTP status code from the webhook's registered endpoint.
    Example: 200

  - `data` (object)
    The data sent to the webhook within the POST request.

  - `attempt` (integer)
    The zero indexed count of POST attempts to the webhook's endpoint.
    Example: 1

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


