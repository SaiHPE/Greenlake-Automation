---
title: "POST Expiring Subscriptions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/catalog/subscriptions-unified-events-glcp-v1/webhooks/paths/expiring%20subscriptions/post.md"
scraped_at: "2026-06-07T06:15:52.211196+00:00Z"
---

# Expiring Subscriptions

Endpoint: POST Expiring Subscriptions
Version: 1.0.0

## Request fields (application/json):

  - `specversion` (string, required)
    The version of the CloudEvents specification the event adheres to.

  - `id` (string, required)
    The unique identifier for the event.

  - `source` (string, required)
    The source field is a URI-reference that identifies the event producer.

  - `type` (string, required)
    The type of event.

  - `subject` (string, required)

  - `data` (object, required)
    The event payload.

  - `data.key` (string)
    The subscription key.

  - `data.expiryDate` (string)
    The expiry date of the subscription.

  - `data.sku` (string)
    The stock keeping unit (SKU) associated with the subscription.

  - `data.licenseTier` (string)
    The license tier associated with the subscription.

  - `data.quantity` (integer)
    The total quantity of the subscription.

  - `data.username` (string)
    The username of the workspace associated with the subscription.

  - `data.subscriptionEndInSecs` (integer)
    The number of seconds until the subscription ends.

  - `data.subscriptionType` (string)
    The type of subscription.

  - `data.productType` (string)
    The product type of the subscription.

  - `data.platformCustomerId` (string)
    The workspace ID associated with the subscription.

  - `data.devices` (array)
    An array containing the devices associated with the subscription.

  - `data.devices.serialNumber` (string)
    The serial number of the device.

  - `data.devices.partNumber` (string)
    The part number of the device.

  - `data.devices.deviceModel` (string)
    The model number associated with the device.

  - `data.devices.macAddress` (string)
    The media access control (MAC) address is a unique identifier that identifies a device on a network.

  - `time` (string)
    The date and time the event occurred in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) format.

  - `dataschema` (string)
    A URI pointing to the data property schema.

  - `datacontenttype` (string)
    The encoding of the data in the data property in [RFC 2046](https://datatracker.ietf.org/doc/html/rfc2046) format.


