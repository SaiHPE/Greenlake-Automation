---
title: "Webhook API - v1beta1"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi.md"
scraped_at: "2026-06-07T05:46:32.169921+00:00Z"
---

# Webhook API - v1beta1

API for registering and managing HTTP webhooks and subscriptions.

Version: v1beta1
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Personal access token compliant with RFC8725 issued by the HPE GreenLake platform.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Webhook API - v1beta1](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi.yaml)

## Webhooks

Everything about Webhooks

### Register a new webhook

 - [POST /events/v1beta1/webhooks](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/createwebhook.md): This endpoint allows clients to create a new webhook to establish a callback mechanism for key events on GLCP services.

### Get all webhooks

 - [GET /events/v1beta1/webhooks](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/retrievewebhooks.md): Retrieves a list of webhooks, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.

### Get a webhook by ID

 - [GET /events/v1beta1/webhooks/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/retrievewebhook.md): Retrieve detailed information about a specific webhook by its unique identifier

### Update a webhook by ID

 - [PATCH /events/v1beta1/webhooks/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/updatewebhook.md): Update an existing webhook's settings, such as its name, description, destination, etc

### Delete a webhook by ID

 - [DELETE /events/v1beta1/webhooks/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/deletewebhook.md): Remove a specific webhook from the system

### Webhook Verification Endpoint

 - [POST /events/v1beta1/webhooks/{id}/verify](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/webhookverification.md): This endpoint is designed to ensure the webhook URL provided by the user is correct and the server is prepared to receive webhook requests.

### Fetch recent webhook deliveries

 - [GET /events/v1beta1/webhooks/{id}/recent-deliveries](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/recentdeliveries.md): This endpoint is dedicated to retrieve detailed information about recent deliveries for a specific webhook.

### Retry webhook delivery failures

 - [POST /events/v1beta1/webhooks/{id}/delivery-failures/{failureId}/retry](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/webhooks/deliveryfailuresretry.md): This endpoint is dedicated to retry delivery failures for a specific webhook.

## Subscriptions

Everything about Subscriptions

### Create a new subscription

 - [POST /events/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/subscriptions/createsubscription.md): Register a new subscription to start receiving event notifications through the configured webhook

### Get all subscriptions for a webhook

 - [GET /events/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/subscriptions/retrievesubscriptions.md): Retrieves a list of subscriptions associated to webhooks, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.  Filtering: Following are the supported filter parameters &#58; webhookId

### Delete subscription for a webhook

 - [DELETE /events/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/subscriptions/deletesubscription.md): Delete the list of subscriptions by the IDs, stopping further event notification linked to the subscriptions

### Update subscription with specific IDs

 - [PATCH /events/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-nbapi/subscriptions/updatesubscription.md): Update all subscription identified by the given IDs.

