---
title: "HPE GreenLake for Subscription Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public.md"
scraped_at: "2026-06-07T06:13:29.553404+00:00Z"
---

# HPE GreenLake for Subscription Management

This page provides an introduction and quick start guide for the Subscription Management API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake for Subscription Management service provides:

- APIs you can use to onboard and manage subscriptions in your workspace. The API allows you to invoke any operation or task that is available through the HPE GreenLake UI.
- An event you can use to get notified of expiring subscriptions.


### Features

With HPE GreenLake for Subscription Management service you can:

- Add subscriptions to a workspace
- View subscriptions in a workspace
- View all auto-subscription settings in a workspace
- View specific auto-subscription settings in a workspace
- Get notified about expiring subscriptions


### What's new

The following table outlines the most recent changes to the Subscription Management service.

| Type | Date | Description | Changelog |
|  --- | --- | --- | --- |
| APIs | March 2025 | Two API endpoints were updated to support the `dry-run` query parameter. | [View the changelog for more information.](/docs/greenlake/services/subscription-management/public/openapi/changelog) |
| Events | September 2024 | The **Expiring Subscriptions** event was released. | [View the changelog for more information.](/docs/greenlake/services/subscription-management/public/catalog/changelog) |


#### Deprecated

The following APIs are being deprecated and removed on their end-of-life date. Use the replacement APIs.

| API | Deprecated endpoint | Deprecation date | Replacement endpoint |
|  --- | --- | --- | --- |
| Add subscriptions | `POST /subscriptions/v1beta1/subscriptions` | May 5th 2025 | `POST /subscriptions/v1/subscriptions` |
| Get the status of an asynchronous operation in subscriptions | `GET /subscriptions/v1beta1/async-operations/{id}` | May 5th 2025 | `GET /subscriptions/v1/async-operations/{id}` |
| Get subscriptions of a workspace | `GET /subscriptions/v1alpha1/subscriptions` | May 5th 2025 | `GET /subscriptions/v1/subscriptions` |
| Update Subscriptions | `PATCH /subscriptions/v1beta1/subscriptions` | May 5th 2025 | `PATCH /subscriptions/v1/subscriptions` |
| Get specific subscription information | `GET /subscriptions/v1beta1/subscriptions/{id}` | May 5th 2025 | `GET /subscriptions/v1/subscriptions/{id}` |
| Get all auto subscription settings in a workspace | `GET /subscriptions/v1alpha1/auto-subscription-settings` | May 5th 2025 | `GET /subscriptions/v1/auto-subscription-settings` |
| Get specific auto subscription settings in a workspace | `GET /subscriptions/v1alpha1/auto-subscription-settings/{resource_id}` | May 5th 2025 | `GET /subscriptions/v1/auto-subscription-settings/{resource_id}` |
| Update configured auto-subscriptions settings of a workspace | `PATCH /subscriptions/v1alpha1/auto-subscription-settings/{resource_id}` | May 5th 2025 | `PATCH /subscriptions/v1/auto-subscription-settings/{resource_id}` |


### Related documentation

- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-6CAED36C-0B6B-4617-BB76-C991FB453673.html)


## Developer guide

The examples in this guide help you start using the Subscription Management APIs to claim and check subscriptions using this service.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API requests to. Subscription Management APIs use the following endpoint:

