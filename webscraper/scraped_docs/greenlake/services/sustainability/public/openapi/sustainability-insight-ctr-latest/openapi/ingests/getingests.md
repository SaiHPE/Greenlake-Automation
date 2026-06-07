---
title: "GET /sustainability-insight-ctr/v1beta1/ingests"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/openapi/ingests/getingests.md"
scraped_at: "2026-06-07T06:16:21.692022+00:00Z"
---

# Get all metadata of uploaded 3rd party device measurements.

This returns the associated metadata of each uploaded 3rd party device measurement.

Endpoint: GET /sustainability-insight-ctr/v1beta1/ingests
Version: v1beta1
Security: bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from.

  - `limit` (integer)
    Number of ingested records to return.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the returned record

  - `items.type` (string, required)
    Type of returned record

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    The server-side creation time of this resource in ISO8601 format.

  - `items.updatedAt` (string, required)
    The server-side last updated time of this resource in ISO8601 format.

  - `items.name` (string)
    Name of the record

  - `items.description` (string)
    Description of the ingest

  - `count` (integer, required)

  - `total` (integer, required)

  - `offset` (integer, required)

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.

## Response 429 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code.


