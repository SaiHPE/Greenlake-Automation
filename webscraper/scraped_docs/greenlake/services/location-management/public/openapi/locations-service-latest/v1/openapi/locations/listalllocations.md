---
title: "GET /locations/v1/locations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/listalllocations.md"
scraped_at: "2026-06-07T06:15:30.458524+00:00Z"
---

# Lists all locations

Retrieve location information for all locations.

Endpoint: GET /locations/v1/locations
Version: v1
Security: Bearer

## Query parameters:

  - `limit` (integer, required)
    The maximum number of results to be returned.

  - `offset` (integer)
    The zero-based resource offset to start the response from.

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0. This API can be filtered by name. NOTE: The filter query parameter must use URL encoding. Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL. The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the location.

  - `items.city` (string)
    The location's city.

  - `items.country` (string)
    The location's country.

  - `items.expiredAt` (string)
    The date the location expired.

  - `items.name` (string)
    The name of the location.

  - `items.validated` (boolean)
    Boolean confirming whether the location has been validated or not.

  - `items.validatedAt` (string)
    The date the location was validated in the format mm-dd-yyyy.

  - `items.validatedByEmail` (string)
    Email address of the workspace user that validated the location.

  - `items.validatedByName` (string)
    The name of the workspace user that validated the location.

  - `items.validationCycle` (string)
    An integer that defines how long, in months, the location remains validated.
    Enum: "", "6", "12", "18"

  - `items.validationExpired` (boolean)
    A boolean confirming whether the location validation has expired or not.

  - `items.lat` (string)
    Latitude coordinate of the location.

  - `items.lng` (string)
    Longitude coordinate of the location.

  - `items.tags` (array)
    Tags associated with the location.

  - `items.tags.id` (string)
    The unique identifier of the tag.

  - `items.tags.name` (string)
    The tag name.

  - `items.tags.value` (string)
    The tag value.

  - `count` (integer, required)
    Number of items returned

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request.

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
