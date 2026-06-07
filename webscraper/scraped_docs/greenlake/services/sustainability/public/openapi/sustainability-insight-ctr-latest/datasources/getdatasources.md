---
title: "GET /sustainability-insight-ctr/v1beta1/datasources"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/datasources/getdatasources.md"
scraped_at: "2026-06-07T06:16:26.501717+00:00Z"
---

# Get all information for SIC data sources.

This returns information such as name and data collection times for each SIC data source.

Endpoint: GET /sustainability-insight-ctr/v1beta1/datasources
Version: v1beta1
Security: bearer

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    ID of the returned datasource record

  - `items.type` (string, required)
    Type of returned datasource

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    The server-side creation time of this resource in ISO8601 format.

  - `items.updatedAt` (string, required)
    The server-side last updated time of this resource in ISO8601 format.

  - `items.name` (string)
    Name of the datasource

  - `items.provider` (string)
    Provider name

  - `items.lastCollectionTime` (string)
    Time of the last collected data for this datasource in ISO8601 format.

  - `items.firstCollectionTime` (string)
    Time of the first collected data for this datasource in ISO8601 format.

  - `count` (integer, required)

  - `total` (integer, required)

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


