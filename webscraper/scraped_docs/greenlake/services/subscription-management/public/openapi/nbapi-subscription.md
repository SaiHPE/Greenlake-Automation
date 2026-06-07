---
title: "HPE GreenLake APIs for Subscription Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription.md"
scraped_at: "2026-06-07T05:46:40.085683+00:00Z"
---

# HPE GreenLake APIs for Subscription Management

With the HPE GreenLake APIs for Subscription Management you can add subscriptions, unclaim subscriptions, get subscription information, and update auto-subscription settings for your HPE GreenLake workspace.

Version: latest

## Servers

Url hostname
```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake APIs for Subscription Management](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/index.yaml)

## Subscriptions - v1

### Add subscriptions

 - [POST /subscriptions/v1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1/postsubscriptionsv1.md): Add one or more subscriptions to a workspace. NOTE: You need to have the edit  permission for the Devices and Subscription service to invoke this API.  This API provides an asynchronous response and will always  return 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to be invoked for  fetching progress of the subscription addition task. For details about  the status fetch URL, refer to the API Get progress or status of async operations in subscriptions. Rate limits are enforced on this API. Four requests per minute is supported per workspace, and the API returns a 429 status code if this threshold is breached.

### Update subscriptions

 - [PATCH /subscriptions/v1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1/patchsubscriptionsv1.md): Update subscriptions by passing one or more subscription IDs. Currently, the API supports adding and removing the tags for subscriptions.
For each tag provided in the request body:

  - Tags are created and inserted into the specified subscriptions if the provided tags do not map to null and are not already present.

  - Tags are updated with the provided if the provided tag key is already present in a subscription, but the provided value differs from the existing value.

  - Tags are removed from subscriptions when a tag key is mapped to a null tag value. The tags are removed from any subscription with a matching tag with the same key.

This API provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The location header in the response provides the URI used to fetch the progress of the subscription update task. For details about the status fetch URL, see Get progress or status of async operations in subscriptions.  Rate limits are enforced on this API. Five requests per minute are supported per workspace, and the API returns 429 if this threshold is breached.  NOTE: To call this API, you need edit permissions for the Devices and Subscription service.

### Get subscriptions of a workspace

 - [GET /subscriptions/v1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1/getsubscriptionsv1.md): Get subscriptions managed in a workspace. Filters can be passed to filter  the subscriptions based on conditional expressions.NOTE: You need to have  view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 60 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Get information on a subscription

 - [GET /subscriptions/v1/subscriptions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1/getsubscriptiondetailsbyidv1.md): Get detailed information for a single subscription by id. NOTE: You need to have the view permission of device management to invoke this API.  Rate limits are enforced on this API. 20 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Get progress or status of async operations in subscriptions

 - [GET /subscriptions/v1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1/getsubscriptionsasyncoperationresourcev1.md): Use this API to find the status of the asynchronous Add and update subscriptions API.  An asynchronous resource is  generated to track the status of an asynchronous operation. An asynchronous  resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT)  will no longer be accessible 24 hours after reaching the terminal state. An  asynchronous resource is set to the TIMEOUT state if the resource  has been in an INITIALIZED or RUNNING state for a period greater than the  timeout set. If an asynchronous operation resource coming from an asynchronous  request consists of multiple subscriptions, a breakdown of succeeded  subscriptions and failed subscriptions, if there are any, is returned  as the response. In this case, the subscription key identifies each subscription.Note: You need view permissions for the Devices and  Subscription service to invoke this API.  Rate limits are enforced on this API. 30 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

## Subscriptions - v2beta1

### Unclaim subscriptions in bulk

 - [DELETE /subscriptions/v2beta1/subscriptions/bulk](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v2beta1/deletesubscriptionsbulkv2beta1.md): Unclaim subscriptions in bulk by passing one or more subscription IDs. Note: You must have edit permission for the Devices and Subscription service to use this API. You can unclaim up to 10 subscriptions in a single request. This endpoint provides an asynchronous response and always returns 202 Accepted if basic input validation is successful. The Location header in the response contains the URI to check the progress of the unclaim task. For details about the status fetch URL, see Get progress or status of async operations in subscriptions Rate limits apply to this endpoint. If the threshold is exceeded, the API returns a 429 Too Many Requests response.

## Subscriptions - v1alpha1

### Get subscriptions of a workspace (deprecated)

 - [GET /subscriptions/v1alpha1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1alpha1/getsubscriptionsv1alpha1.md): Get subscriptions managed in a workspace. Pass filters to limit results based on conditional expressions. NOTE: You need to have the view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 40 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

## Subscriptions - v1beta1

### Add subscriptions (deprecated)

 - [POST /subscriptions/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1beta1/postsubscriptions.md): Add one or more subscriptions to a workspace. NOTE: You need to have the edit  permission for the Devices and Subscription service to invoke this API.  This API provides an asynchronous response and will always  return 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to be invoked for  fetching progress of the subscription addition task. For details about  the status fetch URL, refer to the API Get progress or status of async operations in subscriptions. Rate limits are enforced on this API. Four requests per minute is supported per workspace, and the API returns a 429 status code if this threshold is breached.

### Update subscriptions (deprecated)

 - [PATCH /subscriptions/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1beta1/patchsubscriptions.md): Update subscriptions by passing one or more subscription IDs. Currently, the API supports adding and removing the tags for subscriptions.

  For each tag provided in the request body:

  - Tags are created and inserted into the specified subscriptions if the provided tags do not map to null and are not already present.

  - Tags are updated with the provided if the provided tag key is already present in a subscription, but the provided value differs from the existing value.

  - Tags are removed from subscriptions when a tag key is mapped to a null tag value. The tags are removed from any subscription with a matching tag with the same key.

    This API provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The location header in the response provides the URI used to fetch the progress of the subscription update task. For details about the status fetch URL, see Get progress or status of async operations in subscriptions.

  Rate limits are enforced on this API. Five requests per minute are supported per workspace, and the API returns '429` if this threshold is breached.

  NOTE: To call this API, you need edit permissions for the Devices and Subscription service.

