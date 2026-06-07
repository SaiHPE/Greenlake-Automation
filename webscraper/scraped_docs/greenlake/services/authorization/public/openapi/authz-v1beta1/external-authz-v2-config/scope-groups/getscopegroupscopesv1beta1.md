---
title: "GET /authorization/v1beta1/scope-groups/{id}/scopes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/getscopegroupscopesv1beta1.md"
scraped_at: "2026-06-07T06:13:56.107245+00:00Z"
---

# Retrieve the scope group scopes list

Retrieves a list of scopes for a specific scope group. Results are sorted by description and GRN alphabetically by default.

Endpoint: GET /authorization/v1beta1/scope-groups/{id}/scopes
Version: 1.0.0-beta
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    The scope group instance identifier. The ID can be found in the response body of POST /authorization/v1beta1/scope-groups.

## Query parameters:

  - `limit` (integer)
    Total number of results to be returned. If the parameter is not provided, it will return all records found.

  - `offset` (integer)
    Zero-based resource offset to start the response from

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the object.

  - `items.type` (string, required)
    Enum: "authorization/scope-group/scope"

  - `items.grn` (string, required)
    Example: "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/us-east-2/providers/bmaas/host/123"

  - `items.description` (string, required)
    Example: "host 123"

  - `items.region` (string, required)
    Example: "us-east-2"

  - `items.allScopes` (boolean, required)

  - `items.resourceTypeDisplayName` (string, required)
    Example: "Hosts"

  - `offset` (integer, required)
    The zero-based resource offset.

  - `count` (integer, required)
    The number of items returned.

  - `total` (integer, required)
    The total number of items in the collection that match the filter query, if one was provided in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_AUTHZ_INVALID_FORMAT"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Invalid format of field \"foo\""

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.bad_request"

  - `errorDetails.issues` (array, required)
    Array of bad request issues

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Enum: "field", "header", "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "foo.bar"

  - `errorDetails.issues.description` (string)
    An elaborate description of the issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Invalid format: field \"foo\" is incompatible"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_AUTHZ_EXPIRED_TOKEN"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Authentication error"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_AUTHZ_BLOCKED_USER"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Action is blocked for this user"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 404

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_ERROR_NOT_FOUND"

  - `message` (string, required)
    A user-friendly error message.
    Example: "The resource was not found"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 429

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings.
    Example: "HPE_GL_ERROR_TOO_MANY_REQUESTS"

  - `message` (string, required)
    A user-friendly error message.
    Example: "User sent too many requests"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings.
    Example: "HPE_GL_ERROR_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    A user-friendly error message.
    Example: "The server encountered an unexpected condition which prevented it from fulfilling the request."

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 503

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_ERROR_SERVICE_UNAVAILABLE"

  - `message` (string, required)
    A user-friendly error message.
    Example: "The server is not ready to handle the request"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


