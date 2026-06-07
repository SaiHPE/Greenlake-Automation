---
title: "GET /sustainability-insight-ctr/v1beta1/cloud-usage-series"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getcloudusagebyseries.md"
scraped_at: "2026-06-07T06:16:25.805905+00:00Z"
---

# Timeseries of cloud carbon footprint usage over time

Retrieves aggregated carbon footprint usage statistics grouped by time bucket over a defined time frame and
supports filtering by entities. Behavior is non-deterministic if the time range does not divide evenly by your selected
interval.

Endpoint: GET /sustainability-insight-ctr/v1beta1/cloud-usage-series
Version: v1beta1
Security: bearer

## Query parameters:

  - `interval` (string, required)
    Interval of the created time series. Must be of the format "integer unit". Valid units are day(s), hour
(s), week(s), month(s), and year(s). Cloud usage typically is measured in months, so the smaller time units are
likely to be approximations.

  - `start-time` (string, required)
    Start of the query's time range in ISO8601 format.

  - `end-time` (string, required)
    End of the query's time range in ISO8601 format.

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

  - `items.id` (string, required)
    ID of the returned time-bucketed aggregate.

  - `items.type` (string, required)
    Type of returned aggregate.

  - `items.timeBucket` (string)
    Starting time of the returned time-bucketed aggregate in ISO8601 format.

  - `items.co2eMetricTon` (number)
    CO2 equivalent generation in metric tons for this time bucket.

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


