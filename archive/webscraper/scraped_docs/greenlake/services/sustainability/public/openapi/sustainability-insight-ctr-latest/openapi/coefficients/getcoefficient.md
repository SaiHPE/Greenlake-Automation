---
title: "GET /sustainability-insight-ctr/v1beta1/coefficients/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/openapi/coefficients/getcoefficient.md"
scraped_at: "2026-06-07T06:16:21.643806+00:00Z"
---

# Get a single cost and co2 coefficient for an id

Get a single cost and co2 coefficient for an id

Endpoint: GET /sustainability-insight-ctr/v1beta1/coefficients/{id}
Version: v1beta1
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID of the coefficient mapping

## Response 200 fields (application/json):

  - `id` (string, required)
    ID of the returned coefficient mapping

  - `type` (string, required)
    Type of returned coefficient mapping

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    The server-side creation time of this resource in ISO8601 format.

  - `updatedAt` (string, required)
    The server-side last updated time of this resource in ISO8601 format.

  - `associatedLocation` (object)
    A reference to the Location resource that this coefficient is bound to.

  - `associatedLocation.locationId` (string, required)
    The location id that the coefficients apply to.

  - `associatedLocation.locationName` (string, required)
    The location name that the coefficients apply to

  - `associatedLocation.resourceUri` (string, required)

  - `startTime` (string)
    The date in which this coefficient mapping takes effect for this location in ISO8601 format.

  - `co2eGramsPerKwh` (number)
    The CO2 equivalent generation coefficient in grams per kilowatt-hour for this location. Null if default for this location.

  - `costPerKwh` (number)
    The cost coefficient per kilowatt-hour for this location. Null if default for this location.

  - `currency` (object)
    The currency code and currency name of the returned cost

  - `currency.currencyCode` (string, required)
    The currency code of the returned cost
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

  - `currency.currencyName` (string, required)
    The name of the currency

  - `costUsdPerKwh` (number)
    The cost coefficient in USD per kilowatt-hour for this location. Null if default for this location.

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


