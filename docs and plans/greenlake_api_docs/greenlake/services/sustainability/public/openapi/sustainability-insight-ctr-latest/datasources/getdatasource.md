---
title: "GET /sustainability-insight-ctr/v1beta1/datasources/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/datasources/getdatasource.md"
scraped_at: "2026-06-07T06:16:26.442700+00:00Z"
---

# Get information for a SIC data source.

Get information such as name and data collection times for a SIC data source.

Endpoint: GET /sustainability-insight-ctr/v1beta1/datasources/{id}
Version: v1beta1
Security: bearer

## Path parameters:

  - `id` (string, required)
    ID of the data source

## Response 200 fields (application/json):

  - `id` (string, required)
    ID of the returned datasource record

  - `type` (string, required)
    Type of returned datasource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    The server-side creation time of this resource in ISO8601 format.

  - `updatedAt` (string, required)
    The server-side last updated time of this resource in ISO8601 format.

  - `name` (string)
    Name of the datasource

  - `provider` (string)
    Provider name

  - `lastCollectionTime` (string)
    Time of the last collected data for this datasource in ISO8601 format.

  - `firstCollectionTime` (string)
    Time of the first collected data for this datasource in ISO8601 format.

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


