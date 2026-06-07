---
title: "GET /sustainability-insight-ctr/v1beta1/usage-by-entity"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getusagebyentity.md"
scraped_at: "2026-06-07T06:16:25.682053+00:00Z"
---

# Aggregated energy use for entities

Retrieves an aggregated energy usage list grouped by individual entities over a defined time frame and supports filtering, sorting, and offset-based pagination.

Endpoint: GET /sustainability-insight-ctr/v1beta1/usage-by-entity
Version: v1beta1
Security: bearer

## Query parameters:

  - `start-time` (string, required)
    Start of the query's time range in ISO8601 format.

  - `end-time` (string, required)
    End of the query's time range in ISO8601 format.

  - `filter` (string)
    Limit the entities operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only.
Usage entities can be filtered by:
- entityId
- entityMake
- entityModel
- entityType
- entitySerialNum
- entityProductId
- locationName
- locationId
- locationCity
- locationState
- locationCountry
- name

  - `filter-tags` (string)
    Limit the entities operated on by this endpoint, returning only the subset of entities that contain the tags. The filter grammar is a subset of OData 4.0 supporting "eq" and "or" operators only.
The tag key is on the left of the operator, the value is on the right.

  - `currency` (string)
    The 3 letter currency code the cost returned will be in, case insensitive. Currency calculations are done via a factor queried at the beginning of the day. Defaults to USD.
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

  - `sort` (string)
    Odata 4.0 field to sort entities on. Allowed fields are the strings "locationName", "locationCountry", "locationState", "entityId", "entityMake", "entityModel", "entityType", "entitySerialNum", "entityProductId", "name". Must be of the format "property order".

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

  - `items.entityMake` (string)
    Make of the entity.

  - `items.entityModel` (string)
    Model of the entity.

  - `items.entityType` (string)
    Type of the entity.

  - `items.entitySerialNum` (string)
    Serial number of the entity.

  - `items.entityProductId` (string)
    Product ID of the entity.

  - `items.entityManufacturerTimestamp` (string)
    Manufacturing timestamp of the entity.

  - `items.locationId` (string)
    ID of the entity location.

  - `items.locationCity` (string)
    City that the the entity is located in.

  - `items.locationName` (string)
    The entity location name.

  - `items.locationState` (string)
    State that the the entity is located in.

  - `items.locationCountry` (string)
    Country that the the entity is located in.

  - `items.name` (string)
    Name of the entity.

  - `items.tags` (array)
    List of the entity's tags

  - `items.tags.name` (string, required)
    The name of the tag

  - `items.tags.value` (string, required)
    The value of the tag

  - `items.cost` (number)
    Energy cost in the provided currency type.

  - `items.currency` (string)
    The currency code of the returned cost
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

  - `items.co2eMetricTon` (number)
    CO2 equivalent generation in metric tons.

  - `items.kwh` (number)
    Power consumption in kWh.

  - `items.costUsd` (number)
    Energy cost in USD.

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


