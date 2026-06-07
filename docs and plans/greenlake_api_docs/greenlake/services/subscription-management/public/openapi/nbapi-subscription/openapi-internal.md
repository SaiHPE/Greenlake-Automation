---
title: "HPE GreenLake Internal APIs for Subscription Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal.md"
scraped_at: "2026-06-07T06:13:40.509413+00:00Z"
---

# HPE GreenLake Internal APIs for Subscription Management

With the HPE GreenLake for Subscription Management you can add subscriptions, get subscription information, and update auto-subscription settings. The internal API is for HPE-authorized audiences only.

Version: latest

## Servers

URL hostname
```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake Internal APIs for Subscription Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal.yaml)

## Subscriptions - v1

### Add subscriptions

 - [POST /subscriptions/v1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/postsubscriptionsv1.md): Add one or more subscriptions to a workspace. NOTE: You need to have the edit  permission for the Devices and Subscription service to invoke this API endpoint.  This API endpoint provides an asynchronous response and will always  return 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to be invoked for  fetching progress of the subscription addition task. For details about  the status fetch URL, see Get progress or status of async operations in subscriptions. Rate limits are enforced. Four requests per minute are supported per workspace, and the API endpoint returns a 429 status code if this threshold is breached.

### Update subscriptions

 - [PATCH /subscriptions/v1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/patchsubscriptionsv1.md): Update subscriptions by passing one or more subscription IDs. Currently, the API endpoint supports adding and removing the tags for subscriptions.
For each tag provided in the request body:

  - Tags are created and inserted into the specified subscriptions if the provided tags do not map to null and are not already present.

  - Tags are updated with the provided if the provided tag key is already present in a subscription, but the provided value differs from the existing value.

  - Tags are removed from subscriptions when a tag key is mapped to a null tag value. The tags are removed from any subscription with a matching tag with the same key.

This API endpoint provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The location header in the response provides the URI used to fetch the progress of the subscription update task. For details about the status fetch URL, see Get progress or status of async operations in subscriptions.  Rate limits are enforced. Five requests per minute are supported per workspace, and the API endpoint returns 429 if this threshold is breached.  NOTE: To call this API, you need edit permissions for the Devices and Subscription service.

### Get subscriptions of a workspace

 - [GET /subscriptions/v1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/getsubscriptionsv1.md): Get subscriptions managed in a workspace. Filters can be passed to filter  the subscriptions based on conditional expressions.NOTE: You need to have  view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API endpoint, and 60 requests per minute are supported per workspace. The API endpoint will result in 429 if this threshold is breached.

### Get information on a subscription

 - [GET /subscriptions/v1/subscriptions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/getsubscriptiondetailsbyidv1.md): Get detailed information for a single subscription by id. NOTE: You need to have the view permission of device management to invoke this API.  Rate limits are enforced, and 20 requests per minute are supported per workspace. The API endpoint returns 429 if this threshold is breached.

### Unclaim subscription

 - [DELETE /subscriptions/v1/subscriptions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/unclaimsubscriptionbyid.md): Unclaim a subscription by its resource ID.

### Get progress or status of async operations in subscriptions

 - [GET /subscriptions/v1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v1/getsubscriptionsasyncoperationresourcev1.md): Use this API call to find the status of the asynchronous add and update subscriptions API calls.  An asynchronous resource is  generated to track the status of an asynchronous operation. An asynchronous  resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT)  will no longer be accessible 24 hours after reaching the terminal state. An  asynchronous resource is set to the TIMEOUT state if the resource  has been in an INITIALIZED or RUNNING state for a period greater than the  timeout set. If an asynchronous operation resource coming from an asynchronous  request consists of multiple subscriptions, a breakdown of succeeded  subscriptions and failed subscriptions, if there are any, is returned  as the response. In this case, the subscription key identifies each subscription.Note: You need view permissions for the Devices and  Subscription service to invoke this API endpoint.  Rate limits are enforced on this API endpoint, and 30 requests per minute are supported per workspace. The API endpoint returns 429 if this threshold is breached.

## Subscriptions - v2beta1

### Get subscription pre-claim information

 - [GET /subscriptions/v2beta1/{subscription-key}/preclaim](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/subscriptions-v2beta1/paths/~1subscriptions~1v2beta1~1%7Bsubscription-key%7D~1preclaim/get.md): Fetches pre-claim information for a subscription using the subscription key.  It provides details necessary for claiming a subscription, such as the subscription's status and associated resources.  NOTE: You need to have the view permission for the Devices and Subscription service to invoke this API endpoint.

## Internal subscriptions - v1

### Retrieve subscription data grouped by subscription tier or device type

 - [GET /internal-subscriptions/v1/subscriptions/group](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1/getsubscriptionsgroupbyv1.md): Fetch subscription data grouped by subscription tier or device type within a workspace. This API allows users to organize subscriptions based on the provided grouping criteria.

## Internal subscriptions - v1alpha1

### Count Subscriptions

 - [POST /internal-subscriptions/v1alpha1/subscriptions/count](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1alpha1/countsubscriptionsv1alpha1.md): Provides a count of subscriptions that match the specified search criteria.

### Search Subscriptions

 - [POST /internal-subscriptions/v1alpha1/subscriptions/search](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1alpha1/searchsubscriptionsv1alpha1.md): Search for subscriptions based on the provided criteria and returns a paginated list.

### Auto-complete subscription information

 - [POST /internal-subscriptions/v1alpha1/subscriptions/auto-complete](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1alpha1/autocompletedevicesv1alpha1.md): Returns auto-completion suggestions for a given prefix or query.

