---
title: "GET /identity/v1/users/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/identity-v1/nb_openapi_identity/nb-api-user/get_user_detailed_identity_v1_users__id__get.md"
scraped_at: "2026-06-07T06:15:27.490093+00:00Z"
---

# Get a user

Retrieve a single user based on a given user ID.

Endpoint: GET /identity/v1/users/{id}
Version: 1.0.0
Security: BearerAuth

## Path parameters:

  - `id` (string, required)
    The unique identifier of the user.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 200 fields (application/json):

  - `id` (string, required)
    Resource unique identification

  - `type` (string, required)
    Type of data

  - `username` (string, required)
    User's Email Address

  - `generation` (integer)
    Resource history of updates

  - `createdAt` (string)
    The time the resource was created.

  - `updatedAt` (string)
    The time the resource was last updated.

  - `firstName` (string)
    User's first name

  - `lastName` (string)
    User's last name

  - `userStatus` (any)
    On-Boarding Status of a user
    Enum: "UNVERIFIED", "VERIFIED", "BLOCKED", "DELETE_IN_PROGRESS", "DELETED", "SUSPENDED"

  - `lastLogin` (string)
    Time when this user had last logged in.

  - `resourceUri` (string)
    Full path of the resource

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

## Response 403 fields (application/json):

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


