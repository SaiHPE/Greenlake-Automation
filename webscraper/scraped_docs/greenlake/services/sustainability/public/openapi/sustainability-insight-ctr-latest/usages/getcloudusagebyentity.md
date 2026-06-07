---
title: "GET /sustainability-insight-ctr/v1beta1/cloud-usage-by-entity"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getcloudusagebyentity.md"
scraped_at: "2026-06-07T06:16:25.625127+00:00Z"
---

# Aggregated carbon footprint usage for cloud entities

Retrieves aggregated carbon footprint usage in a list grouped by individual cloud entities, such as, cloud services, over a
defined time frame and supports filtering, sorting, and offset-based pagination.

Endpoint: GET /sustainability-insight-ctr/v1beta1/cloud-usage-by-entity
Version: v1beta1
Security: bearer

## Query parameters:

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

  - `sort` (string)
    Odata 4.0 field to sort entities on. Allowed fields are the strings "entityId", "serviceProvider", "serviceName", "serviceRegion", "serviceAccount", "name". Must be of the format "property order".

  - `offset` (integer)
    Zero-based resource offset to start the response from.

  - `limit` (integer)
    Number of usages to return.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the entity.

  - `items.type` (string, required)
    Type of return object.

  - `items.entityId` (string)
    ID of the entity.

  - `items.serviceProvider` (string)
    Cloud service provider of the entity.

  - `items.serviceName` (string)
    Service name of the entity.

  - `items.serviceRegion` (string)
    Service region of the entity.

  - `items.serviceAccount` (string)
    Service account id of the entity.

  - `items.name` (string)
    Name of the entity.

  - `items.co2eMetricTon` (number)
    CO2 equivalent generation in metric tons.

  - `count` (integer, required)

  - `total` (integer, required)

  - `offset` (integer, required)

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


