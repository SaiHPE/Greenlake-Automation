---
title: "Webhooks Prerequisites"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/webhooks/prereqs.md"
scraped_at: "2026-06-07T06:13:26.043742+00:00Z"
---

# Webhooks Prerequisites

## Endpoint registration

In order for a webhook to deliver events, you must set up an ingest router which is capable of responding to GET and POST requests from Compute Ops Management. The webhook `destination` must point to your ingest router to allow for the setup handshake process and the continuing delivery of events. Further implementation details of this endpoint and recommended configuration are described on this page.

## Destination endpoint protection

In order to ensure that only Compute Ops Management is able to make requests to your destination, HPE recommends that you add an authentication scheme to your destination and configure your webhook to comply with that scheme. Webhooks in Compute Ops Management support any authentication scheme which can be implemented solely with the `headers` field, such as HTTP Basic Authentication or specifying API keys. When sending events to the configured destination, Compute Ops Management will send all headers specified in the configured `headers` field of the webhook in the request to the destination. All headers configured on webhooks are stored securely within Compute Ops Management, and cannot be read once set.

### Headers

For security, origin purposes, or any other reason you might have, it is possible to include additional headers. Any headers that are added to a webhook [using the headers field](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/post_v1beta1_webhooks/#tag/webhooks-v1beta1/operation/post_v1beta1_webhooks!path=headers&t=request) will be sent with any calls that the webhook makes to the registered endpoint.

You are not required to insert additional headers when creating or updating a webhook. In the case that no headers are needed, explicitly set the `headers` field to `{}` during creation.

Compute Ops Management reserves any headers that begin with `x-compute-ops-mgmt` and will deny your request if you attempt to use them as a key value in the `headers` field. For example, `x-compute-ops-mgmt-verification-challenge`. This is a header that Compute Ops Management will automatically insert for all calls to the webhook `GET` endpoint for verification purposes.

### HTTPS

Your ingest router must use a URL prefixed with `https://`. HTTP destinations are not supported.

### Certificate

Your ingest router must use a publicly signed certificate.

## Webhook GET endpoint

### Handshake protocol

The handshake process will occur using the registered GET endpoint when a webhook is set to `"state": "ENABLED"`, either through initial creation or through a PATCH call to update a disabled webhook. The following example shows the process that a webhook will go through before delivering event payloads:

1. A webhook is registered or is updated with a PATCH request to `"state": "ENABLED"`
2. Compute Ops Management calls the GET endpoint at the webhook URL, and the call contains a verification header
3. The GET endpoint responds with the verification header value in the body
4. Compute Ops Management sets the webhook to `"status": "ACTIVE"`


When all of the above steps are successful, any event payloads matching the webhook `eventFilter` are sent to the POST endpoint at the registered URL.

### GET endpoint details

The webhook endpoint will receive a GET request that contains a header from Compute Ops Management named `x-compute-ops-mgmt-verification-challenge`, with a verification string as its value. The endpoint must respond with a response body containing a JSON object with a key `verification` and a value containing the verification string from the header. The request should return with status code 200.

Example header contained in the Compute Ops Management request:


```json
{"x-compute-ops-mgmt-verification-challenge": "headerValue"}
```

Example response with a status code of 200 and body:


```json
{"verification": "headerValue"}
```

If the GET endpoint does not respond with the correct body, or it returns a non-200 status code, the webhook will transition to `"state": "DISABLED"` and `"status": "WARNING"`. While in this state, the webhook will not send any event payloads to the configured destination. The webhook must be updated to `"state": "ENABLED"` in order to re-trigger the handshake process.

### Webhook POST endpoint

The POST endpoint will receive the event payloads that match the webhook `eventFilter`. When the webhook is in an `ENABLED` state with an `ACTIVE` status, event payloads will be delivered to the endpoint. This endpoint must respond with a successful `2xx` HTTP status code for Compute Ops Management to know the event was successfully delivered.

## Rate limiting

Requests to enable a webhook through creation or modification cannot exceed 5 attempts in the last 15 minutes. If there are more than 5 attempts, any further attempts to enable a webhook return an HTTP status of 429. Up to 25 registered webhooks are supported per Compute Ops Management account per region and they can point to the same or different endpoints.