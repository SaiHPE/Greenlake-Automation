---
title: "GET /accounts/v1/users/user-info"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/identity-v1/app_openapi_user/app-instance-user-management/get_the_users_with_given_user_username.md"
scraped_at: "2026-06-07T06:15:27.414824+00:00Z"
---

# Get the user details with given user username

Get the users with given user username

Endpoint: GET /accounts/v1/users/user-info
Version: 1.0.0
Security: Bearer

## Query parameters:

  - `filter` (string, required)
    Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter.

Get user's global id and assert its membership to a workspace with the given username

## Response 200 fields (application/json):

  - `offset` (integer, required)
    Specifies the offset of the returned page

  - `count` (integer, required)
    The number of returned items

  - `total` (integer, required)
    The total number of items in the result set

  - `items` (array, required)
    List of Workspaces

  - `items.id` (string, required)
    The GlobalId for this username.

  - `items.type` (string, required)
    Type of data

  - `items.firstName` (string)
    first name of the user

  - `items.lastName` (string)
    last name of the user

  - `items.generation` (integer)
    Resource history of updates

  - `items.createdAt` (string)
    The time the resource was created.

  - `items.updatedAt` (string)
    The time the resource was last updated.

  - `items.resourceUri` (string)
    Uri of of the resource

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

## Response 404 fields (application/json):

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


