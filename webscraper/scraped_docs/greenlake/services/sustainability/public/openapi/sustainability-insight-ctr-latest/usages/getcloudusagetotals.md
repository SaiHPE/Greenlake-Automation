---
title: "GET /sustainability-insight-ctr/v1beta1/cloud-usage-totals"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getcloudusagetotals.md"
scraped_at: "2026-06-07T06:16:25.806209+00:00Z"
---

# Total aggregated cloud carbon footprint usage

Returns the total carbon footprint over a defined time frame and supports filtering by cloud entities.

Endpoint: GET /sustainability-insight-ctr/v1beta1/cloud-usage-totals
Version: v1beta1
Security: bearer

## Query parameters:

  - `start-time` (string, required)
    Start of the query's time range in ISO8601 format.

  - `end-time` (string, required)
    End of the aggregate's time range in ISO8601 format.

  - `filter` (string)
    Limit the cloud entities operated on by this endpoint, returning only the subset of entities that match the filter. The
filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only.

Cloud entities can be filtered by:
- entityId
- serviceProvider
- serviceName
- serviceRegion
- serviceAccount
- name

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.type` (string, required)
    Type of returned aggregate.

  - `items.co2eMetricTon` (number)
    Total CO2 equivalent generation in metric tons.

  - `count` (integer, required)

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.

## Response 429 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.


