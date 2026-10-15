---
title: "HPE GreenLake Consumption Analytics API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public.md"
scraped_at: "2026-06-07T06:13:26.178317+00:00Z"
---

# HPE GreenLake Consumption Analytics API

This page provides an introduction and quick start guide for the HPE GreenLake Consumption Analytics API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake Consumption Analytics API provides public access to reporting data for cloud consumption. It enables authenticated external clients to retrieve available report definitions, view their structure, and download report results as CSV files. With the release of Reports v2, it also enables clients to generate reports and execute reports with optional date-range filtering.

### Features

- Retrieve a list of available reports and FOCUS export configurations accessible to the authenticated client
- Fetch the full definition of a specific report or FOCUS export configuration, including filters, metrics, and charts
- Download the output of a report as a CSV file for external analysis
- Execute a saved report definition by ID and retrieve the results as structured JSON with flexible date-range filtering (v2)
- Generate and execute a report directly from a full report definition, without requiring a pre-saved report ID, and retrieve the results as structured JSON with flexible date-range filtering (v2)
- Export FOCUS-compliant consumption data as a CSV file with flexible date-range filtering (v1beta1)


### Use cases

- **Automated report extraction**—Fetch and download report contents periodically to power custom dashboards or integrate with data warehouses.
- **Report inspection**—Use the API to programmatically inspect report structure, including filters and fields, before execution.
- **Report generation**—Generate a report with desired information and filters to provide the exact data a workflow requires.
- **Data pipeline integration**—Incorporate downloaded CSV outputs into automated workflows for billing, analytics, or compliance reporting.


### Related documentation

- [Consumption Analytics Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-AD3011AB-D1D4-4E7A-A2FA-E7DA06580298.html)


## Developer guide

This guide provides foundational details and examples to help you use the Consumption Analytics API on the HPE GreenLake cloud.

### Prerequisites

#### Hostname

When forming a Consumption Analytics REST API call, use the following hostname:

- [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)


#### Endpoints

The URIs for the HPE GreenLake Consumption Analytics API are as follows:

**v1 Reports** – `/consumption-analytics/v1/reports`

- `GET /consumption-analytics/v1/reports`—Retrieves a list of available reports that the caller has permission to access.
- `GET /consumption-analytics/v1/reports/{id}`—Retrieves the full definition of a specific report, including filters, columns, charts, sharing settings, and metadata.
- `GET /consumption-analytics/v1/reports/{id}/contents`—Downloads the contents of a specific report in CSV format.


**v2 Reports** – `/consumption-analytics/v2/reports`

