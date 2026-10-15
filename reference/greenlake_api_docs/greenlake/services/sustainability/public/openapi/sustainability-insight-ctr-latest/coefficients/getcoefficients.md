---
title: "GET /sustainability-insight-ctr/v1beta1/coefficients"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/coefficients/getcoefficients.md"
scraped_at: "2026-06-07T06:16:25.867241+00:00Z"
---

# Get all cost and co2 coefficients

Get a list of all costs (amount per kWh) and co2 coefficients of all locations. Supports filtering by locationId.

Endpoint: GET /sustainability-insight-ctr/v1beta1/coefficients
Version: v1beta1
Security: bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from.

  - `limit` (integer)
    Number of entities to return.

  - `filter` (string)
    Limit the coefficients operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq" operator only.
Coefficients can be filtered by:
- locationId

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the returned coefficient mapping

  - `items.type` (string, required)
    Type of returned coefficient mapping

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    The server-side creation time of this resource in ISO8601 format.

  - `items.updatedAt` (string, required)
    The server-side last updated time of this resource in ISO8601 format.

  - `items.associatedLocation` (object)
    A reference to the Location resource that this coefficient is bound to.

  - `items.associatedLocation.locationId` (string, required)
    The location id that the coefficients apply to.

  - `items.associatedLocation.locationName` (string, required)
    The location name that the coefficients apply to

  - `items.associatedLocation.resourceUri` (string, required)

  - `items.startTime` (string)
    The date in which this coefficient mapping takes effect for this location in ISO8601 format.

  - `items.co2eGramsPerKwh` (number)
    The CO2 equivalent generation coefficient in grams per kilowatt-hour for this location. Null if default for this location.

  - `items.costPerKwh` (number)
    The cost coefficient per kilowatt-hour for this location. Null if default for this location.

  - `items.currency` (object)
    The currency code and currency name of the returned cost

  - `items.currency.currencyCode` (string, required)
    The currency code of the returned cost
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

  - `items.currency.currencyName` (string, required)
    The name of the currency

  - `items.costUsdPerKwh` (number)
    The cost coefficient in USD per kilowatt-hour for this location. Null if default for this location.

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


