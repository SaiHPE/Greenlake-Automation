---
title: "POST /sustainability-insight-ctr/v1beta1/coefficients"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/openapi/coefficients/addcoefficients.md"
scraped_at: "2026-06-07T06:16:21.622521+00:00Z"
---

# Create cost and co2 coefficients for a location

Create cost and co2 coefficients for a specific location's data. If a coefficient is provided, either the value must be provided of one of the use default or use current flags must be set. Takes effect after the returned start time.

Endpoint: POST /sustainability-insight-ctr/v1beta1/coefficients
Version: v1beta1
Security: bearer

## Request fields (application/json):

  - `locationId` (string, required)
    The location URI.

  - `co2eGramsPerKwh` (object)

  - `co2eGramsPerKwh.useDefault` (boolean, required)
    Whether or not to use the default coefficient for this location. Cannot be true if useCurrent is also true.

  - `co2eGramsPerKwh.useCurrent` (boolean, required)
    Whether or not to use the preexisting coefficient for this location. Cannot be true if useDefault is also true. Will throw an error if there is no preexisting coefficient.

  - `co2eGramsPerKwh.value` (number)
    The coefficient mapping for this location. Used if neither useDefault or useCurrent flags are true.

  - `costPerKwh` (object)

  - `costPerKwh.currencyCode` (string)
    The 3 letter currency code the cost returned will be in, case insensitive. Currency calculations are done via a factor queried at the beginning of the day.
    Enum: "THB", "CHF", "INR", "EUR", "GBP", "NOK", "USD", "AUD", "SEK", "HKD", "AED", "NZD", "BGN", "RON", "CAD", "UAH", "MXN", "KRW", "JPY", "TRY", "DKK", "PLN", "CZK", "CLP", "CNY", "ILS", "HRK", "BAM", "TWD", "MYR"

  - `costUsdPerKwh` (object)
    Deprecated feature replaced by costPerKwh. Cannot be used in conjunction with costPerKwh and currency fields.

## Response 201 fields (application/json):

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


