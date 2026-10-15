---
title: "DELETE /workspaces/v1beta1/groups/{groupId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/removegroupv2.md"
scraped_at: "2026-06-07T06:13:58.487531+00:00Z"
---

# Delete the workspace group

Delete the existing workspace group from the account

Endpoint: DELETE /workspaces/v1beta1/groups/{groupId}
Version: 1.0.0-beta
Security: bearerAuth

## Path parameters:

  - `groupId` (string, required)
    HPE GreenLake group ID
    Example: "93313ca9-6a6a-48d3-8f91-da639c0b5173"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GROUPS_ERROR_BAD_REQUEST"

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid input of field 'foo'"

  - `debugId` (string, required)
    A unique identifier for the instance of this error
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details
    Example: "hpe.greenlake.bad_request"

  - `errorDetails.issues` (array, required)
    Array of bad request issues

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue
    Enum: "field", "header", "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key
    Example: "foo.bar"

  - `errorDetails.issues.description` (string)
    An elaborate description of the issue. This can be used by developers to understand how the failure can be addressed
    Example: "Invalid format: field 'foo' is incompatible"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GROUPS_ERROR_UNAUTHORIZED"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error"

  - `debugId` (string, required)
    A unique identifier for the instance of this error
    Example: "12312-123123-123123-1231212"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GROUPS_ERROR_FORBIDDEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "User is not authenticated to perform this action"

  - `debugId` (string, required)
    A unique identifier for the instance of this error
    Example: "12312-123123-123123-1231212"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 404

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GROUPS_ERROR_NOT_FOUND"

  - `message` (string, required)
    A user-friendly error message
    Example: "The resource was not found"

  - `debugId` (string, required)
    A unique identifier for the instance of this error
    Example: "12312-123123-123123-1231212"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GROUPS_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    A user-friendly error message
    Example: "The server encountered an unexpected condition which prevented it from fulfilling the request"

  - `debugId` (string, required)
    A unique identifier for the instance of this error
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 503

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_SERVICE_UNAVAILABLE"

  - `message` (string, required)
    A user-friendly error message
    Example: "The server is not ready to handle the request"

  - `debugId` (string, required)
    A unique identifier for the instance of this error
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


## Response 204 fields
