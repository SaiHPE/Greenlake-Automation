---
title: "Flex Solutions API for HPE GreenLake"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public.md"
scraped_at: "2026-06-07T05:46:10.951384+00:00Z"
---

# Flex Solutions API for HPE GreenLake

This page provides an introduction and quick start guide for the HPE Flex Solutions API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

With the HPE Flex Solutions API you can view and manage Flex orders and devices in your workspace. The API allows you to programmatically access Flex order and device data that is available through the HPE GreenLake UI.

### Features

With the HPE Flex Solutions API you can:

- View and search for Flex orders with filtering, sorting, and pagination
- Retrieve distinct transformative data for orders (for example, group by SOW ID, customer, partner)
- View and search for Flex devices with filtering, sorting, and pagination
- Retrieve individual device details by resource ID


### Use cases

- **Automated billing reconciliation:** Retrieve Flex orders and devices programmatically to reconcile billing account data with internal systems, eliminating manual data entry.
- **Fleet visibility and reporting:** Query devices across your workspace to build custom dashboards and reports that track device types, models, and billing tiers.
- **Partner order management:** Use the orders transform endpoint to aggregate order data by partner, customer, or SOW ID for partner-level reporting and analysis.


### What's new

Date: May 2026

Initial release of the HPE Flex Solutions API (`v1beta1`).

[View the changelog for more information](/docs/greenlake/services/flex/public/openapi/changelog)

### Related documentation

- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-B0DEB89D-DE1E-4DD0-AD6F-215DF213E986.html)


## Developer guide

The examples in this guide help you start using the Flex APIs to view and manage Flex orders and devices.

### Prerequisites

#### Hostname

- [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)


#### URIs

Unique Resource Identifiers (URIs) identify a server or resource used in the Flex API. A URI is a full API path ending with a specific endpoint. For example:

- `/flex/v1beta1/orders`
- `/flex/v1beta1/orders/transform`
- `/flex/v1beta1/devices`
- `/flex/v1beta1/devices/{id}`


#### Access and permissions

You need the correct permissions to use the HPE Flex Solutions APIs.

| Endpoint | Permission | Resource |
|  --- | --- | --- |
| `GET /flex/v1beta1/orders` | View | Orders |
| `GET /flex/v1beta1/orders/transform` | View | Orders |
| `GET /flex/v1beta1/devices` | View | Devices |
| `GET /flex/v1beta1/devices/{id}` | View | Devices |


:::info
Learn more about configuring roles and permissions in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html).
:::

#### Rate limits

| Description | HTTP method and path | Limit |
|  --- | --- | --- |
| Get and search for orders | `GET /flex/v1beta1/orders` | 100 requests per minute |
| Get distinct transformative data for orders | `GET /flex/v1beta1/orders/transform` | 100 requests per minute |
| Get and search for devices | `GET /flex/v1beta1/devices` | 100 requests per minute |
| Get a single device by resource ID | `GET /flex/v1beta1/devices/{id}` | 100 requests per minute |


