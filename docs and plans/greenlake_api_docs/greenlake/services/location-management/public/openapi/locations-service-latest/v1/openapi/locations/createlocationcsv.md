---
title: "POST /locations/v1/locations/locations-csv-upload"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/createlocationcsv.md"
scraped_at: "2026-06-07T06:15:31.243414+00:00Z"
---

# Create locations using CSV file

Create locations using a CSV file and store the associated information.

Endpoint: POST /locations/v1/locations/locations-csv-upload
Version: v1
Security: Bearer

## Request fields (multipart/form-data):

  - `Location Name(Required)` (string, required)
    The name of the location to be created.

  - `Street Address(Required)` (string, required)
    The street address of the location to be created.

  - `City(Required)` (string, required)
    The city of the location to be created.

  - `State/Province(Required)` (string, required)
    The state of the location to be created.

  - `Country(Required)` (string, required)
    The country of the location to be created.

  - `Zip/Postal Code(Required)` (string, required)
    The postal code of the location to be created.

  - `Primary Contact Email(optional)` (string)
    The email of the primary contact.

  - `First Name(Required)` (string)
    First name of the primary contact. Required only when the email provided is a NON GLP email.

  - `Last Name(Required)` (string)
    Last name of the primary contact. Required only when the email provided is a NON GLP email.

  - `Tag 1 Name (optional)` (string)
    Tag name associated with the location.

  - `Tag 1 Value (optional)` (string)
    Tag value for the tag name associated with the location.

## Response 202 fields (application/json):

  - `id` (string, required)
    CSV upload operation generated ID.

  - `result` (object, required)

  - `result.totalCount` (integer)

  - `result.succeededCount` (integer)
    Number of locations created successfully.

  - `result.failedCount` (integer)
    The number of failed location creations.

  - `result.failedRecords` (array)

  - `result.failedRecords.error` (object)

  - `result.failedRecords.error.message` (string)

  - `result.failedRecords.error.statusCode` (integer)

  - `result.failedRecords.name` (string)

  - `result.succeededRecords` (array)

  - `result.succeededRecords.id` (string)
    The location ID created from a CSV upload.

  - `result.succeededRecords.name` (string)
    The location name created from a CSV upload.

  - `result.errorMessage` (string)

  - `type` (string, required)
    The type of the resource.

  - `status` (string)
    The status of the CSV upload operation.
    Enum: "INITIALIZED", "IN_PROGRESS", "SUCCEEDED", "FAILED"

  - `startedAt` (string)
    The date and time the CSV upload operation started.

  - `endedAt` (string)
    The date and time the CSV upload operation ended.

  - `progressPercent` (integer)
    Progress percentage of the CSV upload operation.

  - `suggestedPollingIntervalSeconds` (integer)
    The polling interval of the CSV upload operation.

  - `timeoutMinutes` (integer)

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


