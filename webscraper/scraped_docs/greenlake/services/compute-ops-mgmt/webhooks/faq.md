---
title: "Webhook FAQ"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/webhooks/faq.md"
scraped_at: "2026-06-07T06:13:25.969730+00:00Z"
---

# Webhook FAQ

## How do I disable my webhook?

Issue a `PATCH` request against your webhook, and set `state` to `DISABLED.`

The endpoint to target is: `/compute-ops-mgmt/v1beta1/webhooks/{webhook_id}`

Sample payload:


```json
{
    "state": "DISABLED"
}
```

The [Getting Started Guide](/docs/greenlake/services/compute-ops-mgmt/webhooks/guide) can also help to fill in the details.

## I'm getting too many events?

The resource types and what triggers events to be sent to the webhook are described in the [Available Resources](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources) section. One approach to resolving this issue is to study which resource type is driving the majority of the traffic, and add additional filters to slow that down. To read more about filtering, review [Webhook Filters](/docs/greenlake/services/compute-ops-mgmt/webhooks/filters).

## Why is my webhook disabled?

If a webhook fails to acknowledge an event five times within ten attempts, the status changes to `WARNING`.

If a webhook fails to acknowledge an event ten times in a row, the status changes to `ERROR`. Additionally, the webhook will move to the `DISABLED` state.

If a webhook fails to acknowledge an event nine times in a row, then you need ten successful events in a row to return to `ACTIVE` `status`.

To read about `state` and `status`, review the [Getting Started Guide](/docs/greenlake/services/compute-ops-mgmt/webhooks/guide).

## Why did I stop receiving events?

Perform a `GET` against your webhook to see what the `state` and `status` fields are. If the webhook `state` is `ENABLED` and the `status` is `WARNING` or `ERROR` review the `statusReason`.

## Is the order of events guaranteed?

The events coming to your webhook can arrive out of sequence order.

## Why isn't my webhook registering?

To understand and troubleshoot the registration process, review the handshake protocol information in the [Webhook Prerequisites page](/docs/greenlake/services/compute-ops-mgmt/webhooks/prereqs). The following Python sample shows a typical configuration.


```python
import json
import logging
from time import sleep

logger = logging.getLogger()
logger.setLevel(logging.INFO)

POST_RESPONSE = {
    "statusCode": 201,
    "body": json.dumps({}),
}

def webhook_handler(event: dict[str, Any]):
"""
    A pseudo-code function that implements two HTTP methods:
      - GET for webhook handshake validation
      - POST for no-op processing of events.

    Parameters:
       event: A simulated dictionary of data provided by the user's REST framework.
    Returns:
        dict[str, str]: A simulated dictionary for HTTP response defined by the user's REST framework.
 """

    http_method = event.get("httpMethod")
    headers = event.get("headers")
    body = event.get("body")

    # The webhook endpoint will receive a GET request that contains a header from Compute Ops Management
    #     named x-compute-ops-mgmt-verification-challenge, with a verification string as its value.
    # The endpoint must respond with a response body containing a JSON object with a key verification
    #    and a value containing the verification string from the header. The request should return with
    #    status code 200.
    if http_method == "GET":
        # This is described more in the GET endpoint details section of the Webhook Prerequisites page
        challenge = headers.get("x-compute-ops-mgmt-verification-challenge")
        response = {
            "statusCode": 200,
            "body": json.dumps({"verification": challenge}),
        }
        logger.info("Responding to GET with %s", response)

        return response

    # The POST endpoint will receive the event payloads that match the webhook eventFilter. When the webhook
    #    is in an ENABLED state with an ACTIVE status, event payloads will be delivered to the endpoint.
    elif http_method == "POST":
        if body is None:
            logger.info("Body was None")
            return POST_RESPONSE
        payload = json.loads(body)
        logger.info("Received payload: %s", payload)

        return POST_RESPONSE
    else:
        return {"statusCode": 405}
```