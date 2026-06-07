---
title: "HPE Sustainability Insight Center API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public.md"
scraped_at: "2026-06-07T05:46:14.908790+00:00Z"
---

# HPE Sustainability Insight Center API

This document provides a brief overview and quick-start developer guide:

- [Overview](#overview)—Learn about the HPE Sustainability Insight Center API features, use cases, and how it enables programmatic access to energy consumption and carbon footprint data.
- [Developer guide](#developer-guide)—Get started with the API including prerequisites and authentication. The [Making it all work](#making-it-all-work) section describes endpoint usage and provides detailed code examples for retrieving sustainability metrics.


## Overview

HPE Sustainability Insight Center APIs allow developers to access HPE Sustainability Insight Center features and data programmatically. With these APIs, you can get the total energy consumption across your IT infrastructure, information about greenhouse gas emissions, and costs associated with your energy consumption.

### Features

- HPE Sustainability Insight Center API is a RESTful API that enables programmatic access to:
  - Measurements of the carbon footprint of HPE IT assets based on actual energy usage
  - Data on carbon footprint and energy costs across sites (per device and site location)
  - Data on energy consumption data from devices


### Use cases

- **Achieving sustainability goals**—Use data retrieved from the HPE Sustainability Insight Center API to measure your organization's power consumption and carbon footprint. With this data, your organization can make data-backed and informed decisions to reduce its climate impact and ensure its IT assets operate in a way that meets regulatory and business environmental sustainability goals.
- **Monitoring IT costs**—Use HPE data available from the HPE Sustainability Insight Center API to rationalize the power consumption of IT assets operations for cost efficiency. This will free up budget for innovative and growth-oriented investments.
- **Integrating into reporting workflows**—Retrieving HPE Sustainability Insight Center data through the API facilitates incorporating this data into existing analytics, reporting, dashboards, and forecasting workflows to give your organization a robust understanding of its IT operations.


### Related documentation

[HPE GreenLake Cloud User Guide: HPE Sustainability Insight Center](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-64E2035A-138E-44E8-8A04-7968A272A97E.html)

## Developer guide

The details and examples in this guide will help you get started using the HPE Sustainability Insight Center API for HPE GreenLake cloud.

### Prerequisites

#### Hostname

When forming an HPE Sustainability Insight Center REST API call, choose the hostname that is closest to your region:

- [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)
- [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)


#### Endpoints

The URIs for the HPE Sustainability Insight Center API endpoints are as follows:

- `GET /sustainability-insight-ctr/v1beta1/usage-by-entity`
- `GET /sustainability-insight-ctr/v1beta1/usage-totals`
- `GET /sustainability-insight-ctr/v1beta1/usage-series`
- `GET /sustainability-insight-ctr/v1beta1/cloud-usage-by-entity`
- `GET /sustainability-insight-ctr/v1beta1/cloud-usage-totals`
- `GET /sustainability-insight-ctr/v1beta1/cloud-usage-series`
- `GET /sustainability-insight-ctr/v1beta1/coefficients`
- `POST /sustainability-insight-ctr/v1beta1/coefficients`
- `GET /sustainability-insight-ctr/v1beta1/coefficients/{id}`
- `GET /sustainability-insight-ctr/v1beta1/ingests`
- `POST /sustainability-insight-ctr/v1beta1/ingests`
- `GET /sustainability-insight-ctr/v1beta1/ingests/{id}`
- `GET /sustainability-insight-ctr/v1beta1/datasources`
- `GET /sustainability-insight-ctr/v1beta1/datasources/{id}`
- `GET /sustainability-insight-ctr/v1beta1/locations`
- `GET /sustainability-insight-ctr/v1beta1/locations/{locationId}`
- `POST /sustainability-insight-ctr/v1beta1/forecast/energy`
- `GET /sustainability-insight-ctr/v1beta1/usage-by-entity/{id}/locations/{locationId}`


#### Permissions

Any user with access to the HPE Sustainability Insight Center application has access to both the UI and the API.

#### Generating a token

You must configure API credentials and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token.

To access this HPE GreenLake Sustainability Insight Center API, proceed as follows:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


Run the cURL command below to get the token from the `response["access_token"]`:


```sh
curl -X POST https://global.api.greenlake.hpe.com/authorization/v2/oauth2/<WORKSPACE_ID>/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$YOUR_CLIENT_ID&client_secret=$YOUR_CLIENT_SECRET"
```

This access token is used as the bearer token for the authentication of the HPE Sustainability Insight Center API. The token is valid for two hours.

### Making it all work

#### Getting energy usage grouped by entity

Run the below API call with the bearer token from the previous step to get energy usage data related to your workspace. The `start-time` and `end-time` query parameters are required. The `start-time` and `end-time` query parameters must be in ISO 8601 format, for example `2019-10-12T07:20:50.529Z`.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/usage-by-entity?start-time={{START_TIME}}&end-time={{END_TIME}}&offset=0'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "COMPUTE1234567",
      "type": "sustainability-insight-ctr/entities",
      "entityId": "COMPUTE1234567",
      "entityMake": "HPE",
      "entityModel": "PROLIANT DL380 GEN10",
      "entityType": "COMPUTE",
      "entitySerialNum": "1234567",
      "entityProductId": "7654321",
      "entityManufactureTimestamp": "2023-11-01T00:00:00.000Z",
      "locationName": "Somewhere",
      "locationId": "00000000-0000-0000-0000-000000000000",
      "locationCity": "Boston",
      "locationState": "MA",
      "locationCountry": "USA",
      "tags": [
        {
          "name": "OS",
          "value": "Linux"
        }
      ],
      "name": "",
      "cost": 100.1234,
      "costUsd": null,
      "currency": "USD",
      "co2eMetricTon": 0.6,
      "kwh": 700.1234
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

This call can be filtered using the `filter` query parameter. Refer to [filtering](#filtering) for more details.

This call can also be filtered by tags using the `filter-tags` query parameter. Refer to [Filtering tags](#filtering-tags) for more details.

This call can be provided a `currency` currency code query parameter to change the returned currency type. Refer to [Currency](#currency) for more details.

Other supported API parameters are `sort`, `offset` and `limit`.

Returned field `costUsd` is deprecated in favor of `cost`.

#### Getting energy usage totals

This endpoint is for getting the total aggregated energy usages across all entities for the defined time frame. The `start-time` and `end-time` query parameters are required. The `start-time` and `end-time` query parameters must be in ISO 8601 time format, for example `2019-10-12T07:20:50.52934852Z`.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/usage-totals?start-time={{START_TIME}}&end-time={{END_TIME}}'
```

Sample API response:


```json
{
  "items": [
    {
      "type": "sustainability-insight-ctr/totals",
      "cost": 100.1234,
      "costUsd": null,
      "currency": "USD",
      "co2eMetricTon": 0.5,
      "kwh": 700.1234
    }
  ],
  "count": 1
}
```

This example response returns one result (`"count": 1`) and returns the following data:

- `cost`—The estimated energy cost.
- `co2eMetricTon`—Carbon dioxide equivalent estimated in metric tons.
- `kwh`—Energy consumption in kilowatts per hour.
- `currency`—The returned cost currency type.


This call can be filtered using the `filter` query parameter. Refer to [filtering](#filtering) for more details.

This call can also be filtered by tags using the `filter-tags` query parameter. Refer to [Filtering tags](#filtering-tags) for more details.

This call can be provided a `currency` currency code query parameter to change the returned currency type. Refer to [Currency](#currency) for more details.

Returned field `costUsd` is deprecated in favor of `cost`.

#### Getting energy usage series data

This endpoint is for getting energy usages across all entities grouped by time bucket for the defined time frame. The `start-time`, `end-time`, and `interval` query parameters are required. Behavior is non-deterministic if the time range does not divide evenly by your selected interval.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/usage-series?start-time={{START_TIME}}&end-time={{END_TIME}}&interval={{INTERVAL}}'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "2024-01-18T00:00:00.000Z",
      "type": "sustainability-insight-ctr/timeseries",
      "timeBucket": "2024-01-18T00:00:00.000Z",
      "cost": 0,
      "currency": "USD",
      "costUsd": null,
      "co2eMetricTon": 0,
      "kwh": 0
    },
    {
      "id": "2024-01-19T00:00:00.000Z",
      "type": "sustainability-insight-ctr/timeseries",
      "timeBucket": "2024-01-19T00:00:00.000Z",
      "cost": 50.01234,
      "currency": "USD",
      "costUsd": null,
      "co2eMetricTon": 0.25,
      "kwh": 345.321
    }
  ],
  "count": 2
}
```

This example response returns two results (`"count": 2`).

The `interval` query parameter must be of the format "integer unit". Valid units are day(s), hour(s), week(s), month(s), and year(s), for example, `1 day`, `2 hours`, `6 week`, `18 month`,  and `3 year`. The example response shows an `interval` of `1 day` as the `"id:"` and `"timeBucket"` increase by one day (2024-01-**18**T00:00:00.000Z and 2024-01-**19**T00:00:00.000Z).

- `timeBucket`—A time bucket is a feature of time series analysis and forecasting. It is the time interval between successive measurements or values. In the example response, the `timeBucket` interval is `1 day` and the measures for `costUsd`, `co2eMetricTon`, and `kwh` are daily totals.
- `cost`—The estimated energy cost.
- `co2eMetricTon`—Carbon dioxide equivalent estimated in metric tons.
- `kwh`—Energy consumption in kilowatts per hour.
- `currency`—The returned cost currency type.


This call can be filtered using the `filter` query parameter. Refer to [filtering](#filtering) for more details.

This call can also be filtered by tags using the `filter-tags` query parameter. Refer to [Filtering tags](#filtering-tags) for more details.

This call can be provided a `currency` currency code query parameter to change the returned currency type. Refer to [Currency](#currency) for more details.

Returned field `costUsd` is deprecated in favor of `cost`.

#### Getting public cloud sustainability data grouped by entity

Run the below API call to get public cloud sustainability data related to your workspace. The `start-time` and `end-time` query parameters are required. The `start-time` and `end-time` query parameters must be in ISO 8601 format, for example `2019-10-12T07:20:50.529Z`.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/usage-by-entity?start-time={{START_TIME}}&end-time={{END_TIME}}&offset=0'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "COMPUTE1234567",
      "type": "sustainability-insight-ctr/cloud-entities",
      "serviceProvider": "aws",
      "serviceName": "s3",
      "serviceRegion": "us-east",
      "serviceAccount": "123456789012",
      "name": "",
      "co2eMetricTon": 0.6
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

This call can be filtered using the `filter` query parameter. Refer to [filtering](#filtering) for more details.

Other supported API parameters are `sort`, `offset`, and `limit`.

#### Getting public cloud sustainability data totals

This endpoint is for getting the total aggregated public cloud sustainability data across all entities for the defined time frame. The `start-time` and `end-time` query parameters are required. The `start-time` and `end-time` query parameters must be in ISO 8601 time format, for example `2019-10-12T07:20:50.52934852Z`.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/usage-totals?start-time={{START_TIME}}&end-time={{END_TIME}}'
```

Sample API response:


```json
{
  "items": [
    {
      "type": "sustainability-insight-ctr/cloud-totals",
      "co2eMetricTon": 0.5
    }
  ],
  "count": 1
}
```

This example response returns one result (`"count": 1`) and returns the following data:

- `co2eMetricTon`—Carbon dioxide equivalent estimated in metric tons.


This call can be filtered using the `filter` query parameter. Refer to [filtering](#filtering) for more details.

#### Getting public cloud sustainability series data

This endpoint is for getting public cloud sustainability data across all entities grouped by time bucket for the defined time frame. The `start-time`, `end-time`, and `interval` query parameters are required. Behavior is non-deterministic if the time range does not divide evenly by your selected interval.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/cloud-usage-series?start-time={{START_TIME}}&end-time={{END_TIME}}&interval={{INTERVAL}}'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "2024-01-01T00:00:00.000Z",
      "type": "sustainability-insight-ctr/cloud-timeseries",
      "timeBucket": "2024-01-01T00:00:00.000Z",
      "co2eMetricTon": 0
    },
    {
      "id": "2024-02-01T00:00:00.000Z",
      "type": "sustainability-insight-ctr/cloud-timeseries",
      "timeBucket": "2024-02-01T00:00:00.000Z",
      "co2eMetricTon": 6.25
    }
  ],
  "count": 2
}
```

This example response returns two results (`"count": 2`).

The `interval` query parameter must be of the format "integer unit". Valid units are `hour`, `hours`, `day`, `days`, `week`, `weeks`, `month`, `months`, `year`, and `years`, for example, `1 day`, `2 hours`, `6 week`, `18 month`,  and `3 year`. The example response shows an `interval` of `1 month` as the `"id:"` and `"timeBucket"` increase by one month (2024-**01**-01T00:00:00.000Z and 2024-**02**-01T00:00:00.000Z).

- `timeBucket`—A time bucket is a feature of time series analysis and forecasting. It is the time interval between successive measurements or values. In the example response, the `timeBucket` interval is `1 month` and the measure for `co2eMetricTon` is the monthly total.
- `co2eMetricTon`—Carbon dioxide equivalent estimated in metric tons.


This call can be filtered using the `filter` query parameter. Refer to [filtering](#filtering) for more details.

#### Getting cost and CO2 coefficients

This endpoint is for getting previously defined cost and CO2 coefficients.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/coefficients'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-0000000000000",
      "type": "sustainability-insight-ctr/coefficient",
      "associatedLocation": {

        "locationId": "00000000-0000-0000-0000-000000000000",
        "locationName": "Denver, CO",
        "resourceUri": "/locations/v1beta1/locations/00000000-0000-0000-0000-0000000000000"
      },
      "startTime": "2024-01-01T00:00:00.000Z",
      "co2eGramsPerKwh": 0.5,
      "costUsdPerKwh": null,
      "costPerKwh": 0.5,
      "currency": "USD",
      "generation": 0,
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-02-01T00:00:00.000Z"
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

This call can be filtered using the `filter` query parameter.  The only field available to filter on is `locationId`. Refer to [filtering](#filtering) for more details.

This call can also be filtered by tags using the `filter-tags` query parameter. Refer to [Filtering tags](#filtering-tags) for more details.

This call can be provided a `currency` currency code query parameter to change the returned currency type. Refer to [Currency](#currency) for more details.

Other supported API parameters are `offset` and `limit`.

Returned field `costUsdPerKwh` is deprecated in favor of `costPerKwh`.

#### Setting cost and CO2 coefficients

This endpoint is for setting cost and CO2 coefficients for your workspace. This endpoint requires the HPE Sustainability Insight Center Administrator Role. You must provide a location URI as `locationId`. If you exclude `co2eGramsPerKwh` or `costPerKwh`, its behavior is the same as including it with `useCurrent` set to true.

- `useDefault` - Set to true if you want to use the default value determined by HPE. This cannot be true if `useCurrent` is true.
- `useCurrent` - Set to true if you want to keep whatever was previously set for this coefficient. This cannot be true if `useDefault` is true.
- `value` - A floating point number to be used as the coefficient starting the next day, as long as `useDefault` and `useCurrent` are both false.
- `currency` - In the case of the `costPerKwh`, you can provide a currency code to specify the type of cost. Refer to [Currency](#currency) for more details.


Input field `costUsdPerKwh` is deprecated in favor of `costPerKwh`.


```sh
POST '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/coefficients'
```

Sample payload:


```json
{
  "locationId": "/locations/v1beta1/locations/00000000-0000-0000-0000-0000000000000",
  "co2eGramsPerKwh": {
    "useDefault": false,
    "useCurrent": false,
    "value": 0.1
  },
  "costUsdPerKwh": null,
  "costPerKwh": {
    "useDefault": false,
    "useCurrent": false,
    "value": 0.1,
    "currencyCode": "USD"
  }
}
```

If this `POST` call succeeds, the API returns a `201 Created` response with the created coefficient. This response contains the exact startTime that the coefficient will begin taking effect. Here is an example:


```json
{
  "id": "00000000-0000-0000-0000-0000000000000",
  "type": "sustainability-insight-ctr/coefficient",
  "associatedLocation": {
    "locationId": "00000000-0000-0000-0000-000000000000",
    "locationName": "Denver, CO",
    "resourceUri": "/locations/v1beta1/locations/00000000-0000-0000-0000-0000000000000"
  },
  "startTime": "2024-01-02T00:00:00.000Z",
  "co2eGramsPerKwh": 0.5,
  "costUsdPerKwh": null,
  "costPerKwh": 0.5,
  "currency": {
    "currencyCode": "USD",
    "currencyName": "United States Dollar"
  },
  "generation": 0,
  "createdAt": "2024-01-01T12:00:00.000Z",
  "updatedAt": "2024-01-01T12:00:00.000Z"
}
```

Returned field `costUsdPerKwh` is deprecated in favor of `costPerKwh`.

#### Getting a specific cost and CO2 coefficient by ID

This endpoint is for getting a single cost and CO2 coefficient.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/coefficients/00000000-0000-0000-0000-0000000000000'
```

Sample API response:


```json
{
  "id": "00000000-0000-0000-0000-0000000000000",
  "type": "sustainability-insight-ctr/coefficient",
  "associatedLocation": {
    "locationId": "00000000-0000-0000-0000-000000000000",
    "locationName": "Denver, CO",
    "resourceUri": "/locations/v1beta1/locations/00000000-0000-0000-0000-0000000000000"
  },
  "startTime": "2024-01-01T00:00:00.000Z",
  "co2eGramsPerKwh": 0.5,
  "costPerKwh": 0.5,
  "currency": {
    "currencyCode": "USD",
    "currencyName": "United States Dollar"
  },
  "costUsdPerKwh": null,
  "generation": 0,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-02-01T00:00:00.000Z"
}
```

Returned field `costUsdPerKwh` is deprecated in favor of `costPerKwh`.

#### Getting metadata on uploaded device measurements

This endpoint is for getting the metadata related to any user uploaded device measurements.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/ingests'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-0000000000000",
      "type": "sustainability-insight-ctr/ingest",
      "name": "Example Data",
      "description": "Lorem ipsum",
      "generation": 0,
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-02-01T00:00:00.000Z"
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

This call supports the API parameters `offset` and `limit`.

#### Uploading device measurements

This endpoint is for users to upload their own device measurements to HPE Sustainability Insight Center. The upload must be a `.csv` file and match the HPE Sustainability Insight Center third party data template.  You can find the template on the HPE Sustainability Insight Center UI on the Data Configuration > Data Import page. The maximum size allowed for a single upload is 300MB. This endpoint requires the HPE Sustainability Insight Center Administrator Role.


```sh
POST '/sustainability-insight-ctr/v1beta1/ingests' -F name="Example Name" -F description="Lorem ipsum" -F file=@measurements.csv
```

Form data payload:


```sh
name="Example Name"
description="Lorem ipsum"
file=@measurements.csv
```

#### Getting metadata on uploaded device measurements by ID

This endpoint is for getting metadata on a single device measurement upload.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/ingests/00000000-0000-0000-0000-0000000000000'
```

Sample API response:


```json
{
  "id": "00000000-0000-0000-0000-0000000000000",
  "type": "sustainability-insight-ctr/ingest",
  "name": "Example Data",
  "description": "Lorem ipsum",
  "generation": 0,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-02-01T00:00:00.000Z"
}
```

#### Getting data sources

This endpoint is for getting the list of all HPE Sustainability Insight Center data sources.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/datasources'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-0000000000000",
      "type": "sustainability-insight-ctr/datasources",
      "name": "HPE Aruba Central",
      "provider": "HPE",
      "lastCollectionTime": "2024-05-28T00:00:00.000Z",
      "firstCollectionTime": "2024-02-29T00:00:00.000Z",
      "generation": 0,
      "createdAt": "2024-01-01T00:00:00.000Z",
      "updatedAt": "2024-02-01T00:00:00.000Z"
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
}
```

#### Getting a single data source

This endpoint is for getting the details of a single data source by id.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/datasources/{id}'
```

Sample API response:


```json
{
  "id": "00000000-0000-0000-0000-0000000000000",
  "type": "sustainability-insight-ctr/datasources",
  "name": "HPE Aruba Central",
  "provider": "HPE",
  "lastCollectionTime": "2024-05-28T00:00:00.000Z",
  "firstCollectionTime": "2024-02-29T00:00:00.000Z",
  "generation": 0,
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-02-01T00:00:00.000Z"
}
```

#### Getting locations not associated with a GreenLake location

This endpoint is for getting non-GreenLake locations associated with the authenticated workspace. Each location includes its `name`, `city`, `state`, `country`, and `resourceUri`. This call supports the API parameters `offset`, `limit`, and `sort`.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/locations'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "00000000-0000-0000-0000-000000000000",
      "type": "sustainability-insight-ctr/locations",
      "ownerId": "00000000-0000-0000-0000-000000000000",
      "locationId": "<origin>-123",
      "name": "Building A",
      "city": "San Jose",
      "state": "CA",
      "country": "USA",
      "startTime": "2025-01-01T00:00:00Z",
      "resourceUri": "/sustainability-insight-ctr/v1beta1/locations/loc-123"
    }
  ],
  "count": 1,
  "total": 10,
  "offset": 0
}
```

#### Getting a specific location by location ID

This endpoint is for getting the details of a single non-GreenLake location by its location ID within the authenticated workspace, returning the location's `name`, `city`, `state`, `country`, and `startTime`.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/locations/{locationId}'
```

Sample API response:


```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "type": "sustainability-insight-ctr/locations",
  "ownerId": "00000000-0000-0000-0000-000000000000",
  "locationId": "<origin>-123",
  "name": "Building A",
  "city": "San Jose",
  "state": "CA",
  "country": "USA",
  "startTime": "2025-01-01T00:00:00Z",
  "resourceUri": "/sustainability-insight-ctr/v1beta1/locations/loc-123"
}
```

#### Getting forecasted kWh, CO2, and cost along with confidence intervals for future time range

This endpoint is for retrieving forecasted sustainability metrics—including CO₂ emissions (co2e in metric tons), energy consumption (kWh), and associated costs with confidence intervals—over a specified future time range of 1 to 6 months,
allowing you to project and plan around your expected energy usage, carbon footprint, and costs in a given currency. You must provide `timePeriodMonths` and `currencyCode`.

- `timePeriodMonths` - The number of months into the future to forecast. Must be between 1 and 6.
- `currencyCode` - In the case of the `cost`, you can provide a currency code to specify the type of cost. Refer to [Currency](#currency) for more details.



```sh
POST '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/forecast/energy'
```

Sample payload:


```json
{
  "currencyCode": "USD",
  "timePeriodMonths": 1
}
```

If this call succeeds, the API returns a `200` response with a JSON body containing three sections:

- `pastSeries` — An array of exactly 3 data points representing the last 3 months of historical data. Each entry includes a startDate, energyKwh (energy consumption in kwh), co2eMt (CO₂ equivalent in metric tons), and cost (with a value and unit in the requested currency).
- `forecasts` — An array of forecast data points for the requested number of future months (1–6). Each entry includes a `startDate` and three forecast metrics — `co2eMt`, `energyKwh`, and `cost`— each containing a forecast value along with `lowerBound` and `upperBound` confidence intervals. The cost object also includes a unit field indicating the currency code.
- `sustainabilityJourney` — A summary object comparing the actual latest energy usage against the forecasted expectation. It includes actual (latest kWh value from the past series), expected (forecasted kWh value), `lowerBound` and `upperBound` confidence intervals, and a `startDate` — giving a quick view of whether usage is trending above or below the projected sustainability trajectory.


Sample API response:


```json
{
  "pastSeries": [
    {
      "startDate": "2025-05-01T00:00Z",
      "energyKwh": 300.19,
      "co2eMt": 0.103,
      "cost": {
        "value": "20.004,",
        "unit": "USD"
      }
    },
    {
      "startDate": "2025-06-01T00:00Z",
      "energyKwh": 561.19,
      "co2eMt": 0.248,
      "cost": {
        "value": "76.004,",
        "unit": "USD"
      }
    },
    {
      "startDate": "2025-07-01T00:00Z",
      "energyKwh": 135.19,
      "co2eMt": 0.3453,
      "cost": {
        "value": "30.004,",
        "unit": "USD"
      }
    }
  ],
  "forecasts": [
    {
      "startDate": "2019-08-24T14:15:22Z",
      "co2eMt": {
        "forecast": 0.21135315,
        "lowerBound": 0.13543535,
        "upperBound": 0.3345345
      },
      "energyKwh": {
        "forecast": 0.24635,
        "lowerBound": 0.125235,
        "upperBound": 0.335325
      },
      "cost": {
        "forecast": 0.2235235,
        "lowerBound": 0.135252,
        "upperBound": 0.335232,
        "unit": "USD"
      }
    }
  ],
  "sustainabilityJourney": {
    "actual": 0.248,
    "expected": 0.223,
    "lowerBound": 0.198,
    "upperBound": 0.253,
    "startDate": "2025-06-01T00:00Z"
  }
}
```

#### Getting detailed information for a single device at a specific location over a given time range

This endpoint is for retrieving detailed information for a single entity (device) at a specific location within a time range, including identity, energy metrics, tags, and metadata.


```sh
GET '{{HOSTNAME}}/sustainability-insight-ctr/v1beta1/usage-by-entity/COM12345/locations/a324a06e-c5fc-43b0-ab92-cc8bc14566f5'
```

Sample API response:


```json
{
  "id": "COM12345",
  "type": "sustainability-insight-ctr/usage-by-entity",
  "entityId": "COM12345",
  "entityMake": "HPE",
  "entityModel": "PROLIANT DL380 GEN10",
  "entityType": "COMPUTE",
  "entitySerialNum": "ABCDEFGGG",
  "entityProductId": "A59961995",
  "entityManufactureTimestamp": "2023-12-20T03:50:23Z",
  "name": "nebraska.server.web",
  "locationId": "a324a06e-c5fc-43b0-ab92-cc8bc14566f5",
  "locationName": "Somewhere in Omaha, NE",
  "locationCity": "Omaha",
  "locationState": "NE",
  "locationCountry": "USA",
  "kwh": 400.1,
  "co2eMetricTon": 0.2,
  "cost": 60.3,
  "currency": "USD",
  "tags": [
    {
      "name": "OS",
      "value": "Linux"
    }
  ],
  "metadata": {
    "cpuCount": {
      "minValue": 64.0,
      "maxValue": 64.0
    },
    "deepSleepEnabled": true
  },
  "resourceUri": "/sustainability-insight-ctr/v1beta1/usage-by-entity/COM12345/locations/a324a06e-c5fc-43b0-ab92-cc8bc14566f5"
}
```

### Filtering

Filters allow you to limit the entities involved in the REST call. They are specified using the query parameter `filter`. The following fields can be filtered for regular entities:

- `entityId`
- `entityMake`
- `entityModel`
- `entityType`
- `entitySerialNum`
- `entityProductId`
- `locationName`
- `locationId`
- `locationCity`
- `locationState`
- `locationCountry`
- `name`


The following fields can be filtered for cloud entities:

- `entityId`
- `serviceProvider`
- `serviceName`
- `serviceRegion`
- `serviceAccount`
- `name`


#### Requirements

- Queries will be separated by `and`.
- Queries will have 'equality', 'contains', and 'in' comparisons.
- Each query must follow the format below for different operators.
  - `key eq 'value'` for an 'equality' operation.
  - `contains(key, 'value')` for a 'contains' operation.
  - `key in ('value1', 'value2')` for an 'in' operation.


#### Filtering on a single property

Here is a simple example of filtering energy usage data based on an entity model:


```bash
GET <URI>?filter=entityModel eq 'PROLIANT DL380 GEN10'
```

In this example, the API call only returns data from the entities with the model of ProLiant DL380 Gen10.

**Property** is the name of an attribute in the requested resource type, for example, flag. The property name is always to the left of the operation. Specify nested property names with the `/` separator.

The following example of the possible filter values use the `GET Usage by Entity` endpoint.

| **Filter** | **Example** |
|  --- | --- |
| Location country | `locationCountry eq 'USA'` |
| Entity make | `entityMake eq 'HPE'` |
| Entity model | `entityModel eq 'PROLIANT DL380 GEN10'` |
| Entity type | `entityType eq 'COMPUTE'` |
| Location city | `locationCity eq 'Boston'` |
| Location state | `locationState eq 'MA'` |
| Entity serial number | `entitySerialNum eq '1234567'` |
| Entity product ID | `entityProductId eq '7654321'` |


**Operations** compare properties against literals, for example, `eq`. All parameters require the property on the left and the literal on the right.

Examples of operations:

| Operation | Example | Description |
|  --- | --- | --- |
| eq | `locationCountry eq 'Mexico'` | locationCountry equals Mexico |
| in | `locationCountry in ('Brazil', 'Germany')` | locationCountry must equal one of the literals Brazil or Germany |


A **literal** is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Since our API only supports string filters at this time, this means the literal must be a string literal. String literals are anything inside 'single quotes'. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

#### Composite filtering on multiple properties

The previous section explained queries for filtering on a single property. However, the logical operations enable more elaborate filtering using multiple queries.
Currently, filtering supports combining multiple operations using the 'and' operator.

- **Require both (and)**: `entityMake eq 'HPE' and locationCity eq 'Boston'`


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).

### Filtering tags

Similar to `filter`, the `filter-tags` query parameter allows you to limit the entities involved in a REST call based on their tags. You can filter based on a tag's key and value, case-insensitive.

#### Requirements

- Separate multiple tag filter queries with `and`.
- The only comparison available for tag filters is 'equality'.
- Each query must follow the format below.
  - `'key' eq 'value'` for an 'equality' operation.


#### Filtering on a single tag

Here is a simple example of filtering energy usage data based on an entity model:


```sh
GET <URI>?filter-tags='OS' eq 'Linux'
```

In this example, the API call only returns data from the entities tagged with the Linux operating system.

**Operations** compare tag keys against tag values using the `eq` equality operation. All parameters require the tag key on the left and the tag value on the right.

Examples of operations:

| Operation | Example | Description |
|  --- | --- | --- |
| eq | `'type' eq 'business'` | type equals business |
| eq | `'severity' eq 'Escalated'` | severity equals escalated |


The type of all tag keys and values is string literal. String literals are anything inside 'single quotes'. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

#### Composite filtering on multiple properties

The previous section explained queries for tag filtering on a single tag. However, the logical operations enable more elaborate tag filtering using multiple queries.
Currently, tag filtering supports combining multiple operations using the 'and' operator.

- **Require both (and)**: `'type' eq 'business' and 'OS' eq 'Linux'`


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).

### Currency

Several endpoints allow you to specify the currency type for your input values or the currency type for the returned values. Valid values for the currency are case-insensitive, 3-letter currency codes, such as `USD` for the United States Dollar.

The following table shows all supported currency codes and their expanded name.

| **Currency Code** | **Name** |
|  --- | --- |
| THB | Thai Baht |
| CHF | Swiss Franc |
| INR | Indian Rupee |
| EUR | Euro |
| GBP | Pound Sterling |
| NOK | Norwegian Krone |
| USD | US Dollar |
| AUD | Australian Dollar |
| SEK | Swedish Krona |
| HKD | Hong Kong Dollar |
| AED | UAE Dirham |
| NZD | New Zealand Dollar |
| BGN | Bulgarian Lev |
| RON | Romanian Leu |
| CAD | Canadian Dollar |
| UAH | Ukrainian Hryvnia |
| MXN | Mexican Peso |
| KRW | South Korean Won |
| JPY | Japanese Yen |
| TRY | Turkish Lira |
| DKK | Danish Krone |
| PLN | Polish Zloty |
| CZK | Czech Koruna |
| CLP | Chilean Peso |
| CNY | Chinese Yuan |
| ILS | Israeli New Shekel |
| HRK | Croatian Kuna |
| BAM | Convertible Mark |
| TWD | New Taiwan Dollar |
| MYR | Malaysian Ringgit |


At the start of each day, a currency conversion rate is calculated for each currency and used to convert any values collected for that day.