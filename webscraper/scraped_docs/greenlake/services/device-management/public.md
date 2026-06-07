---
title: "HPE GreenLake for Device Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public.md"
scraped_at: "2026-06-07T05:46:09.821360+00:00Z"
---

# HPE GreenLake for Device Management

This page provides an introduction and quick start guide for the Device Management API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

With the HPE GreenLake for Device Management API you can view, manage, and onboard devices in your workspace. The API allows you to invoke any operation or task that is available through the HPE GreenLake UI.

### Features

With the HPE GreenLake for Device Management API you can:

- Add devices to a workspace
- View devices in a workspace
- Assign devices to applications
- Remove device assignments
- Apply subscriptions to devices
- Remove subscriptions from devices
- View details of a device in a workspace


### What's new

Date: November 2025

The `GET /devices/v1/devices` and `GET /devices/v1/devices/{id}` endpoints were updated to include additional information in their responses.

[View the changelog for more information](/docs/greenlake/services/device-management/public/openapi/changelog)

#### Deprecated

The following APIs are being deprecated and removed on their end-of-life date. Use the replacement APIs.

| API | Deprecated endpoint | Deprecation date | Replacement endpoint |
|  --- | --- | --- | --- |
| Add devices | `POST /devices/v1beta1/devices` | May 5, 2025 | `POST /devices/v1/devices` |
| Update devices | `PATCH /devices/v1beta1/devices` | May 5, 2025 | `PATCH /devices/v1/devices` |
| Get devices managed in a workspace | `GET /devices/v1beta1/devices` | May 5, 2025 | `GET /devices/v1/devices` |
| Get the status of an asynchronous operation in devices | `GET /devices/v1beta1/async-operations/{id}` | May 5, 2025 | `GET /devices/v1/async-operations/{id}` |
| Get specific device information | `GET /devices/v1beta1/devices/{id}` | May 5, 2025 | `GET /devices/v1/devices/{id}` |


### Related documentation

- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-6CAED36C-0B6B-4617-BB76-C991FB453673.html)


## Developer guide

The examples in this guide help you start using the Device Management APIs to add and manage devices using this service.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API requests to. Device Management APIs use the following endpoint:

