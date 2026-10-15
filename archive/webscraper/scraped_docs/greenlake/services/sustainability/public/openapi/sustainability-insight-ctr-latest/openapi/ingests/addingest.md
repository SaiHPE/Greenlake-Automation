---
title: "POST /sustainability-insight-ctr/v1beta1/ingests"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/openapi/ingests/addingest.md"
scraped_at: "2026-06-07T06:16:21.677403+00:00Z"
---

# Upload a document with 3rd party device measurement data.

Allows a user to upload power measurements for 3rd party devices from their own configured ITOM applications.

Endpoint: POST /sustainability-insight-ctr/v1beta1/ingests
Version: v1beta1
Security: bearer

## Request fields (multipart/form-data):

  - `name` (string)
    The name of the device measurements being uploaded.

  - `description` (string)
    Description for this record

  - `file` (string)
    The 3rd party device measurement file. Must be .csv and matching the SIC third party data template. Maximum size is 300MB. Files that are invalid will not be consumed.

## Response 201 fields (application/json):

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


