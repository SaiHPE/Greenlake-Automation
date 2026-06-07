---
title: "HPE GreenLake for Tags"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/tags/public.md"
scraped_at: "2026-06-07T05:46:14.917467+00:00Z"
---

# HPE GreenLake for Tags

This page provides an introduction and quick start guide for the Tags API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

With the HPE GreenLake for Tags APIs, you can view and filter all tags and all supported tagged resources in a workspace. A tag is a form of metadata applied to any resource and primarily used to categorize resources based on purpose, owner, environment, or other criteria. A tag is a key-value pair attached to an HPE GreenLake cloud and services resource. The API allows you to view the details of all your tags that are available through the HPE GreenLake UI.

### Features

With the HPE GreenLake for Tags APIs you can:

- View all tags in a workspace
- View all supported tagged resources in a workspace


### What's new

January 2025

New stable v1 versions of the Tags APIs released.

[Find out more in the changelog](/docs/greenlake/services/tags/public/openapi/changelog).

#### Deprecated

The following APIs are being deprecated and removed on their end-of-life date. Use the replacement APIs.

| API | Deprecated endpoint | Deprecation date | Replacement endpoint |
|  --- | --- | --- | --- |
| Get all the tagged resources for a workspace | `GET /tags/v1beta1/tags` | May 5th 2025 | `GET /tags/v1/tags` |
| Get tags associated to a workspace | `GET /tags/v1beta1/tag-resources` | May 5th 2025 | `GET /tags/v1/tag-resources` |


### Related documentation

- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-C6A8D175-2F31-45A7-A1DB-4E7BBFFDCDDF.html)


## Developer guide

The examples in this guide help you start using the Tags APIs to view and filter tags and tagged resources using this service.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API requests to. The HPE GreenLake for Tags APIs use the following endpoint:

[https://global.api.greenlake.hpe.com/](https://global.api.greenlake.hpe.com/)

#### URIs

Unique Resource Identifiers (URIs) identify a server or resource used in the Tags API. A URI is a full API path ending with a specific endpoint. For example:

- `/tags/v1/tags`
- `/tags/v1/tag-resources`


#### Access and permissions

You need the correct permissions to use the HPE GreenLake Tags APIs.

View permissions for Devices and Subscription Service (`ccs.device-management.view`) or Location Management Service (`ccs.location-management.view`) are required to make the following Tags API calls:

- `GET /tags/v1/tags`
- `GET /tags/v1/tag-resources`


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

The following examples demonstrate common usage patterns. The complete **API reference** includes additional query parameters, response schemas, error codes, and advanced filtering options.

#### Get tags of a workspace

Review a list of the tags managed in a workspace.


```sh
GET https://global.api.greenlake.hpe.com/tags/v1/tags
```

The following information is returned in the response:

- `id`
- `type`
- `key`
- `value`
- `resourceCount`
- and more


You can use query parameters with the **Get tags of a workspace** API:

- `filter`—Limit the resources operated on by an endpoint or, when used with a multiple-GET endpoint, return only the subset of resources that match the filter. View the [filtering section](#filtering) to learn more about filtering.
- `sort`—Specify the order in which to return results. The value of the sort query parameter is a comma-separated list of sort expressions.
- `limit`—Define the maximum number of records to return.


#### Get tagged resources of a workspace

Review a list of the tagged resources managed in a workspace.


```sh
GET https://global.api.greenlake.hpe.com/tags/v1/tag-resources
```

The following information is returned in the response:

- `id`
- `type`
- `resourceUri`
- `resourceType`
- `tags`
- and more


You can use query parameters with the **Get tagged resources of a workspace** API:

- `filter`—Limit the resources operated on by an endpoint or, when used with a multiple-GET endpoint, return only the subset of resources that match the filter. View the [filtering section](#filtering) to learn more about filtering.
- `sort`—Specify the order in which to return results. The value of the sort query parameter is a comma-separated list of sort expressions.
- `limit`—Define the maximum number of records to return.


### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query's resources are limited to results where the resource type is `DEVICE_SUBSCRIPTION`.


```sh
GET <URI>?filter=resourceType eq 'DEVICE_SUBSCRIPTION'
```

#### Filtering on a single property


```sh
filter = <propertyName> <comparison operation> <literal>
```

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the operation.

For example:

| **Property** | **Example** | **Description** |
|  --- | --- | --- |
| Key | `key eq 'STIQQ4L04'` | Returns results when the property, `key`, is exactly the value to the right of `eq`. |


**Operation** is the comparison operation being evaluated. Operations compare properties against literals, for example, `eq`. Currently, the operation is always in the middle part of a filter expression for this service.

Examples of operations:

| Operation | Description |
|  --- | --- |
| eq | The property exactly matches the literal, for example, `key eq 'STIQQ4L04'`. |
| ne | The property does not equal the specified literal. |
| contains() | The property contains the specified substring. For example, `contains(key,'loc')` matches keys containing "loc" such as "location" or "allocation". |


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

- **Require both (and):** `key eq 'STIQQ4L04' and value eq 'Checked'`
- **Require either (or):** `key eq 'STIQQ4L04' or id eq 'd725b07f-cc56-5923-826c-6098dd3abdba'`
- **Partial match with contains:** `contains(key,'loc') or contains(value,'loc')` matches any tag where the key or value contains the substring "loc"


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).