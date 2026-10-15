---
title: "POST /audit-log/v2beta1/configs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/createauditconfigs.md"
scraped_at: "2026-06-07T06:16:38.240762+00:00Z"
---

# Create external service audit configurations.

This API helps to create audit configurations. This API accepts valid 1.x tokens.

Endpoint: POST /audit-log/v2beta1/configs
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

## Response 201 fields (application/json):

  - `message` (string)
    Example: "Audit configurations created successfully."

## Response 400 fields (application/json):

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
    Error type

  - `errorDetails.issues` (array, required)
    List of bad request issues

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.

  - `errorDetails.issues.subject` (string, required)
    The specific issue key. For example, if the source property is field, the subject is the dot-separated property name the issue is about.

  - `errorDetails.issues.description` (string)
    A human-readable description of the issue.

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


