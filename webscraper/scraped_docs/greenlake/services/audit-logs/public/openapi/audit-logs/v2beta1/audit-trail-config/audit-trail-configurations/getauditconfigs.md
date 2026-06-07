---
title: "GET /audit-log/v2beta1/configs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-config/audit-trail-configurations/getauditconfigs.md"
scraped_at: "2026-06-07T06:16:38.081273+00:00Z"
---

# Get the unified audit configurations for the given list of service offer IDs.

Up to 5 service offer Ids can be passed in the query parameter. This API accepts valid 1.x tokens.

Endpoint: GET /audit-log/v2beta1/configs
Version: v2beta1
Security: Bearer

## Query parameters:

  - `svc-offer-ids` (string, required)
    Provide the list of service offer IDs (comma separated) to fetch unified audit configuration.
    Example: "567567-cd79-4a22-b583-bc4aa7e42fcd, 373b7710-cd79-4a22-b583-bc4aa7e42fcd"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Reference ID for the configuration.
    Example: "373b7710-cd79-4a22-b583-bc4aa7e42fcd"

  - `type` (string, required)
    The type of the resource.

  - `config` (object, required)
    The configuration for the resource.

  - `config.categories` (array, required)

  - `config.fixedColumns` (array, required)

  - `config.fixedColumns.order` (integer, required)
    Order of the column

  - `config.fixedColumns.displayName` (string, required)
    The display name of the column in the UI.

  - `config.fixedColumns.responsePath` (string, required)
    The response path of the column in the API response.

  - `config.fixedColumns.isFilterable` (boolean, required)
    A boolean declaring if the column is filterable or not. Set to true if the column is filterable.

  - `config.fixedColumns.svcOfferId` (string)
    The service offer ID for which the column is applicable. If not provided, the column applies to all service offers.
    Example: "373b7710-cd79-4a22-b583-bc4aa7e42fcd"

  - `config.additionalColumns` (array, required)

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

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

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


