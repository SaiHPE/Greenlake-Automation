---
title: "GET /identity/v1/users"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/identity-v1/nb_openapi_identity/nb-api-user/get_users_identity_v1_users_get.md"
scraped_at: "2026-06-07T06:15:27.500327+00:00Z"
---

# Get users

Retrieve list of users with filtering, and pagination options. All users are returned when no filters are provided. 
Note: User view all permission is required to invoke this API. 
Rate limit: 300 requests per minute per workspace, resulting in a 429 error if exceeded.

Endpoint: GET /identity/v1/users
Version: 1.0.0
Security: BearerAuth

## Query parameters:

  - `filter` (string)
    Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter.

Supported classes and examples include:
- Types: timestamp, string
- Comparison: eq, ne, gt, ge, lt
- Logical Expressions: and, or, not

The Get users API can be filtered by:
- id
- username
- firstName
- lastName
- userStatus
- createdAt
- updatedAt
- lastLogin

userStatus can be one of the following:
- UNVERIFIED
- VERIFIED
- BLOCKED
- DELETE_IN_PROGRESS
- DELETED
- SUSPENDED

Note: The userStatus filter is case-sensitive.

  - `offset` (integer)
    Specify pagination offset. An offset argument defines how many pages to skip before returning results.

  - `limit` (integer)
    Specify the maximum number of entries per page. NOTE: The maximum value accepted is 600.

## Response 200 fields (application/json):

  - `offset` (integer, required)
    Specifies the offset of the returned page

  - `count` (integer, required)
    The number of returned items

  - `total` (integer, required)
    The total number of items in the result set

  - `items` (array, required)
    List of users

  - `items.id` (string, required)
    Resource unique identification

  - `items.type` (string, required)
    Type of data

  - `items.username` (string, required)
    User's Email Address

  - `items.generation` (integer)
    Resource history of updates

  - `items.createdAt` (string)
    The time the resource was created.

  - `items.updatedAt` (string)
    The time the resource was last updated.

  - `items.firstName` (string)
    User's first name

  - `items.lastName` (string)
    User's last name

  - `items.userStatus` (any)
    On-Boarding Status of a user
    Enum: "UNVERIFIED", "VERIFIED", "BLOCKED", "DELETE_IN_PROGRESS", "DELETED", "SUSPENDED"

  - `items.lastLogin` (string)
    Time when this user had last logged in.

  - `items.resourceUri` (string)
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


