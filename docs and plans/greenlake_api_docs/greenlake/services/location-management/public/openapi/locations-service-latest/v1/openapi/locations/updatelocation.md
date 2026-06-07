---
title: "PATCH /locations/v1/locations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/updatelocation.md"
scraped_at: "2026-06-07T06:15:30.779923+00:00Z"
---

# Update a location

Update a location's information by specifying its location ID. Only include the fields that need to be updated in the request body. Fields that are not included in the request body will remain unchanged.
Note: The name and locationType fields are mandatory and cannot be set to empty or invalid values.

Endpoint: PATCH /locations/v1/locations/{id}
Version: v1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier for the location.

## Request fields (application/merge-patch+json):

  - `addresses` (array)

  - `addresses.type` (string, required)
    Must match the existing address type. The address type cannot be changed during an update operation.
    Enum: "street", "shipping_receiving"

  - `addresses.id` (string)
    The unique identifier of the address.

  - `addresses.city` (string)
    The city the location is in.

  - `addresses.country` (string)
    The country the location is in.

  - `addresses.locationId` (string)
    The unique identifier of the location.

  - `addresses.postalCode` (string)
    The location's postal code.

  - `addresses.state` (string)
    The location's state.

  - `addresses.streetAddress` (string)
    The location's address.

  - `addresses.streetAddress2` (string)
    The location's address.

  - `contacts` (array)

  - `contacts.type` (string, required)
    Enum: "primary", "shipping_receiving", "security", "operations"

  - `contacts.email` (string)
    The email address of the contact.

  - `contacts.id` (string)
    The unique identifier of the contact.

  - `contacts.locationId` (string)
    The location ID related to the contact.

  - `contacts.name` (string)
    The name of the contact.

  - `contacts.phoneNumber` (string)
    The phone number associated with the contact.

  - `description` (string)
    A long description of the location.

  - `expiredAt` (string)
    The date the location expired.

  - `name` (string)
    The name of location.

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
    An integer that defines, in months, how long the location remains validated.
    Enum: "", "6", "12", "18"

  - `validationExpired` (boolean)
    A boolean confirming whether the location validation has expired or not.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the location.

  - `type` (string, required)
    The type of the resource.

  - `createdAt` (string, required)
    The date and time the location was created.

  - `updatedAt` (string, required)
    Time of the last update to the location.

  - `generation` (integer, required)
    Monotonically increasing update counter.

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
    Locations can have at most one primary contact but can have more than one of the other contact types.

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

  - `name` (string)
    The name of the location.

  - `locationType` (string)
    Type of location.
    Enum: "building"

  - `description` (string)
    A long descriptions of the location.

  - `expiredAt` (string)
    The date and time the location expired.

  - `validated` (boolean)
    Boolean confirming whether the location has been validated or not.

  - `validatedAt` (string)
    The date and time the location was validated in the format mm-dd-yyyy.

  - `validatedByEmail` (string)
    Email address of the workspace user that validated the location.

  - `validatedByName` (string)
    The name of the workspace user that validated the location.

  - `validationCycle` (string)
    An integer that defines, in months, how long the location remains validated.
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

## Response 403 fields (application/json):

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


