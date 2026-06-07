---
title: "GET /sustainability-insight-ctr/v1beta1/usage-totals"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/openapi/usages/getusagetotals.md"
scraped_at: "2026-06-07T06:16:20.967761+00:00Z"
---

# Total aggregated data

Returns the total aggregated power cost, power consumption, and carbon emissions over a defined time frame and supports filtering by entities.

Endpoint: GET /sustainability-insight-ctr/v1beta1/usage-totals
Version: v1beta1
Security: bearer

## Query parameters:

  - `start-time` (string, required)
    Start of the query's time range in ISO8601 format.

  - `end-time` (string, required)
    End of the aggregate's time range in ISO8601 format.

  - `filter` (string)
    Limit the entities operated on by this endpoint, returning only the usage for entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq", "in", and "and" operators only.
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

  - `filter-tags` (string)
    Limit the entities operated on by this endpoint, returning only the subset of entities that contain the tags. The filter grammar is a subset of OData 4.0 supporting "eq" and "or" operators only.
The tag key is on the left of the operator, the value is on the right.

  - `currency` (string)
    The 3 letter currency code the cost returned will be in, case insensitive. Currency calculations are done via a factor queried at the beginning of the day. Defaults to USD.
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.type` (string, required)
    Type of returned aggregate.

  - `items.cost` (number)
    Total energy cost in the provided currency type.

  - `items.currency` (string)
    The currency code of the returned cost
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

  - `items.co2eMetricTon` (number)
    Total CO2 equivalent generation in metric tons.

  - `items.kwh` (number)
    Total power consumption in kWh.

  - `items.costUsd` (number)
    Total energy cost in USD.

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