#### Getting an access token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#generating-an-access-token)
  - [View code samples for generating an access token.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

The following examples demonstrate common usage patterns. The complete **API reference** includes additional query parameters, response schemas, error codes, and advanced filtering options.

#### Get orders

Use this `GET` API request to retrieve and search for Flex orders. You can filter, sort, and paginate the results.

Example API call:


```sh
GET 'https://us-west.api.greenlake.hpe.com/flex/v1beta1/orders?limit=2'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "3b741a59-a22b-432f-b2cf-b72cc1a04c2d",
      "createdAt": "2023-01-01T00:00:00Z",
      "updatedAt": "2023-01-01T00:00:00Z",
      "type": "flex/orders",
      "generation": 1,
      "billingAccountId": "HP-123456789",
      "sowId": "OPE-123456789",
      "billingAccountName": "Hewlett Packard Enterprise Cloud Storage",
      "orderStartDate": "2025-01-01T00:00:00Z",
      "orderEndDate": "2035-01-01T00:00:00Z",
      "customerName": "Some Company Inc.",
      "resellerName": "1st Street Resellers",
      "distributorName": "HPE Distributions",
      "partnerName": "Friendly Reseller LLC",
      "isFlexPartner": true
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

The response contains a paginated list of Flex orders, including billing account details, SOW information, customer and partner names, and order start and end dates. Use the `offset` and `limit` parameters to paginate through large result sets.

#### Get distinct transformative data for orders

Use this `GET` API request to retrieve distinct values for orders grouped by a specific field. This is useful for building filter dropdowns or aggregating data by partner, customer, or billing account.

Example API call:


```sh
GET 'https://us-west.api.greenlake.hpe.com/flex/v1beta1/orders/transform?group-by=partnerName'
```

Sample API response:


```json
{
  "items": [
    {
      "partnerName": "HPE Distributions"
    },
    {
      "partnerName": "Friendly Reseller LLC"
    }
  ],
  "count": 2,
  "offset": 0,
  "total": 2
}
```

Supported `group-by` fields: `sowId`, `customerName`, `billingAccountName`, `billingAccountId`, `partnerName`. The `partnerName` field is a unique combined set of `resellerName` and `distributorName`.

#### Get devices

Use this `GET` API request to retrieve and search for Flex devices. You can filter, sort, and paginate the results.

Example API call:


```sh
GET "https://us-west.api.greenlake.hpe.com/flex/v1beta1/devices?filter=make eq 'HPE'&limit=1"
```

Sample API response:


```json
{
  "items": [
    {
      "id": "3b741a59-a22b-432f-b2cf-b72cc1a04c2d",
      "createdAt": "2023-01-01T00:00:00Z",
      "updatedAt": "2023-01-01T00:00:00Z",
      "type": "flex/devices",
      "generation": 1,
      "macAddress": "CA:35:DC:4F:5D:FE",
      "serialNumber": "CN134FD36",
      "resourceId": "3b741a59-a22b-432f-b2cf-b72cc1a04c2d",
      "partNumber": "JK130GT",
      "name": "custom-device-name",
      "deviceType": "DHCI_STORAGE",
      "model": "HPE Compute 6030X",
      "make": "HPE",
      "billingAccountName": "Hewlett Packard Enterprises",
      "billingTier": "HPE Distributions",
      "tags": [
        {
          "name": "category1",
          "value": "value1"
        }
      ]
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

The response contains device details including MAC address, serial number, part number, device type, and associated billing information. Devices can be tagged with key-value metadata for categorization.

#### Get a specific device

Get details of a specific device by its resource ID.

Example API call:


```sh
GET 'https://us-west.api.greenlake.hpe.com/flex/v1beta1/devices/3b741a59-a22b-432f-b2cf-b72cc1a04c2d'
```

Sample API response:


```json
{
  "id": "3b741a59-a22b-432f-b2cf-b72cc1a04c2d",
  "createdAt": "2023-01-01T00:00:00Z",
  "updatedAt": "2023-01-01T00:00:00Z",
  "type": "flex/devices",
  "generation": 1,
  "macAddress": "CA:35:DC:4F:5D:FE",
  "serialNumber": "CN134FD36",
  "resourceId": "3b741a59-a22b-432f-b2cf-b72cc1a04c2d",
  "partNumber": "JK130GT",
  "name": "custom-device-name",
  "deviceType": "DHCI_STORAGE",
  "model": "HPE Compute 6030X",
  "make": "HPE",
  "billingAccountName": "Hewlett Packard Enterprises",
  "billingTier": "HPE Distributions",
  "tags": [
    {
      "name": "category1",
      "value": "value1"
    }
  ]
}
```

The response contains the full device record for the requested resource ID, including all properties from the Device schema.

### Filtering

Filters provide the ability to limit the resources returned by a REST call. When a REST call includes a filter, the GET action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query's resources are limited to results where the customer name is `Some Company Inc.`.


```sh
GET https://us-west.api.greenlake.hpe.com/flex/v1beta1/orders?filter=customerName%20eq%20%27Some%20Company%20Inc.%27
```

#### Filtering on a single property


```sh
filter = <propertyName> <comparison operation> <literal>
```

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the operation.

For orders, the following properties support filtering:

| **Filter** | **Example** | **Description** |
|  --- | --- | --- |
| id | `id eq '3b741a59-a22b-432f-b2cf-b72cc1a04c2d'` | Filters orders by their unique ID. |
| billingAccountId | `billingAccountId eq '3b741a59-a22b-432f-b2cf-b72cc1a04c2d'` | Filters orders by billing account ID. |
| sowId | `sowId eq 'OPE-0011261086'` | Filters orders by Statement of Work ID. |
| billingAccountName | `billingAccountName eq 'Hewlett Packard Enterprise Cloud Storage'` | Filters orders by billing account name. |
| customerName | `customerName eq 'Some Company Inc.'` | Filters orders by customer name. |
| resellerName | `resellerName eq '1st Street Resellers'` | Filters orders by reseller name. |
| partnerName | `partnerName eq 'Friendly Reseller LLC'` | Filters orders by partner name. |
| distributorName | `distributorName eq 'HPE Distributions'` | Filters orders by distributor name. |
| isFlexPartner | `isFlexPartner eq true` | Filters orders by Flex Partner status. |


For devices, the following properties support filtering:

| **Filter** | **Example** | **Description** |
|  --- | --- | --- |
| id | `id eq '3b741a59-a22b-432f-b2cf-b72cc1a04c2d'` | Filters devices by their unique ID. |
| macAddress | `macAddress eq 'CA:35:DC:4F:5D:FE'` | Filters devices by MAC address. |
| serialNumber | `serialNumber eq 'CN134FD36'` | Filters devices by serial number. |
| resourceId | `resourceId eq '3b741a59-a22b-432f-b2cf-b72cc1a04c2d'` | Filters devices by resource ID. |
| partNumber | `partNumber eq 'JK130GT'` | Filters devices by part number. |
| name | `name eq 'custom-device-name'` | Filters devices by name. |
| type | `type eq 'flex/devices'` | Filters devices by resource type. |
| model | `model eq 'HPE Compute 6030X'` | Filters devices by model. |
| make | `make eq 'HPE'` | Filters devices by maker. |
| billingAccountName | `billingAccountName eq 'Hewlett Packard Enterprises'` | Filters devices by billing account name. |
| billingTier | `billingTier eq 'HPE Distributions'` | Filters devices by billing tier. |


**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

Examples of operations:

| Operation | Example | Description |
|  --- | --- | --- |
| eq | `customerName eq 'Some Company Inc.'` | The property exactly matches the literal. |
| ne | `make ne 'HPE'` | The property does not equal the literal. |
| in | `billingAccountId in ('HP-APJ-999-JPN-00104', 'HP-APUS-787-EN-00100')` | The property matches one of the values in the list. |


A **literal**, for example, true, is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

The following are examples of literals.

- **String**: Anything in 'single quotes'. Reserved characters in string literals must be URL encoded.
- **Integer**: -100, -1, 0, 1, 100
- **Boolean**: true, false


#### Filtering on multiple properties

Logical operations facilitate filtering using multiple queries. Combine multiple operations using the operator `and`, for example:

**Require both (and):** `sowId eq 'OPE-0011261086' and customerName eq 'HPE Tech Care'`

#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).