---
title: "DELETE /data-services/v1beta1/secrets/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secrets/removesecretv1.md"
scraped_at: "2026-06-07T06:15:22.066687+00:00Z"
---

# Removes a secret

Removes the specified secret. All associated assignments will also be removed.

Endpoint: DELETE /data-services/v1beta1/secrets/{id}
Version: 1.3.0
Security: 

## Path parameters:

  - `id` (string, required)
    UUID of the secret

## Query parameters:

  - `safe` (boolean)
    Enable delete-lock safety checking

## Header parameters:

  - `x-envoy-external-address` (string)

  - `x-forwarded-for` (string)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 412 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID


## Response 204 fields