[https://global.api.greenlake.hpe.com/](https://global.api.greenlake.hpe.com/)

#### URIs

Unique Resource Identifiers (URIs) identify a server or resource used in the Subscription Management API. A URI is a full API path ending with a specific endpoint. For example:

- `/subscriptions/v1/subscriptions`
- `/subscriptions/v1/async-operations/{id}`
- `/subscriptions/v1/auto-subscription-settings`


#### Access and permissions

You need the correct permissions to use the HPE GreenLake Subscription Management APIs.

View permissions for Devices and Subscription Service (`ccs.device-management.view`) are required to make the following Subscription Management API calls:

- `GET /subscriptions/v1/async-operations/{id}`
- `GET /subscriptions/v1/subscriptions`
- `GET /subscriptions/v1/subscriptions/{id}`
- `GET /subscriptions/v1/auto-subscription-settings`
- `GET /subscriptions/v1/auto-subscription-settings/{id}`


Edit permissions for Devices and Subscription Service (`ccs.device-management.edit`) are required to make the following Subscription Management API calls:

- `POST /subscriptions/v1/subscriptions`
- `PATCH /subscriptions/v1/auto-subscription-settings/{id}`
- `PATCH /subscriptions/v1/subscriptions`


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

The following examples demonstrate common usage patterns. The complete **API reference** includes additional query parameters, response schemas, error codes, and advanced filtering options.

#### Get subscriptions of a workspace

Review a list of the subscriptions managed in a workspace.


```bash
GET https://global.api.greenlake.hpe.com/subscriptions/v1/subscriptions
```

The following information is returned in the response:

- `id`
- `key`
- `quantity`
- `evaluationType`
- `productSku`
- `productDescription`
- `quote`
- `endUserName`
- and more


You can use query parameters with the **Get subscriptions of a workspace** API:

- `filter`—Limit the resources operated on by an endpoint or, when used with a multiple-GET endpoint, return only the subset of resources that match the filter. View the [filtering section](#filtering) to learn more about filtering.
- `sort`—Specify the order in which to return results. The value of the sort query parameter is a comma-separated list of sort expressions.
- `limit`—Define the maximum number of records to return.


#### Get specific subscription information

Retrieve details of a specific subscription associated with a workspace.


```bash
GET https://global.api.greenlake.hpe.com/subscriptions/v1/subscriptions/{id}
```

The following information is returned in the response:

- `id`
- `key`
- `quantity`
- `evaluationType`
- `productSku`
- `productDescription`
- `quote`
- and more


#### Get the status of an asynchronous operation in subscriptions

Adding subscriptions is an asynchronous operation. Use this API to find the status of the asynchronous operation.


```bash
GET https://global.api.greenlake.hpe.com/subscriptions/v1/async-operations/{id}
```

The following information is returned in the response:

- `id`
- `type`
- `status`
- `startedAt`
- `endedAt`
- `progressPercent`
- `suggestedPollingIntervalSeconds`
- `timeoutMinutes`
- `result`
- `resultType`


#### Get all auto subscription settings in a workspace

Use this `GET` API call to list the auto-subscription settings configured in a workspace. Auto-subscription settings are configured with default values when a workspace is created.


```bash
GET https://global.api.greenlake.hpe.com/subscriptions/v1/auto-subscription-settings
```

The following information is returned in the response:

- `id`
- `createdAt`
- `updatedAt`
- `generation`
- `type`
- `autoSubscriptionSettings`


NOTE: No filtering support is given for this API.

#### Get specific auto subscription settings in a workspace

Retrieve specific auto subscription settings configured in a workspace.


```bash
GET https://global.api.greenlake.hpe.com/subscriptions/v1/auto-subscription-settings/{id}
```

#### Update configured auto-subscriptions settings of a workspace

Update configured auto-subscriptions managed in a workspace. You can pass a list of `deviceType` and `tier` combinations in the payload to be updated. If the combination of `deviceType` and `tier` is already configured, it will be updated. Otherwise, that combination will be configured. If you need to remove settings for one or more combination of `deviceType` and `tier`, you need to pass `tier` as `null` for the respective `deviceType`.


```bash
PATCH https://global.api.greenlake.hpe.com/subscriptions/v1/auto-subscription-settings/{id}
```

The payload:


```json
{
  "autoSubscriptions": [
    {
      "deviceType": "{device_type}",
      "tier": "{license_tier}"
    }
  ]
}
```

#### Add subscriptions

Add one or more subscriptions to a workspace. This API provides an asynchronous response and returns `202 Accepted` when validations are successful.

The location header in the response provides the URI to be invoked for fetching progress of the subscription addition task.


```bash
POST https://global.api.greenlake.hpe.com/subscriptions/v1/subscriptions
```

The payload:


```json
{
  "subscriptions": [
    {
      "key": "{subscription_key}"
    }
  ]
}
```

### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query's resources are limited to results where the subscription type is `CENTRAL_STORAGE`.


```bash
GET <URI>?filter=subscriptionType eq 'CENTRAL_STORAGE'
```

#### Filtering on a single property


```bash
filter = <propertyName> <comparison operation> <literal>
```

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the operation. Specify nested property names with the `/` separator.

For example:

| **Property** | **Example** | **Description** |
|  --- | --- | --- |
| Key | `key eq 'STIQQ4L04'` | Returns results when the property, `key`, is exactly the value to the right of `eq`. |


**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

Examples of operations:

| Operation | Definition |
|  --- | --- |
| eq | The property exactly matches the literal, for example, `key eq 'STIQQ4L04'`. |
| ne | The property does not equal the literal. |
| gt | The property is greater than the integer, decimal, or timestamp literal, for example, `createdAt gt '2019-10-12T07:20:50.52934852Z'` |
| ge | The property is greater or equal to the integer, decimal, or timestamp literal. |
| lt | The property is less than the integer, decimal, or timestamp literal. |
| le | The property is less than or equal to the integer, decimal, or timestamp literal. |
| in | The property matches one of multiple values, for example, `key in ['STIQQ4L04', 'STIQQ4L05', 'STIQQ4L06']` |
| not | The property does not match any of multiple values, for example, `key not eq 'STIQQ4L04', 'STIQQ4L05', 'STIQQ4L06'` |


A **literal**, for example, true, is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

The following are examples of literals.

- **String**: Anything in 'single quotes'. Reserved characters in string literals must be URL encoded.
- **Integer**: -100, -1, 0, 1, 100
- **Decimal**: -3.14, -2.71, 2.71, 3.14
- **Timestamp**: 2019-10-12T07:20:50.52934852Z. The timestamp format is [RFC3339]
- **Boolean**: true, false
- **Null**: null. Null is equal to itself and nothing else. Null is not greater or less than anything.


#### Filtering on multiple properties

Logical operations facilitate filtering using multiple queries. Combine multiple operations using the operator `and` or `or`, for example:

- **Require both (and):** `key eq 'STIQQ4L04' and subscriptionType eq 'CENTRAL_STORAGE'`
- **Require either (or):** `key eq 'STIQQ4L04' or subscriptionType eq 'CENTRAL_STORAGE'`


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).