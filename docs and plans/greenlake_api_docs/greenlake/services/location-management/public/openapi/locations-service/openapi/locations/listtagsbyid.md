---
title: "GET /locations/v1/locations/tags/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service/openapi/locations/listtagsbyid.md"
scraped_at: "2026-06-07T06:15:29.504253+00:00Z"
---

# Retrieves tags for given a location

Return a listing of all tag names and tag values for a given location. If a location has no tags, only the location ID and location name are returned.

Endpoint: GET /locations/v1/locations/tags/{id}
Version: v1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier of the location. For example, 945e70ec-b043-4cad-9ed0-069c06fdb8af.

## Response 200 fields (application/json):

  - `locationId` (string, required)
    The unique identifier for the location.

  - `locationName` (string, required)
    The name of the location.

  - `tags` (array)
    An array of tag names and values. The array is empty if the location has no associated tags.

  - `tags.id` (string)
    The unique identifier of the tag.

  - `tags.name` (string)
    The tag name.

  - `tags.value` (string)
    The tag value.

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

## Response 404 fields (application/json):

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


