---
title: "HPE GreenLake for Webhooks"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public.md"
scraped_at: "2026-06-07T06:13:27.109290+00:00Z"
---

# HPE GreenLake for Webhooks

HPE GreenLake for Webhooks enables you to automate event-driven workflows by delivering real-time notifications to your systems. This documentation helps you understand webhook concepts and provides step-by-step guidance for implementation.

- [Overview](#overview) — A summary of HPE GreenLake webhooks, events, and how they work together.
- [Developer guide](#developer-guide) — API prerequisites, authentication, and practical examples for registering webhooks and subscribing to events.


## Overview

HPE GreenLake for Webhooks provides RESTful APIs to manage webhooks and events programmatically.

Events are actions or changes within HPE GreenLake cloud that trigger a webhook; for example, an audit log was created, or a subscription is due to expire. Webhooks deliver automated messages with event data to the webhook destination URL.

HPE GreenLake has a growing catalog of events that help you get real-time information about your HPE GreenLake infrastructure.

The documentation includes:

- [Developer guide](/docs/greenlake/services/event/public#developer-guide)— The developer guide covers the prerequisites to make API calls and step-by-step instructions on using the API to register a webhook and subscribe to an event.
- [Webhooks](/docs/greenlake/services/event/public/webhooks)— Learn more about webhooks, webhook verification, HTTPS status codes, and how to create a webhook handler.
- [Events](/docs/greenlake/services/event/public/events)— Learn about events and their structure, and how to build an event filter.
- [Manage webhooks and events in the HPE GreenLake cloud](/docs/greenlake/services/event/public/ui)— This documentation covers how to use the HPE GreenLake cloud UI to manage webhooks and events.


Further, see the [frequently asked questions.](/docs/greenlake/guides/public/frequently_asked_questions/webhook_faq)

### Webhooks and events process overview

1. Create your webhook handler. See either of the following:
  - [Configure a webhook handler](/docs/greenlake/services/event/public/webhooks#configure-a-webhook-handler)
  - [Getting started with webhooks on HPE GreenLake cloud](https://developer.hpe.com/blog/getting-started-with-the-hpe-greenlake-cloud-eventing-framework/)— An HPE Developer Community blog outlining how to configure a low-code webhook handler.
2. Register the webhook. See either of the following:
  - HPE GreenLake UI—[Registering a webhook](/docs/greenlake/services/event/public/ui#registering-a-webhook)
  - Webhook API—[Registering a webhook](/docs/greenlake/services/event/public#registering-a-new-webhook)
3. Browse the [event catalog.](/docs/greenlake/services#event-catalog)
4. Copy the **Event type.**
5. Subscribe to the event. See either of the following:
  - HPE GreenLake UI—[Subscribing to an event](/docs/greenlake/services/event/public/ui#subscribing-to-an-event)
  - Webhook API—[Subscribing to an event](/docs/greenlake/services/event/public#subscribing-to-an-event)


### Webhook integrations

The [HPE Developer Community](https://developer.hpe.com/) has blogs describing how to integrate HPE GreenLake webhooks with platforms like ServiceNow and Splunk.

- [HPE GreenLake cloud integration with ServiceNow using webhooks](https://developer.hpe.com/blog/hpe-greenlake-cloud-integration-with-servicenow-using-webhooks/)
- [No-code integration of HPE GreenLake cloud with ServiceNow](https://developer.hpe.com/blog/no-code-integration-of-hpe-greenlake-cloud-with-servicenow/)
- [Integrating HPE GreenLake webhooks with Splunk](https://developer.hpe.com/blog/integrating-hpe-greenlake-webhooks-with-splunk/)


### CloudEvents standards

Events follow the CloudEvents standard adopted by the Cloud Native Computing Foundation. This standard describes common formats for event data that provide interoperability across services, platforms, and systems. View the [CloudEvents standard](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md).

### What's new

This section outlines the most recent notable updates to the HPE GreenLake for Webhooks API.

Date: October 2025

Events can now be sent in batches.

[See more in the changelog.](/docs/greenlake/services/event/public/openapi/changelog/)

## Developer guide

The examples in this guide help you start using the Webhooks API to register a webhook and subscribe to an event.

### Prerequisites

#### Endpoints

Endpoints are the host URLs to which you will submit your API requests.

- `https://global.api.greenlake.hpe.com/`


#### URIs

Unique Resource Identifiers (URIs) are used to identify a server or resource used within the Webhook service. For example:

- `/events/v1beta1/webhooks`
- `/events/v1beta1/webhooks/{id}`
- `/events/v1beta1/webhooks/{id}/recent-deliveries`
- `/events/v1beta1/subscriptions`


#### Access and permissions

You need the correct permissions to use the HPE GreenLake Webhooks API.

| Endpoint | Permission | Resource |
|  --- | --- | --- |
| `POST /events/v1beta1/webhooks` | Create | Automations Webhook |
| `GET /events/v1beta1/webhooks` | Read | Automations Webhook |
| `GET /events/v1beta1/webhooks/{id}` | Read | Automations Webhook |
| `PATCH /events/v1beta1/webhooks/{id}` | Update | Automations Webhook |
| `DELETE /events/v1beta1/webhooks/{id}` | Delete | Automations Webhook |
| `GET /events/v1beta1/webhooks/{id}/verify` | Read | Automations Webhook |
| `GET /events/v1beta1/webhooks/{id}/recent-deliveries` | Read | Automations Webhook |
| `POST /events/v1beta1/webhooks/{id}/delivery-failures/{failureId}/retry` | Update | Automations Webhook |
| `POST /events/v1beta1/subscriptions` | Create | Automations Subscription |
| `GET /events/v1beta1/subscriptions` | Read | Automations Subscription |
| `DELETE /events/v1beta1/subscriptions` | Delete | Automations Subscription |
| `PATCH /events/v1beta1/subscriptions` | Update | Automations Subscription |


You can find out more in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html). You can:

- Find a list of preconfigured roles and the permissions they have.
- Learn how to create custom roles.
- Discover how to assign roles to users.


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as authorization bearer tokens.

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

The following sections provide guidance on using the HPE GreenLake for Webhooks API to register a new webhook, retrieve information on all webhooks, and subscribe to an event.

#### Registering a new webhook

Before registering a webhook by API, you need to create a webhook handler. While webhook verification is optional, it is enabled by default and is strongly recommended for secure communications. See either:

- [Configure a webhook handler](/docs/greenlake/services/event/public/webhooks#configure-a-webhook-handler)
- [Getting started with webhooks on HPE GreenLake cloud](https://developer.hpe.com/blog/getting-started-with-the-hpe-greenlake-cloud-eventing-framework/)


After creating your webhook handler, you can use the following endpoint to register a webhook:


```bash
POST https://global.api.greenlake.hpe.com/events/v1beta1/webhooks
```

In the request body, you must provide a name (`"name":`) and a URL to your webhook handler (`"destination":`).

Example payload:


```bash
curl -i -X POST \
  https://global.api.greenlake.hpe.com/events/v1beta1/webhooks \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Example name",
    "description": "Example description of a webhook",
    "destination": "https://example.com/new-endpoint",
    "secret": "<s3cr3tKey>"
  }'
```

Other elements of the API payload include:

- `authType`—The authentication type of the webhook. Leave blank for no authentication, or provide `OAuth` or `APIKey`.
  - `apiKey`—If you chose `APIKey` in `authType`, provide the API key in this field.
  - `clientId` and `clientSecret`—Supply the client ID and client secret if you chose `OAuth` as the authentication type.
- `secret` and `secondarySecret`—See [webhook verification](/docs/greenlake/services/event/public/webhooks#webhook-verification) for more information on validation and shared secret rotation. While webhook verification is optional and enabled by default, it is strongly recommended for secure webhook communications.
- `batching`—Set the boolean value to `true` to enable event batching. The default is `false`. For more information, see [Event batching](/docs/greenlake/services/event/public/events#event-batching).


Example response:


```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "events/webhook",
  "name": "License Notification",
  "description": "Webhook for receiving license notifications",
  "destination": "https://example.com/new-endpoint",
  "paused": false,
  "status": "ACTIVE",
  "resourceUri": "/events/v1beta1/webhooks/123e4567-e89b-12d3-a456-426614174000",
  "generation": 1,
  "hpePrincipal": "user:<opaque-global-id>",
  "createdBy": "sample.user@example.com",
  "createdAt": "2024-04-29T15:25:06.194Z",
  "updatedAt": "2024-04-29T15:25:06.194Z",
  "clientId": "0908777a-788f-45da-afb8-295c626e4d14",
  "issuerUrl": "https://example.com/new-endpoint",
  "authType": "Oauth",
  "dualSecret": false,
  "batching": false
}
```

#### Retrieving webhook details

To retrieve information on all of the registered webhooks, use the following endpoint:


```bash
GET  https://global.api.greenlake.hpe.com/events/v1beta1/webhooks
```

Example payload:


```bash
curl -i -X GET \
  https://global.api.greenlake.hpe.com/events/v1beta1/webhooks \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

The response returns an object with all of the information stored on all registered webhooks.

The response includes the webhook ID (for example, `"id": "123e4567-e89b-12d3-a456-426614174000"`), which you will use as a path parameter in the following endpoints:

- `GET /events/v1beta1/webhooks/{id}`
- `PATCH /events/v1beta1/webhooks/{id}`
- `DELETE /events/v1beta1/webhooks/{id}`


Example response:


```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "type": "events/webhook",
      "name": "License Notification",
      "description": "Webhook for receiving license notifications",
      "destination": "https://example.com/new-endpoint",
      "paused": false,
      "status": "ACTIVE",
      "stateReason": "Failure in Event Deliveries",
      "resourceUri": "/events/v1beta1/webhooks/123e4567-e89b-12d3-a456-426614174000",
      "generation": 1,
      "hpePrincipal": "user:<opaque-global-id>",
      "createdBy": "string",
      "createdAt": "2019-08-24T14:15:22Z",
      "updatedAt": "2019-08-24T14:15:22Z",
      "authType": "oauth",
      "clientId": "a822f43a-9e72-4a04-8476-ad00422b987f",
      "issuerUrl": "http://example.com",
      "dualSecret": false,
      "batching": false
    }
  ],
  "count": 0,
  "offset": 0,
  "total": 0
}
```

#### Subscribing to an event

After you register a webhook, you can subscribe to an event. To subscribe to an event, use the following endpoint:


```bash
POST https://global.api.greenlake.hpe.com/events/v1beta1/subscriptions
```

In the payload of the API call, you must provide:

- The `eventType`—You can find event types from the [Event catalog](/docs/greenlake/services#event-catalog). Event types are in the form `com.hpe.greenlake.sample-publisher.v1beta1.sample-event1`.
- The `resourceUri` for a webhook—You can use the `GET /events/v1beta1/webhooks/` or `GET /events/v1beta1/webhooks/{id}` endpoints to find a webhook's `resourceUri`.


Optionally, if the event supports it, you can provide an `eventFilter`. See [Event filtering](/docs/greenlake/services/event/public/events#event-filtering) for more information.

Example payload:


```bash
curl -i -X POST \
  https://global.api.greenlake.hpe.com/events/v1beta1/subscriptions \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -d '{
    "eventType": "Example name",
    "webhook": {"resourceUri": ""}
  }'
```

Example response:


```json
[
  {
    "id": "0908777a-788f-45da-afb8-295c626e4d14",
    "type": "events/subscription",
    "serviceManager": "00000000-0000-0000-0000-000000000000",
    "apiGroup": "Sample Publisher",
    "eventType": "com.hpe.greenlake.sample-publisher.v1beta1.sample-event1",
    "friendlyName": "Sample Event",
    "description": "Custom Role Created",
    "resourceUri": "/events/v1beta1/subscriptions/3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "webhook": {
      "resourceUri": "/events/v1beta1/webhooks/123e4567-e89b-12d3-a456-426614174000"
    },
    "hpePrincipal": "user:<opaque-global-id>",
    "createdBy": "string",
    "createdAt": "2019-08-24T14:15:22Z",
    "updatedBy": "string",
    "updatedAt": "2019-08-24T14:15:22Z",
    "generation": 1,
    "eventFilter": "createdAt lt 2021-05-12T07:20:00.00Z"
  }
]
```

### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET or PUT action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

Use the following syntax for filtering:


```bash
filter = <propertyName> <comparison operation> <literal>
```

The `GET /events/v1beta1/subscriptions` supports filtering.

- The endpoint can be filtered on the `webhookId` property.
- The endpoint supports the `eq` comparison operator. Using this comparison operator, only webhook IDs that match the literal exactly are returned.
- The `<literal>` must be a valid `webhookId`. A `webhookId` is a string, so it must be wrapped in single quotation marks, for example, `''`.


An example of a valid filter is as follows:


```bash
filter=webhookId eq '123e4567-e89b-12d3-a456-426614174000'
```

#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).