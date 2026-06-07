---
title: "PATCH /locations/v1/locations/update/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service/openapi/locations/managelocation.md"
scraped_at: "2026-06-07T06:15:29.033862+00:00Z"
---

# Manage a location

Manage the location information for a location specified by its location ID. Provide information in the request body schema to create, update, or delete the location's address, contact, or location details. Only include the fields that need to be modified in the request body. Fields that are not included will remain unchanged.

Endpoint: PATCH /locations/v1/locations/update/{id}
Version: v1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The unique identifier for the location. For example, 945e70ec-b043-4cad-9ed0-069c06fdb8af.

## Request fields (application/merge-patch+json):

  - `addresses` (object)

  - `addresses.add` (array)
    Add new location address information.

  - `addresses.add.city` (string, required)
    The location's city.

  - `addresses.add.country` (string, required)
    The location's country.

  - `addresses.add.postalCode` (string, required)
    The location's postal code.

  - `addresses.add.state` (string, required)
    The location's state or region.

  - `addresses.add.streetAddress` (string, required)
    The location's street address.

  - `addresses.add.type` (string, required)
    Only addresses of type “shipping_receiving” can be added during an add operation.
    Enum: "shipping_receiving"

  - `addresses.add.id` (string)
    The unique identifier of the address.

  - `addresses.add.locationId` (string)
    The unique identifier of the location.

  - `addresses.add.streetAddress2` (string)
    The location's street address.

  - `addresses.delete` (array)
    Delete location address information by providing the address ID (UUID). Note that "street" type addresses cannot be deleted.

  - `addresses.update` (array)
    Update location address information.

  - `addresses.update.type` (string, required)
    Must match the existing address type. The address type cannot be changed during an update operation.
    Enum: "street", "shipping_receiving"

  - `addresses.update.city` (string)
    The city the location is in.

  - `addresses.update.country` (string)
    The country the location is in.

  - `addresses.update.state` (string)
    The location's state.

  - `addresses.update.streetAddress` (string)
    The location's address.

  - `addresses.update.streetAddress2` (string)
    The location's address.

  - `contacts` (object)

  - `contacts.add` (array)
    Add location contact information.

  - `contacts.add.email` (string, required)
    The email address associated with the contact.

  - `contacts.add.name` (string, required)
    The name of the contact. For API-created locations with a non-GLP email, append "NONGLP" to the name (e.g., "John Doe NONGLP").

  - `contacts.add.type` (string, required)
    The type of contact.
    Enum: "primary", "shipping_receiving", "security", "operations"

  - `contacts.add.id` (string)
    The unique identifier of the contact.

  - `contacts.add.phoneNumber` (string)
    The phone number associated with the contact.

  - `contacts.delete` (array)
    Delete location contact information.

  - `locationDetails` (object)

  - `locationDetails.description` (string)
    A description of the location.

  - `locationDetails.expiredAt` (string)
    The date and time the location expired.

  - `locationDetails.locationType` (string)
    Enum: "building"

  - `locationDetails.name` (string)
    The name of the location.

  - `locationDetails.validated` (boolean)
    A boolean confirming whether the location has been validated or not.

  - `locationDetails.validatedAt` (string)
    The date the location was validated in the format mm-dd-yyyy.

  - `locationDetails.validatedByEmail` (string)
    The email address of the workspace user that validated the location.

  - `locationDetails.validatedByName` (string)
    The name of the workspace user that validated the location.

  - `locationDetails.validationCycle` (string)
    Enum: "", "6", "12", "18"

  - `locationDetails.validationExpired` (boolean)

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


