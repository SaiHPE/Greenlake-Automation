---
title: "PATCH /wellness/v2/events/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/events/updateevent.md"
scraped_at: "2026-06-07T06:16:33.912054+00:00Z"
---

# Update wellness event with specific ID

Update a wellness event identified by the given ID. Only the attributes flag, read, and archive can be updated.

Endpoint: PATCH /wellness/v2/events/{id}
Version: v2
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Event ID

## Request fields (application/merge-patch+json):

  - `read` (boolean)
    Boolean indicating the read status of the wellness event.

  - `flag` (boolean)
    Boolean indicating whether the wellness event is flagged or not.

  - `archive` (boolean)
    Boolean indicating whether the wellness event is archived or not.

## Response 200 fields (application/json):

  - `event` (object)
    Reference to the wellness event.

  - `event.resourceUri` (string, required)
    URI to the wellness event

  - `event.id` (string, required)
    Unique ID of the the wellness event

  - `success` (boolean)
    Indicates whether the event identified by the ID was updated or not.

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 404 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 422 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code


## Response 429 fields
