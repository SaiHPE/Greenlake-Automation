---
title: "GET /locations/v1/locations/address/revgeocode"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service/openapi/locations/reversegeocode.md"
scraped_at: "2026-06-07T06:15:29.681294+00:00Z"
---

# Retrieve location from latitude and longitude.

Geolocate a location by providing the longitude and latitude. Optionally, provide an ISO language code to return the information in a language different from the default (English).

Endpoint: GET /locations/v1/locations/address/revgeocode
Version: v1
Security: Bearer

## Query parameters:

  - `latitude` (string, required)
    Provide a latitude coordinate.

  - `longitude` (string, required)
    Provide a longitude coordinate.

  - `language` (string)
    (Optional) Specify a language code to return the location information in that language. The default is English.

## Response 200 fields (application/json):

  - `label` (string)
    Full address label.

  - `countryCode` (string)
    ISO country code.

  - `countryName` (string)
    Country name.

  - `stateCode` (string)
    State or province code.

  - `state` (string)
    State or province name.

  - `county` (string)
    County name.

  - `city` (string)
    City name.

  - `street` (string)
    Street address.

  - `postalCode` (string)
    Postal or ZIP code.

  - `lat` (number)
    Latitude coordinate.

  - `lng` (number)
    Longitude coordinate.

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    Unique error code identifier (e.g., HPE_GL_LM_BAD_REQUEST).

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error for debugging purposes.

  - `httpStatusCode` (string, required)
    HTTP equivalent status code.

  - `errorDetails` (array)
    Additional details about the error.

  - `errorDetails.type` (string)
    Type of error detail (e.g., hpe.greenlake.metadata).

  - `errorDetails.source` (string)
    Source of the error (e.g., hpe.greenlake.lm).

  - `errorDetails.metadata` (object)
    Additional metadata about the error.

  - `errorDetails.metadata.error` (string)
    Detailed error message.

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique error code identifier (e.g., HPE_GL_LM_BAD_REQUEST).

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error for debugging purposes.

  - `httpStatusCode` (string, required)
    HTTP equivalent status code.

  - `errorDetails` (array)
    Additional details about the error.

  - `errorDetails.type` (string)
    Type of error detail (e.g., hpe.greenlake.metadata).

  - `errorDetails.source` (string)
    Source of the error (e.g., hpe.greenlake.lm).

  - `errorDetails.metadata` (object)
    Additional metadata about the error.

  - `errorDetails.metadata.error` (string)
    Detailed error message.


## Response 404 fields
