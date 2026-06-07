---
title: "PUT /audit-log/v2beta1/configs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/updateauditconfigs.md"
scraped_at: "2026-06-07T06:16:38.540647+00:00Z"
---

# Update service audit configurations.

This API accepts valid 1.x tokens.

Endpoint: PUT /audit-log/v2beta1/configs
Version: v2beta1
Security: Bearer

## Request fields (application/json):

  - `serviceOfferIds` (array, required)

  - `config` (object, required)

  - `config.categories` (array, required)

  - `config.additionalColumns` (array)

  - `config.additionalColumns.order` (integer, required)
    Order of the column

  - `config.additionalColumns.displayName` (string, required)
    The display name of the column in the UI.

  - `config.additionalColumns.responsePath` (string, required)
    The response path of the column in the API response.

  - `config.additionalColumns.isFilterable` (boolean, required)
    A boolean declaring if the column is filterable or not. Set to true if the column is filterable.

## Response 200 fields (application/json):

  - `message` (string)
    Example: "Audit configurations updated successfully."

## Response 403 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

## Response 429 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)
    Additional detailed information about the error.

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


