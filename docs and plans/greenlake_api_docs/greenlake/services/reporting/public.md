---
title: "HPE GreenLake for Reporting"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public.md"
scraped_at: "2026-06-07T06:13:28.789122+00:00Z"
---

# HPE GreenLake for Reporting

This guide provides comprehensive information about the HPE GreenLake for Reporting API.

- [Overview](#overview)—Learn about HPE GreenLake for Reporting API and the key features for generating and managing reports.
- [Developer guide](#developer-guide)—Get started with the Reporting API by exploring prerequisites, endpoints, authentication, and typical API workflows.


## Overview

HPE GreenLake for Reporting provides access to reports on your HPE GreenLake cloud workspace in an efficient and programmatic way. Use the reports to manage, monitor, and make data-backed insights related to your HPE workspaces, devices, and subscriptions. The APIs also allow you to get the statuses of reports.

### Features

- **Generate reports**—Generate reports across a variety of supported report types.
- **Customizable reports**—Tailor reports to suit your needs by specifying columns, date ranges, filters, and more.
- **Asynchronous operation**—The HPE GreenLake for Reporting API provides an asynchronous API, allowing you to submit requests and continue with other tasks while the reports are being generated in the background. Further, APIs are provided to help you track the status of report generation.


### What's new

Date: 2026-04-30

The `v1alpha1` Reporting endpoints have reached end of life and are no longer available. The deprecation period began on 2025-03-12. Those paths are no longer available. Use the stable `v1` endpoints.

The alpha `GET /reporting/v1alpha1/fixed-filters` endpoint has also been removed; filter and column options for exports are provided through [GET report exports metadata](#get-report-exports-metadata) (`GET /reporting/v1/report-exports-metadata`).

[View the Changelog for more information](/docs/greenlake/services/reporting/public/openapi/changelog).

Date: 2025-03-12

New stable version `v1` released.

[View the Changelog for more information](/docs/greenlake/services/reporting/public/openapi/changelog).

## Developer guide

The examples in this guide help you start using the Reporting APIs to check the status of reports using this service.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API request to. Reporting APIs use the following endpoint:

[https://global.api.greenlake.hpe.com/](https://global.api.greenlake.hpe.com/)

#### V1 version (v1)

The Reporting REST API is stable at `v1`. URIs are full paths to a resource, for example:

- `/reporting/v1/report-exports-metadata`
- `/reporting/v1/report-exports`
- `/reporting/v1/async-operations/{id}`
- `/reporting/v1/statuses/{id}`
- `/reporting/v1/statuses`


#### Access and permissions

You need the correct permissions to use the HPE GreenLake Reporting APIs.

View permission for an HPE GreenLake cloud workspace (`ccs.accounts.platform.customer.view`) is sufficient to make the following API calls:

- `GET /reporting/v1/report-exports-metadata`
- `GET /reporting/v1/async-operations/{id}`
- `GET /reporting/v1/statuses/{id}`
- `GET /reporting/v1/statuses`


Edit permissions are required to make the following API call:

- `POST /reporting/v1/report-exports`


Find out more about Roles & Permissions in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html).

#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

A typical HPE GreenLake for Reporting API workflow:

1. To determine what data to report on, call the [GET Report exports metadata](#get-report-exports-metadata).
2. Use the [POST Report exports](#post-report-exports) to generate your report, using the columns, filter criteria, and supported operators returned in step 1. Make a note of the report identifier returned in the API response.
3. Check the status of the asynchronous API call with the [GET Get report status by ID](#get-report-status-by-id) endpoint.
4. View the report with the URI returned in [GET asynchronous operation details](#get-asynchronous-operation-details).


If you configure the recipient email address, the report is emailed to the listed recipient.

#### GET report exports metadata

This API returns a list of all the data available for reporting, including:

- The supported columns.
- The data types that each column contains.
- The filter criteria that can be used.
- The supported filtering operators.


The data available to report on depends on the configuration of your HPE GreenLake workspace.

Calling this API helps you structure your call to the [POST report exports](#post-report-exports) endpoint.


```bash
GET /reporting/v1/report-exports-metadata
```

Example response.


```json
            {
              "items": [
                  {
                      "id": "SUBSCRIPTION",
                      "kind": "REPORT.EXPORTS.METADATA",
                      "type": "subscription",
                      "columns": [
                          {
                              "displayName": "Subscription Key",
                              "name": "SUBSCRIPTION_KEY",
                              "dataType": "string"
                          },
                          {
                              "displayName": "Subscription Type",
                              "name": "SUBSCRIPTION_TYPE",
                              "dataType": "string"
                          },
                          {
                              "displayName": "Subscription Tier Description",
                              "name": "SUBSCRIPTION_TIER_DESCRIPTION",
                              "dataType": "string"
                          },
                          {
                              "displayName": "Available Quantity",
                              "name": "AVAILABLE_QUANTITY",
                              "dataType": "integer"
                          }
                      ],
                      "filterCriteria": [
                          {
                              "name": "product_type",
                              "dataType": "string",
                              "supportedOperators": ["EQ"]
                          },
                          {
                              "name": "sort_by",
                              "dataType": "string",
                              "supportedOperators": ["EQ"]
                          }
                      ]
                  },
                  {
                      "id": "UID_DEVICE_INVENTORY",
                      "kind": "REPORT.EXPORTS.METADATA",
                      "type": "device_inventory",
                      "columns": [
                          {
                              "displayName": "Serial Number",
                              "name": "SERIAL_NUMBER",
                              "dataType": "string"
                          },
                          {
                              "displayName": "Device Model",
                              "name": "DEVICE_MODEL",
                              "dataType": "string"
                          },
                          {
                              "displayName": "MAC Address",
                              "name": "MAC_ADDRESS",
                              "dataType": "string"
                          },
                          {
                              "displayName": "Part Number",
                              "name": "PART_NUMBER",
                              "dataType": "string"
                          }
                      ],
                      "filterCriteria": [
                          {
                              "name": "unassigned_only",
                              "dataType": "boolean",
                              "supportedOperators": ["EQ"]
                          },
                          {
                              "name": "archive_visibility",
                              "dataType": "string",
                              "supportedOperators": ["EQ"]
                          }
                      ]
                  }
              ],
              "count": 2,
              "total": 6,
              "offset": 0
          }
```

#### POST report exports

With the information returned by the [GET report exports metadata](#get-report-exports-metadata) endpoint, structure the reporting request. This is an asynchronous API call.


```bash
POST /reporting/v1/report-exports
```

In your payload:

- Give the report a name, define the type, and provide a description of the report.
- Define the query elements (`queryElements`), specifically, the `columns` of information you want to return in the report. The example payload shows the criteria of a report on workspace subscriptions.
- Specify the filter criteria (`filterCriteria`). For example, to return a particular subscription you could filter on a unique subscription key. Separate multiple `filterCriteria` with a comma.
- Define the format of the report (`CSV`,`PDF`,`EXCEL`,`TXT`), the email subject, and recipients email address (separate multiple recipients with a comma).


An example of filter criteria.


```json
    {
        "key": "SUBSCRIPTION_KEY",
        "operator": "EQ",
        "value": "123PQR32AQ5BC"
    },
    {
        "key": "product_type",
        "operator": "EQ",
        "value": "DEVICE"
    }
```

Example request payload.


```json
        {
          "name": "Name of the report",
          "description": "Description about the report",
          "kind": "REPORT.EXPORTS",
          "type": "subscriptions",
          "definition": {
              "queryElements": {
                  "columns": [
                      "SUBSCRIPTION_KEY",
                      "SUBSCRIPTION_TYPE",
                      "SUBSCRIPTION_TIER_DESCRIPTION",
                      "AVAILABLE_QUANTITY",
                      "QUANTITY",
                      "SUBSCRIPTION_START",
                      "SUBSCRIPTION_END",
                      "CONTRACT"
                  ],
                  "filterCriteria": [
                      {
                          "key": "product_type",
                          "operator": "EQ",
                          "value": "DEVICE"
                      },
                      {
                          "key": "SUBSCRIPTION_KEY",
                          "operator": "EQ",
                          "value": "123PQR32AQ5BC"
                      },
                      {
                          "key": "QUANTITY",
                          "operator": "GT",
                          "value": "5"
                      },
                      {
                          "key": "sort_by",
                          "operator": "EQ",
                          "value": "expiration"
                      },
                      {
                          "key": "direction",
                          "operator": "EQ",
                          "value": "asc"
                      }
                  ]
              },
              "enrollment": {
                  "delivery": {
                      "format": "CSV",
                      "email": {
                          "subject": "Subscription report sorted with expiration generated",
                          "recipients": [
                              "test@test.com"
                          ]
                      }
                  }
              }
          }
      }
```

A successful call to this API returns a `202 Accepted` response if the request is processing. This response indicates that the call is being processed, but is not yet complete. A `202 Accepted` response includes:

- A unique identifier for the request.
- An indication of the status, for example, that the request is in process. It might return a more detailed message.


The location header of a successfully completed `POST report exports` includes a URL to retrieve the report.

#### GET report status by ID

Use this API to get an update on the progress of the asynchronous API call. Pass the status identifier (`id`) returned in the [GET async operations](#post-report-exports) into the API request.

Example request.


```bash
GET /reporting/v1/statuses/{id}
```

Example response.


```json

{
    "id": "<Status-Id>",
    "resourceUri": "</reporting/v1/statuses/{id}>",
    "type": "REPORT",
    "status": "<status of stage>",
    "stage":"<Report Submission/In queue>",
    "message": "<small brief of the message to customer",
    "isExpired": "<True/False based on the expiry of the report>",
    "reportType": "<Subscription Report or Device Inventory Report or Activate Report>",
    "reportDownloadUrl": "<Presigned URL after report generation is complete and report is not expired else empty>",
    "recipientEmailId": "<Recipient email Id>",
    "startTime": "<timestamp at which report request placed in RFC3339 format>",
    "statusTimestamp": "<Timestamp of last available status in RFC3339 format>",
    "createdAt": "<Timestamp of the creation date in RFC3339 format>"
}
```

#### GET asynchronous operation details

Use the `GET asynchronous operation details` API to retrieve a URL to view the report (and other information on the `POST report exports` API call).

In the request, include the unique identifier (`id`) returned by the `POST report exports` API. For example:


```bash
GET /reporting/v1/async-operations/**{id}**
```

The response body includes a `results` array that contains the URL (`resourceUri`) to the report when the report is generated.

### Filtering

Filters limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET or PUT action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query limits resources to results with the attribute flag and the value true.


```bash
GET <URI>?filter=example eq true
```

#### Filtering on a single property


```bash
filter = <propertyName> <comparison operation> <literal>
```

For example:


```bash
GET <URI>?filter=example eq example`
```

**Property** is the name of an attribute in the requested resource type, such as flag. The property name is always to the left of the operation. Specify nested property names with the `/` separator.

**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

| Operation | Example | Description |
|  --- | --- | --- |
| `eq` | `type eq 'REPORT'` | Checks if the type is `REPORT`. |
| `ne` | `type ne 'REPORT'` | Returns all results when type is not equal to `REPORT`. |
| `gt` | `createdAt gt 2019-08-24T14:15:22Z` | Returns all resources created after the specified date. |
| `ge` | `createdAt ge 2019-08-24T14:15:22Z` | Returns all resources created on or after the specified date. |
| `lt` | `createdAt lt 2019-08-24T14:15:22Z` | Returns all resources before the specified date. |


A **literal**, for example, `true`, is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals.

Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

The following are examples of literals.

- **String**—Anything in 'single quotes'. Reserved characters in string literals must be URL encoded.
- **Integer**—-100, -1, 0, 1, 100
- **Decimal**—-3.14, -2.71, 2.71, 3.14
- **Timestamp**—2019-10-12T07:20:50.52934852Z. The timestamp format is [RFC3339]
- **Boolean**—true, false
- **Null**—Null is equal to itself and nothing else. Null is not greater or less than anything.


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).