---
title: "PATCH /locations/v1/locations/tags"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/updatetags.md"
scraped_at: "2026-06-07T06:15:30.770059+00:00Z"
---

# Create or delete a tag

Use this API to create or delete a tag. In the request body, provide: The tag name and tag value in the appropriate array to create (createTags) or delete (deleteTags) tags as needed.The location ID.

Endpoint: PATCH /locations/v1/locations/tags
Version: v1
Security: Bearer

## Request fields (application/merge-patch+json):

  - `createTags` (array)
    An array of key-value pairs to create new tags.

  - `createTags.id` (string)
    The unique identifier of the tag.

  - `createTags.name` (string)
    The tag name.

  - `createTags.value` (string)
    The tag value.

  - `deleteTags` (array)
    An array of key-value pairs to delete existing tags.

  - `locationId` (string)
    The unique identifier of the location.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the tag.

  - `type` (string, required)
    The type of the resource.

  - `createdAt` (string, required)
    The date and time the tag was created.

  - `updatedAt` (string, required)
    Date and time of the last update to the tag.

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `createTags` (array)
    Location Tags to be created

  - `createTags.name` (string)
    The tag name.

  - `createTags.value` (string)
    The tag value.

  - `deleteTags` (array)
    Location Tags to be deleted

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

## Response 409 fields (application/json):

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


