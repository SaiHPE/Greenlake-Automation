---
title: "GreenLake webhooks and events FAQ"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/guides/public/frequently_asked_questions/webhook_faq.md"
scraped_at: "2026-06-07T06:13:20.980090+00:00Z"
---

# GreenLake webhooks and events FAQ

This FAQ provides general information about webhooks and events on GreenLake cloud. See the [webhooks and events documentation](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/) or [contact HPE support](/docs/greenlake/guides/public/support/contact-us) for detailed guidance and specific queries.

The FAQ contains the following sections:

- [General overview](#general-overview)
- [Setting up webhooks](#setting-up-webhooks)
- [Security features](#security-features)
- [Event delivery and monitoring](#event-delivery-and-monitoring)
- [Event subscriptions](#event-subscriptions)
- [Operational states](#operational-states)
- [Compliance and governance](#compliance-and-governance)
- [Real-world use cases](#real-world-use-cases)
- [Limitations and future enhancements](#limitations-and-future-enhancements)
- [Documentation](#documentation)


## General overview

### What are webhooks in GreenLake?

Webhooks are automated HTTP requests that send real-time notifications
from GreenLake to a pre-configured client's external URL when
specific events occur.

### What are events in GreenLake?

Events are records that GreenLake creates when a resource has changed (like device additions). The records contain metadata and data about the change in the resource, and the events are sent by GreenLake to the webhook URL. Events enable real-time updates and integrations.

### What types of events can trigger webhooks?

Events can include actions like creating an audit log or expiring a subscription. Check the [Event catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/#event-catalog)
for the current offering.

### How are webhooks different from APIs?

Webhooks are event-driven and automatically push data to external webhook URLs
when events occur. Whereas APIs are request-driven and require users to
fetch data manually or periodically.

### What is the main purpose of webhooks in GreenLake?

To enable real-time integrations, automate workflows, and provide
instant notifications about platform events and data delivery without request.

### What is an event subscription in the context of webhooks?

An event subscription defines the type of events a webhook listens for,
such as resource creation, updates, or deletions.

## Setting up webhooks

### How do I register a webhook in GreenLake?

Go to the platform’s **Manage Workspace** section, navigate to
**Automations > Webhooks**, and fill out the required details, including the webhook URL and secret key. Read more about [registering a webhook](/docs/greenlake/services/event/public/ui#registering-a-webhook).

### Can I test a webhook after registering it?

Yes, you can use the **Test** option from the **Actions** menu in the webhook’s settings to
ensure proper configuration. Read more about [testing a webhook](/docs/greenlake/services/event/public/ui#testing-a-webhook).

### How many webhooks can I create in a single workspace?

You can create up to five webhooks per workspace.

### What is the maximum number of event subscriptions that a webhook can have?

Each webhook can have up to five event subscriptions.

### Can multiple webhooks subscribe to the same event?

Yes, different webhooks can subscribe to the same event.

## Security features

### How are webhook notifications secured?

Webhooks use the secret key and HMAC (hash-based message authentication code) SHA-256 encryption algorithm for verifying the authenticity of
the notifications (webhook payload).

### What is the role of the webhook secret?

The webhook secret is a password used to authenticate communications between GreenLake and your server. It generates an HMAC signature using the SHA-256 hashing algorithm to verify message authenticity and ensure the event hasn't been tampered with. This secret acts as a shared key between the events infrastructure and the listener, securing webhook payloads.

### Can I change the webhook secret after registration?

Yes, you can rotate or replace the webhook secret in the settings.

### What happens if a webhook fails multiple times?

The platform retries delivery up to **20 times**. On the first failure,
the webhook’s state changes to **Warning**. If all 20 retries fail,
the webhook’s state transitions to **Critical**, requiring manual
intervention.

This number may change in the future.

### Are webhook logs available for troubleshooting?

Yes, the platform provides logs of all webhook activities, including
failures and errors. These logs can be accessed in two locations:

1. **Manage Workspace > Audit Logs**
2. The **Webhook details** page


### How do I verify my webhook?

To verify your webhook, navigate to its details page. Under the
**Actions** drop-down, you will find a **Test** option that allows you to
send a sample notification to ensure that the webhook is functioning
correctly.

### What source IP addresses does GreenLake use when delivering webhook events?

All outbound traffic from GreenLake—including webhook event delivery—originates from the NAT gateway IPs of the cluster where your tenant is hosted. This applies uniformly to all services. There is no separate set of IPs specific to webhooks.

If you need to restrict inbound traffic on their firewall to only allow GreenLake webhook deliveries, you can allowlist these IPs.

The current production NAT IPs are:

- `3.143.33.158`
- `3.14.114.104`
- `3.131.230.165`
- `52.13.81.129`
- `35.155.30.112`
- `35.163.131.189`


Allowlist all IPs listed in this section to ensure uninterrupted webhook delivery.

These IPs are infrastructure-managed and may change during cluster upgrades. Before relying on this list for allowlisting, contact HPE support to obtain the current NAT egress IPs. Do the same if webhook deliveries begin failing after an infrastructure change. For a more durable and resilient security mechanism that does not depend on source IP, implement HMAC-based signature verification.

### What are the best practices for webhook security?

To enhance security, follow these best practices:

- **Rotate your webhook secret periodically,** for example, every 6–12 months or immediately if you suspect it has been compromised.
- **Restrict access** by allowing only specific IP addresses or domains to send requests to your webhook endpoint.
- **Implement rate limiting** to control request load and prevent abuse.
- **Validate HMAC signatures** to verify the authenticity and integrity of incoming payloads.


## Event delivery and monitoring

### How does GreenLake handle high event volumes?

The system queues events for delivery and batches them if necessary to
manage high volumes efficiently.

### How can I monitor the health of my webhooks?

You can monitor webhook health through the platform’s dashboard, which
shows states like "Active," "Warning," or "Critical."

### What are the retry policies for failed webhooks?

The system retries failed webhook notifications up to **20 times** over
a span of **12 hours**. The retries are spread out at progressively
increasing intervals to account for transient issues. If all retries
fail, the webhook’s state transitions to **Critical**.

### What happens to undelivered events?

Undelivered events (after 20 tries) are logged, and the event is
dropped.

This number may change in future.

### What kind of data is included in an **event** sent by webhooks?

Events include metadata about the occurrence such as type of event
(created, updated, or deleted), time of occurrence, and detailed data about
the event.

## Event subscriptions

### How do I subscribe to an event?

Before subscribing to an event, you need to have registered a webhook.

1. Go to the **[Event catalog.](/docs/greenlake/services#event-catalog)**
2. From the **Service** column, select a service. You are brought to the event catalog of that service.
3. On the navigation menu, click an event.
4. From the event reference documentation, copy the event type. The event type follows the description of the event.
5. Log in to GreenLake and navigate to your registered webhook.
6. Click **Subscribe to event.**
7. When prompted, paste the event type in to the **Event type** field.
8. Click **Subscribe to event.**


![The location of an event type in event reference documentation](/assets/event_type.4ae3e4ac75b518cbad2acdc4e7f990aae736b15859bcd2d6492f5a5b3428bcd4.28bc669c.png)

For a complete overview of managing webhooks and events through the GreenLake UI, see the [events documentation.](/docs/greenlake/services/event/public/ui)

### Can I unsubscribe from an event?

Yes, you can change the webhook settings to remove specific
subscriptions.

### How are events categorized?

Events are categorized by resource type and action type (for example, device
created or workspace updated).

## Operational states

### What are the different webhook states?

- Pending—Awaiting verification.
- Active—Operational and delivering events.
- Warning—Experiencing intermittent issues.
- Critical—Failing consistently.
- Disabled—The webhook is temporarily paused by the user to stop receiving events. When re-enabled manually, it will resume delivering events if the webhook is in an active state.


### Can I manually disable a webhook?

Yes, you can disable a webhook at any time.

### What triggers a "Warning" state?

A "Warning" state occurs if the webhook starts failing intermittently,
such as due to temporary connectivity issues.

### How do I reactivate a disabled webhook?

Simply toggle the webhook back to the **Active** state in the settings.

### Can I delete a webhook permanently?

Yes, you can delete webhooks, but you will lose all associated
configurations and logs.

## Compliance and governance

### Does the platform log all webhook activities?

Yes, an audit log records all webhook-related activities, including
creation, modification, and failures.

### How long are webhook logs retained?

Logs are retained for a predefined period (typically 30-90 days) as per
platform policies.

### Can webhook usage be audited for compliance purposes?

Yes, audit logs provide detailed records for compliance and governance
needs.

### Are webhook notifications encrypted?

Yes, webhook payloads are encrypted during transit using HTTPS.

### Can I enforce regional restrictions on webhook delivery?

Not currently, but future updates may support region-specific webhook
configurations.

## Real-world use cases

### How can webhooks be used for monitoring?

Webhooks can notify admins about critical events like device
provisioning, resource failures, or configuration changes.

### How can webhooks automate workflows?

For example, a webhook can trigger a CI/CD pipeline whenever a new
resource is created in GreenLake.

### Are webhooks suitable for real-time alerting?

Yes, they are ideal for sending instant alerts to Slack, Microsoft
Teams, or other communication tools.

## Limitations and Future Enhancements

### Are webhooks supported in all regions?

Yes, webhooks are region agnostic and can be used across all regions
supported by GreenLake.

### Is WebSocket supported for events?

Not in the current release. Future updates may include WebSocket
support.

### Can webhook payloads be customized?

No, payloads follow a predefined structure. Custom payload support may
be added in the future.

### What is the maximum payload size for a webhook?

The maximum size is typically 64Kb. Larger payloads are truncated.

### Can I subscribe to multiple events using one webhook?

Yes, you can subscribe one webhook to multiple event types as needed
within its configuration settings. The limit is five per webhook.

### Are there plans to increase the event subscription limits?

Yes, subscription limits may be expanded based on customer feedback and
platform scaling.

## Documentation

- [Event catalog](https://developer.greenlake.hpe.com/docs/greenlake/services/#event-catalog)
- [Webhook and events](https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/)