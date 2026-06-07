---
title: "POST /wellness/v2/support-cases"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/support-cases/createsupportcase.md"
scraped_at: "2026-06-07T06:16:34.981308+00:00Z"
---

# Create a support case

Create a support case for a wellness event. This is an asynchronous operation. Use the URI specified in the Location response header to retrieve the status of the case creation operation.

Endpoint: POST /wellness/v2/support-cases
Version: v2
Security: Bearer

## Request fields (application/json):

  - `event` (object)
    Reference to the wellness event.

  - `event.resourceUri` (string, required)
    URI to the wellness event

  - `event.id` (string, required)
    Unique ID of the the wellness event

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

## Response 409 fields (application/json):

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


## Response 202 fields

## Response 429 fields
