---
title: "PUT /identity/v1/users/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/identity-v1/nb-api-user/update_user_preferences_identity_v1_users__id__put.md"
scraped_at: "2026-06-07T06:15:29.848857+00:00Z"
---

# Update a user

Update an existing user's preferences.

Endpoint: PUT /identity/v1/users/{id}
Version: 1.0.0
Security: BearerAuth

## Path parameters:

  - `id` (string, required)
    The unique identifier of the user to be updated.
    Example: "7600415a-8876-5722-9f3c-b0fd11112283"

## Request fields (application/json):

  - `language` (any)
    The preferred language of the user.
    Enum: "en", "de", "es", "fr", "jp", "br", "cn", "ko", "ru", "it"

  - `idleTimeout` (integer)
    The user's session idle timeout in seconds.

## Response 200 fields (application/json):

  - `message` (string, required)
    Message

## Response 400 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 401 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 412 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 422 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 500 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.


