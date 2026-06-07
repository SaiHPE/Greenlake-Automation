---
title: "POST /internal-subscriptions/v1alpha1/subscriptions/auto-complete"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription/openapi-internal/internal-subscriptions-v1alpha1/autocompletedevicesv1alpha1.md"
scraped_at: "2026-06-07T06:15:53.288737+00:00Z"
---

# Auto-complete subscription information

Returns auto-completion suggestions for a given prefix or query.

Endpoint: POST /internal-subscriptions/v1alpha1/subscriptions/auto-complete
Version: latest
Security: Bearer

## Header parameters:

  - `CCS-Platform-Customer-Id` (string, required)
    Platform customer identifier.

  - `CCS-Transaction-Id` (string, required)
    Transaction identifier for traceability.

## Query parameters:

  - `limit` (integer)
    Maximum results to return (default 10, max 10).

## Request fields (application/json):

  - `searchText` (string)
    The search query string.

## Response 200 fields (application/json):

  - `completion` (object)
    Completion context and suggestion set.

  - `completion.prefix` (string)
    Input prefix used to generate suggestions.
    Example: "ser"

  - `completion.suggestions` (array)
    Ranked suggestion list.

  - `completion.suggestions.value` (string)
    Suggested full value.

  - `completion.suggestions.highlight` (string)

  - `completion.suggestions.relevance` (number)
    Numeric relevance score.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetail` (array)

  - `errorDetail.type` (string, required)
    The type of error details.

  - `errorDetail.issues` (array, required)
    An array of bad request issues.

  - `errorDetail.issues.source` (string)
    The source of the error.

  - `errorDetail.issues.subject` (string)
    The specific issue key.

  - `errorDetail.issues.description` (string)
    A brief explanation of the error.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error.

  - `errorDetails.source` (string, required)
    The source of the error.

  - `errorDetails.metadata` (object, required)
    Additional key value pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64343c3c-3016-4234-baee-765651aa4bb3"

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