### Get subscriptions of a workspace (deprecated)

 - [GET /subscriptions/v1beta1/subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1beta1/getsubscriptionsbeta.md): Get subscriptions managed in a workspace. Filters can be passed to filter  the subscriptions based on conditional expressions.NOTE: You need to have  view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 60 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Get information on a subscription (deprecated)

 - [GET /subscriptions/v1beta1/subscriptions/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1beta1/getsubscriptiondetailsbyid.md): Get detailed information for a single subscription by id. NOTE: You need to have the view permission of device management to invoke this API.  Rate limits are enforced on this API. 20 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Get progress or status of async operations in subscriptions (deprecated)

 - [GET /subscriptions/v1beta1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/subscriptions-v1beta1/getsubscriptionsasyncoperationresource.md): Use this API to find the status of the asynchronous Add and update subscriptions API.  An asynchronous resource is  generated to track the status of an asynchronous operation. An asynchronous  resource that has reached a terminal state (SUCCEEDED, FAILED, TIMEOUT)  will no longer be accessible 24 hours after reaching the terminal state. An  asynchronous resource is set to the TIMEOUT state if the resource  has been in an INITIALIZED or RUNNING state for a period greater than the  timeout set. If an asynchronous operation resource coming from an asynchronous  request consists of multiple subscriptions, a breakdown of succeeded  subscriptions and failed subscriptions, if there are any, is returned  as the response. In this case, the subscription key identifies each subscription.Note: You need view permissions for the Devices and  Subscription service to invoke this API.  Rate limits are enforced on this API. 30 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

## Auto Subscriptions settings - v1alpha1

### Get all configured auto-subscriptions settings (deprecated)

 - [GET /subscriptions/v1alpha1/auto-subscription-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1alpha1/getautosubscriptionsv1alpha1.md): Get all configured auto-subscriptions settings in a workspace.  NOTE: You need to have the view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Get configured auto-subscriptions settings per workspace (deprecated)

 - [GET /subscriptions/v1alpha1/auto-subscription-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1alpha1/getautosubscriptionbyidv1alpha1.md): Retrieve the configured auto-subscriptions settings in a workspace.  NOTE: You need to have view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

### Update the configured auto-subscriptions settings of a workspace (deprecated)

 - [PATCH /subscriptions/v1alpha1/auto-subscription-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1alpha1/updateautosubscriptionsv1alpha1.md): Update the configured auto-subscriptions managed in a workspace.  In the payload, you can pass a list of deviceType and tier combinations to be updated or created. If the combination of deviceType and tier is already configured, it is updated. Otherwise, the combination is created. If you need to remove settings for one or more combination of deviceType and tier, pass tier as null for the required deviceType. NOTE: You need to have the edit permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

## Auto Subscriptions settings - v1

### Get all configured auto-subscriptions settings

 - [GET /subscriptions/v1/auto-subscription-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1/getautosubscriptionsv1.md): Get all configured auto-subscriptions settings in a workspace.  NOTE: You need to have the view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Get configured auto-subscriptions settings per workspace

 - [GET /subscriptions/v1/auto-subscription-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1/getautosubscriptionbyidv1.md): Retrieve the configured auto-subscriptions settings in a workspace.  NOTE: You need to have view permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

### Update the configured auto-subscriptions settings of a workspace

 - [PATCH /subscriptions/v1/auto-subscription-settings/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/auto-subscriptions-settings-v1/updateautosubscriptionsv1.md): Update the configured auto-subscriptions managed in a workspace.  In the payload, you can pass a list of deviceType and tier combinations to be updated or created. If the combination of deviceType and tier is already configured, it is updated. Otherwise, the combination is created. If you need to remove settings for one or more combination of deviceType and tier, pass tier as null for the required deviceType. NOTE: You need to have the edit permission for the Devices and subscription service to invoke this API.  Rate limits are enforced on this API. 25 requests per minute is supported per workspace. The API returns 429 if this threshold is breached.

