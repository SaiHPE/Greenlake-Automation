---
title: "GET /locations/v1/locations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/getlocationby.md"
scraped_at: "2026-06-07T06:15:30.643863+00:00Z"
---

# Retrieve a location

Return information for a location specified by a location ID.

Endpoint: GET /locations/v1/locations/{id}
Version: v1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique indentifier of the location. For example, 945e70ec-b043-4cad-9ed0-069c06fdb8af.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier for the location.

  - `addresses` (array)

  - `addresses.city` (string)
    The location's city.

  - `addresses.country` (string)
    The location's country.

  - `addresses.id` (string)
    A unique identifier for the address.

  - `addresses.postalCode` (string)
    The locations postal code.

  - `addresses.state` (string)
    The location's state or region.

  - `addresses.streetAddress` (string)
    The location's address.

  - `addresses.streetAddress2` (string)
    The location's address.

  - `addresses.type` (string)
    The type of address.
    Enum: "street", "shipping_receiving"

  - `addresses.lat` (string)
    Latitude coordinate of the address.

  - `addresses.lng` (string)
    Longitude coordinate of the address.

  - `contacts` (array)

  - `contacts.email` (string)
    The email address of the contact.

  - `contacts.id` (string)
    The unique identifer of the contact.

  - `contacts.name` (string)
    The name of the contact.

  - `contacts.phoneNumber` (string)
    The phone number associated with the contact.

  - `contacts.type` (string)
    Enum: "primary", "shipping_receiving", "security", "operations"

  - `description` (string)
    A long description of the location.

  - `expiredAt` (string)
    The date the location expired.

  - `name` (string)
    The name of the location.

  - `locationType` (string)
    Type of location.
    Enum: "building"

  - `validated` (boolean)
    Boolean confirming whether the location has been validated or not.

  - `validatedAt` (string)
    The date the location was validated in the format mm-dd-yyyy.

  - `validatedByEmail` (string)
    Email address of the workspace user that validated the location.

  - `validatedByName` (string)
    The name of the workspace user that validated the location.

  - `validationCycle` (string)
    An integer in months that defines how long the location remains validated.
    Enum: "", "6", "12", "18"

  - `validationExpired` (boolean)
    A boolean confirming whether the location validation has expired or not.

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


