---
title: "Webhook Internal API - v1beta1"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-internal-api.md"
scraped_at: "2026-06-07T05:46:31.925562+00:00Z"
---

# Webhook Internal API - v1beta1

API for registering and managing HTTP webhooks and subscriptions.

Version: v1beta1
License: HPE License

## Servers

```
http://unified-events-registration-service.unified-events.svc.cluster.local:5000
```

## Security

### Bearer

Personal access token compliant with RFC8725 issued by the HPE GreenLake platform.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Webhook Internal API - v1beta1](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-internal-api.yaml)

## Webhooks

Everything about Webhooks

### Update a webhook status by ID

 - [PATCH /internal-events/v1beta1/webhooks/{webhookId}](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-internal-api/webhooks/updatewebhookstatus.md): Update an existing webhook's status

## Subscriptions

Everything about Subscriptions

### Get all subscriptions

 - [GET /internal-events/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/webhook-v1beta1/webhook-v1beta1-internal-api/subscriptions/getallsubscriptions.md): Retrieves a list of subscriptions, organized in descending order based on their creation time.  Pagination: This endpoint exclusively supports offset-based pagination.