- `GET /consumption-analytics/v2/reports`—Lists available report definitions with support for pagination (`limit`, `offset`).
- `POST /consumption-analytics/v2/reports/execute`—Executes a report from a full definition supplied in the request body. The request uses a structured public model with explicit filter and column definitions (see [Executing a report from a definition](#executing-a-report-from-a-definition) below).
- `POST /consumption-analytics/v2/reports/{id}/execute`—Executes a saved report definition by ID and returns the results as a JSON table. Accepts an optional date-range filter in the request body using either a relative range or absolute start/end dates.


**v1beta1 FOCUS Exports** – `/consumption-analytics/v1beta1/focus-exports`

- `GET /consumption-analytics/v1beta1/focus-exports`—Lists the FOCUS export configurations available to the caller.
- `GET /consumption-analytics/v1beta1/focus-exports/{id}`—Retrieves the full definition of a specific FOCUS export configuration.
- `GET /consumption-analytics/v1beta1/focus-exports/{id}/contents`—Executes the given FOCUS export configuration and returns a FOCUS-compliant CSV file. Requires either `relativeDate` or a `startDate`/`endDate` pair.


#### Permissions

Any user with access to the Consumption Analytics application in HPE GreenLake can access both the UI and the API, subject to configured permissions.

#### Generating a token

You must configure API credentials and generate an OAuth-based access token to make API calls.

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


Use the following cURL command to get the token:


```sh
curl -X POST https://sso.common.cloud.hpe.com/as/token.oauth2 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$YOUR_CLIENT_ID&client_secret=$YOUR_CLIENT_SECRET"
```

The token response includes an `expires_in` field (in seconds) indicating how long the token is valid. Check this value to determine when the token will expire and request a new one before it does.

### Making it all work

#### Listing available reports

This endpoint allows you to retrieve a list of all available reports. Only reports that the caller has permission to access will be included in the response.

Example request:


```sh
GET '{{HOSTNAME}}/consumption-analytics/v1/reports'
```

Example response:


```json
[
  {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx0001",
    "name": "Cost Analysis (Last 30 Days)",
    "created": {
      "id": "system",
      "name": "System",
      "time": "2022-05-04T22:27:12.071872"
    },
    "lastUpdated": {
      "id": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
      "name": "User A",
      "time": "2023-02-15T18:41:24.531274"
    },
    "shared": true,
    "owner": false
  },
  {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx0002",
    "name": "Monthly Usage Cost Report",
    "created": {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "name": "User B",
      "time": "2023-08-31T16:56:41.044146",
      "email": "user.b@example.com"
    },
    "lastUpdated": {
      "id": "system",
      "name": "System",
      "time": "2023-08-31T16:56:41.044146"
    },
    "shared": true,
    "owner": false
  },
  {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx0003",
    "name": "Cloud Cost Breakdown Report",
    "created": {
      "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "name": "User C",
      "time": "2023-08-31T17:07:37.97998",
      "email": "user.c@example.com"
    },
    "lastUpdated": {
      "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "name": "User C",
      "time": "2024-09-05T03:17:11.578997"
    },
    "shared": true,
    "owner": false
  }
]
```

#### Downloading a report as CSV

This endpoint allows you to download the contents of a specific report as a CSV file.

Example request:


```sh
GET '{{HOSTNAME}}/consumption-analytics/v1/reports/{id}/contents'
```

Replace `{id}` with the ID of the report you want to download.

Example response:


```text
Product,Cost,Accounting Date
VM,1701.59,2025-02-24
VM,1733.42,2025-02-20
VM,1729.88,2025-02-25
VM,1732.28,2025-02-27
VM,1730.24,2025-02-26
VM,1720.95,2025-02-18
VM,1731.17,2025-02-21
VM,1718.34,2025-02-19
VM,1537.63,2025-03-03
VM,1563.79,2025-03-04
VM,1563.79,2025-03-05
VM,1563.79,2025-03-06
VM,1562.71,2025-03-07
VM,1732.3,2025-02-28
VM,1570.89,2025-03-12
VM,1570.53,2025-03-13
VM,1563.01,2025-03-11
VM,1567.19,2025-03-19
VM,1527.94,2025-03-10
```

- The response will return a CSV file with `Content-Disposition` set to **attachment**.


#### Retrieving a report definition

This endpoint allows you to fetch the full definition of a specific report, including its filters, columns, charts, sharing information, and metadata.

Example request:


```sh
GET '{{HOSTNAME}}/consumption-analytics/v1/reports/{id}'
```

Replace `{id}` with the ID of the report you want to retrieve.

Example response:


```json
{
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "name": "Sample Report Name",
    "description": "Example report description",
    "filter": {
        "dateFilter": {
            "type": "RELATIVE",
            "relativeRange": "LAST_90_DAYS"
        },
        "fieldFilters": [
            {
                "name": "sys_ServiceCategory_s",
                "operator": "NOT_EMPTY",
                "values": []
            }
        ]
    },
    "columns": [
        {
            "fieldName": "sys_ServiceCategory_s",
            "aggFunction": "NONE",
            "group": false,
            "formatting": {}
        },
        {
            "fieldName": "sys_Cost_f",
            "aggFunction": "SUM",
            "group": false,
            "formatting": {
                "placesAfterDecimal": 2
            }
        }
    ],
    "created": {
        "id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "name": "API Client User",
        "time": "2025-03-21T00:00:00.000000",
        "email": "user@example.com"
    },
    "lastUpdated": {
        "id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "name": "API Client User",
        "time": "2025-03-21T00:00:00.000000"
    },
    "owner": true,
    "charts": [
        {
            "id": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            "type": "BAR",
            "title": "Sample Chart Title",
            "definition": {
                "metric": "sys_Cost_f",
                "metricAggFunction": "SUM",
                "series": "sys_ServiceCategory_s",
                "excludeOther": false,
                "maxGroups": 10,
                "orientation": "VERTICAL"
            }
        }
    ],
    "sharing": {
        "type": "PRIVATE"
    },
    "pivot": false,
    "shared": false
}
```

#### Executing a report from a definition

This endpoint allows you to generate report results by supplying a full report definition in the request body, without requiring a pre-saved report ID. The request body uses a structured public model.

The request body contains two top-level fields:

- `filter`—Controls what data is included. Contains:
  - `dateFilter` (required)—Scopes results to a time window. Set `type` to `RELATIVE` and supply a `relativeRange` value, or set `type` to `ABSOLUTE` and supply both `startDate` and `endDate` in `YYYY-MM-DD` format.
  - `fieldFilters` (optional)—An array of conditions on metadata fields. Each entry specifies a `name` (field identifier), an `operator` (such as `EQ`, `NOT_EQ`, or `STARTS_WITH`), and a `values` array.
- `columns`—The fields to include in the output. Each entry specifies a `fieldName` and an optional `aggFunction` (such as `SUM` or `NONE`).


Example request using a relative date with a field filter:


```sh
POST '{{HOSTNAME}}/consumption-analytics/v2/reports/execute'
```


```json
{
  "filter": {
    "dateFilter": { "type": "RELATIVE", "relativeRange": "LAST_7_DAYS" },
    "fieldFilters": [
      {
        "name": "sys_Provider_s",
        "operator": "STARTS_WITH",
        "values": ["H"]
      }
    ]
  },
  "columns": [
    { "fieldName": "sys_Provider_s" },
    { "fieldName": "sys_MeterName_s" },
    { "fieldName": "sys_Cost_f", "aggFunction": "SUM" }
  ]
}
```

Example request using an absolute date range, no field filter:


```sh
POST '{{HOSTNAME}}/consumption-analytics/v2/reports/execute'
```


```json
{
  "filter": {
    "dateFilter": { "type": "ABSOLUTE", "startDate": "2026-01-01", "endDate": "2026-03-31" }
  },
  "columns": [
    { "fieldName": "sys_Provider_s" },
    { "fieldName": "sys_Cost_f", "aggFunction": "SUM" }
  ]
}
```