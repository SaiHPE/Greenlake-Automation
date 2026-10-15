---
title: "GET /locations/v1/locations/tags"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service/openapi/locations/listalltags.md"
scraped_at: "2026-06-07T06:15:29.114311+00:00Z"
---

# Get tags for a workspace

Retrieve tag information for your workspace.

Endpoint: GET /locations/v1/locations/tags
Version: v1
Security: Bearer

## Query parameters:

  - `limit` (integer, required)
    The maximum number of results to be returned.

  - `offset` (integer)
    The zero-based resource offset to start the response from.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.name` (string, required)
    The tag name.

  - `items.value` (string, required)
    The tag value.

  - `items.createdAt` (string, required)
    The date the location was created.

  - `count` (integer, required)
    The number of items returned.

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer)
    The total number of items in the collection that match the filter query, if one was provided in the request.

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
