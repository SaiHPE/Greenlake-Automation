---
title: "GET /sustainability-insight-ctr/v1beta1/ingests/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/ingests/getingest.md"
scraped_at: "2026-06-07T06:16:26.424141+00:00Z"
---

# Get metadata for a 3rd party device measurement.

Get metadata for an ingested 3rd party device measurement.

Endpoint: GET /sustainability-insight-ctr/v1beta1/ingests/{id}
Version: v1beta1
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID of the record

## Response 200 fields (application/json):

  - `id` (string, required)
    ID of the returned record

  - `type` (string, required)
    Type of returned record

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    The server-side creation time of this resource in ISO8601 format.

  - `updatedAt` (string, required)
    The server-side last updated time of this resource in ISO8601 format.

  - `name` (string)
    Name of the record

  - `description` (string)
    Description of the ingest

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


