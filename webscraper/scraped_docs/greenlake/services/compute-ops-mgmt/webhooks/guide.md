---
title: "Getting Started Guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/webhooks/guide.md"
scraped_at: "2026-06-07T05:46:07.058523+00:00Z"
---

# Getting Started Guide

This guide walks you through the process of creating a webhook and updating it with PATCH. You can also retrieve any webhook with a GET call.

## 1. Check out Prerequisites

Before creating a webhook, verify that the prerequisites are met. For more information, see [Webhook Prerequisites](/docs/greenlake/services/compute-ops-mgmt/webhooks/prereqs).

## 2. Webhook state and status

### State

State is a webhook property that can be controlled by the user and by Compute Ops Management. Compute Ops Management will not re-enable a webhook once it has been disabled, but a user can switch between the two states at any time.

| Value | Description |
|  --- | --- |
| `ENABLED` | Webhook is ready to send event payloads to the `destination` endpoint. |
| `DISABLED` | Webhook is not sending event payloads and requires a POST to `ENABLED` to start sending messages. |


### Status

Status is a webhook property that is read-only for the user. From looking at its value and the webhook `statusReason`, it is possible to understand reason for the webhook status.

| Value | Description | Sending Events |
|  --- | --- | --- |
| `PENDING` | Handshake in progress | No |
| `ACTIVE` | Webhook is acting normally, and the handshake was successful.This status is also set when a webhook recovers from `WARNING` `status` | Yes |
| `WARNING` | Recent delivery attempts failed or the initial handshake process failed. | Yes, if `state` is `ENABLED` |
| `ERROR` | Webhook was set to `DISABLED` `state` by Compute Ops Management | No |
| `DISABLED` | The webhook was set to `DISABLED` `state` by the user | No |


### Status changes

If a webhook fails to acknowledge an event five times within ten attempts, the status changes to `WARNING`.

If a webhook fails to acknowledge an event ten times in a row, the status changes to `ERROR`, and the webhook will move to the `DISABLED` `state`. When the webhook is reactivated through a PATCH request, the `state` will change to `ENABLED` and the `status` will change to `PENDING` until the handshake process completes.

If a webhook fails to acknowledge an event nine times in a row, then you need ten successful events in a row to return to `ACTIVE`.

## 3. Create a webhook

To create a webhook, send a POST request to the `/compute-ops-mgmt/v1beta1/webhooks` endpoint as specified [here](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/post_v1beta1_webhooks/). The `destination` for a webhook should be an HTTPS URL that has endpoints registered as specified in the [prerequisites](/docs/greenlake/services/compute-ops-mgmt/webhooks/prereqs#destination-endpoint-protection). A webhook can be created with a `state` of `ENABLED` or `DISABLED` depending on whether or not the handshake should occur immediately on creation. For more information about `state`, see the [API reference for webhooks](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta1_webhooks_by_id/#!c=200&path=state&t=response). The available events to filter with `eventFilter` are mentioned in [Available Resources](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources). Event filters are used to limit the kinds of event payloads to send to the registered webhook POST endpoint. More information on how `eventFilter` works can be found in [Filtering](/docs/greenlake/services/compute-ops-mgmt/webhooks/filters). More information about how the `headers` field works can be found in [Webhook Prerequisites](/docs/greenlake/services/compute-ops-mgmt/webhooks/prereqs#destination-endpoint-protection). A sample payload to register for events from all server events follows:


```json
{
    "name": "All Compute Ops Management Events",
    "destination": "https://example.com/webhookDestination",
    "state": "ENABLED",
    "eventFilter": "type eq 'compute-ops/server'",
    "headers": {
        "exampleCustomHeader": "customHeaderValue"
    }
}
```

A response sample from the POST follows: note that the acknowledgement process is still in progress as shown by `"status": "PENDING"`. Once it shows `"status": "ACTIVE"`, Compute Ops Management is able to send messages to the endpoint.


```json
{
    "name": "All Compute Ops Management events, no further filtering",
    "destination": "https://example.com/webhookDestination",
    "state": "ENABLED",
    "eventFilter": "type eq 'compute-ops/server'",
    "type": "compute-ops-mgmt/webhooks",
    "id": "12345678-9012-3456-7890-123456789012",
    "generation": 1,
    "createdAt": "2023-10-27T18:08:07.201080+00:00",
    "updatedAt": "2023-10-27T18:08:07.201080+00:00",
    "status": "PENDING",
    "statusReason": "User enabled the webhook.",
    "resourceUri": "/compute-ops-mgmt/v1beta1/webhooks/12345678-9012-3456-7890-123456789012",
    "deliveriesUri": "/compute-ops-mgmt/v1beta1/webhooks/12345678-9012-3456-7890-123456789012/deliveries"
}
```

## 4. Retrieve a webhook

A GET request sent to `/compute-ops-mgmt/v1beta1/webhooks/{webhook_id}`  as specified [here](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta1_webhooks_by_id/) will return a body that resembles the response from the POST request, shown above. For a webhook to send event payloads to the registered `destination` URL it must match the `state` and `status` requirements specified [here](#2-webhook-state-and-status).

## 5. Update a webhook

PATCH requests can be sent to `/compute-ops-mgmt/v1beta1/webhooks/{webhook_id}`. More information about this request can be found in the [API documentation](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/patch_v1beta1_webhook_by_id/). The following example shows the payload that would be sent to `/compute-ops-mgmt/v1beta1/webhooks/12345678-9012-3456-7890-123456789012` to disable the webhook created in the first step.


```json
{"state": "DISABLED"}
```

Any request that changes the state of a webhook from `DISABLED` to `ENABLED` will initiate the handshake process, even if it has succeeded in the past. At any time, a webhook can be changed between `"state": "ENABLED"` and `"state": "DISABLED"` to stop events from being delivered to its registered endpoint.

If a PATCH request updates the webhook `destination` or `headers`, the handshake will be attempted with the new URL. This is to ensure that the new URL has its endpoints set up correctly before delivering future event payloads.

## 6. Remove a webhook

Webhooks can be deleted by sending a DELETE request to `/compute-ops-mgmt/v1beta1/webhooks/{webhook_id}`. More information can be found in the [API documentation](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/delete_webhook/).