[https://global.api.greenlake.hpe.com/](https://global.api.greenlake.hpe.com/)

#### URIs

Unique Resource Identifiers (URIs) identify a server or resource used in the Device Management API. A URI is a full API path ending with a specific endpoint. For example:

- `/devices/v1/devices`
- `/devices/v1/async-operations/{id}`
- `/devices/v1/devices/{id}`


#### Access and permissions

You need the correct permissions to use the HPE GreenLake Device Management APIs.

View permissions for Devices and Subscription Service (`ccs.device-management.view`) are required to make the following Device Management API calls:

- `GET /devices/v1/devices`
- `GET /devices/v1/async-operations/{id}`
- `GET /devices/v1/devices/{id}`


Edit permissions for Devices and Subscription Service (`ccs.device-management.edit`) are required to make the following Device Management API calls:

- `POST /devices/v1/devices`
- `PATCH /devices/v1/devices`


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

The following examples demonstrate common usage patterns. The complete **API reference** includes additional query parameters, response schemas, error codes, and advanced filtering options.

#### Add devices

Use this `POST` API request to add one or more devices to a workspace.

This API request provides an asynchronous response and returns a `202 Accepted` status when input validations are successful. Use the [Get the status of an asynchronous operation in devices](#get-the-status-of-an-asynchronous-operation-in-devices) API to view the status of this asynchronous operation. The location header in the response provides the URI to be invoked for fetching progress of the subscription addition task. Example location header: `/devices/v1/async-operations/84a4e4d0-82c4-4de8-9238-69ffbcbb8ec9`.


```sh
POST https://global.api.greenlake.hpe.com/devices/v1/devices
```

The payload:


```json
{
  "network": [
    {
      "tags": {
        "property1": "{tag_value1}",
        "property2": "{tag_value2}"
      },
      "serialNumber": "{serial_number}",
      "macAddress": "{mac_address}"
    }
  ],
  "compute": [
    {
      "tags": {
        "property1": "{tag_value1}",
        "property2": "{tag_value2}"
      },
      "serialNumber": "{serial_number}",
      "partNumber": "{mac_address}"
    }
  ],
  "storage": [
    {
      "tags": {
        "property1": "{tag_value1}",
        "property2": "{tag_value2}"
      },
      "serialNumber": "{serial_number}",
      "subscriptionKey": "{subscription_key}"
    }
  ]
}
```

#### Get devices managed in a workspace

Get a list of devices managed in a workspace.


```sh
GET https://global.api.greenlake.hpe.com/devices/v1/devices
```

The following is an example of the information returned in the response:

- `id`
- `macAddress`
- `serialNumber`
- `partNumber`
- `type`
- `deviceType`
- `model`
- `region`


You can use query parameters with the **Get devices managed in a workspace** API:

- `filter`—Limit the resources operated on by an endpoint or, when used with a multiple-GET endpoint, return only the subset of resources that match the filter. View the [filtering section](#filtering) to learn more about filtering.
- `sort`—Specify the order in which to return results. The value of the sort query parameter is a comma-separated list of sort expressions.
- `limit`—Define the maximum number of records to return.


#### Get specific device information

Get details of a specific device associated with a workspace. Take the field `id` from the response of [Get devices managed in a workspace API](#get-devices-managed-in-a-workspace).


```sh
GET https://global.api.greenlake.hpe.com/devices/v1/devices/{id}
```

The following information is returned in the response:

- `id`
- `macAddress`
- `serialNumber`
- `partNumber`
- `deviceType`
- `model`
- `region`


#### Get the status of an asynchronous operation in devices

This API returns the status of the [Adding devices](#add-devices) and [updating devices](#update-devices) asynchronous API operations.


```sh
GET https://global.api.greenlake.hpe.com/devices/v1/async-operations/{id}
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


More information on this API can be found in the **API reference.**

#### Update devices

Use this `PATCH` API to update devices by passing one or more device IDs. Currently, this API supports:

- Assigning devices to an application.
- Removing devices from an application.
- Applying subscriptions to devices.
- Removing subscriptions from devices.



```sh
PATCH https://global.api.greenlake.hpe.com/devices/v1/devices?id={id}
```

The payload:


```json
{
  "subscription": [
    {
      "id": "subscription_id"
    }
  ],
  "application": {
    "id": "application_id"
  },
  "region": "region"
}
```

More information can be found in the **API reference.**

### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query's resources are limited to results where the device type is `COMPUTE`.


```sh
GET <URI>?filter=deviceType eq 'COMPUTE'
```

#### Filtering on a single property


```sh
filter = <propertyName> <comparison operation> <literal>
```

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the operation.

For example:

| **Property** | **Example** | **Description** |
|  --- | --- | --- |
| Key | `serialNumber eq 'STIQQ4L04'` | Returns results when the property, `serialNumber`, is exactly the value to the right of `eq`. |


**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

Examples of operations:

| Operation | Definition |
|  --- | --- |
| eq | The property exactly matches the literal, for example, `serialNumber eq 'STIQQ4L04'`. |
| ne | The property does not equal the literal. |
| gt | The property is greater than the integer, decimal, or timestamp literal, for example, `createdAt gt '2019-10-12T07:20:50.52934852Z'` |
| ge | The property is greater or equal to the integer, decimal, or timestamp literal. |
| lt | The property is less than the integer, decimal, or timestamp literal. |
| le | The property is less than or equal to the integer, decimal, or timestamp literal. |
| in | The property matches one of multiple values, for example, `serialNumber in ['STIQQ4L04', 'STIQQ4L05', 'STIQQ4L06']` |
| not | The property does not match any of multiple values, for example, `serialNumber not eq 'STIQQ4L04'` |


A **literal**, for example, true, is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

The following are examples of literals.

- **String**: Anything in 'single quotes'. Reserved characters in string literals must be URL encoded.
- **Integer**: -100, -1, 0, 1, 100
- **Decimal**: -3.14, -2.71, 2.71, 3.14
- **Timestamp**: 2019-10-12T07:20:50.52934852Z. The timestamp format is RFC3339.
- **Boolean**: true, false
- **Null**: null. Null is equal to itself and nothing else. Null is not greater or less than anything.


#### Filtering on multiple properties

Logical operations facilitate filtering using multiple queries. Combine multiple operations using the operator `and` or `or`, for example:

- **Require both (and):** `serialNumber eq 'STIQQ4L04' and deviceType eq 'STORAGE'`
- **Require either (or):** `serialNumber eq 'STIQQ4L04' or deviceType eq 'STORAGE'`


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).

Find more information and examples in the [API reference](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory-latest/operation/getDevicesV1/).