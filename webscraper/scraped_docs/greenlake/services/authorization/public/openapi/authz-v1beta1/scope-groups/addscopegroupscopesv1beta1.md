---
title: "POST /authorization/v1beta1/scope-groups/{id}/scopes/batch"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/scope-groups/addscopegroupscopesv1beta1.md"
scraped_at: "2026-06-07T06:13:57.656760+00:00Z"
---

# Add scopes to a scope group

Add new scopes to an existing scope group. This operation is synchronous and non-atomic.

Endpoint: POST /authorization/v1beta1/scope-groups/{id}/scopes/batch
Version: 1.0.0-beta
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    The scope group instance identifier. ID can be found in the response body of POST /authorization/v1beta1/scope-groups.

## Request fields (application/json):

  - `items` (array, required)

  - `items.grn` (string, required)
    Example: "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/us-east-2/providers/bmaas/host/123"

  - `items.description` (string, required)
    Example: "host 123"

## Response 200 fields (application/json):

  - `successCount` (integer, required)
    How many items were processed successfully
    Example: 1

  - `errorCount` (integer, required)
    How many items were not processed and resulted in errors
    Example: 2

  - `successes` (array, required)

  - `successes.id` (string, required)
    The unique identifier of the object.

  - `successes.type` (string, required)
    Enum: "authorization/scope-group/scope"

  - `successes.grn` (string, required)
    Example: "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/us-east-2/providers/bmaas/host/123"

  - `successes.description` (string, required)
    Example: "host 123"

  - `successes.region` (string, required)
    Example: "us-east-2"

  - `successes.allScopes` (boolean, required)

  - `successes.resourceTypeDisplayName` (string, required)
    Example: "Hosts"

  - `errors` (array, required)
    Example: [{"httpStatusCode":409,"errorCode":"HPE_GL_AUTHORIZATION_RESOURCE_CONFLICT","message":"Scope already exists in scope group","debugId":"","errorDetails":[{"type":"hpe.greenlake.metadata","source":"hpe.greenlake.authorization","metadata":[{"description":"scope 2 description","grn":"grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/us-east-2/providers/bmaas/host/456"}]}]},{"httpStatusCode":400,"errorCode":"HPE_GLERROR_BAD_REQUEST","message":"field \\\"items[0].description\\\" must not be empty: field \\\"items[0].grn\\\" with value \\\"\\\" must be a GRN: missing GRN root tag","debugId":"","errorDetails":[{"type":"hpe.greenlake.bad_request","issues":[{"source":"field","subject":"items[0].description","description":"field \"items[0].description\" must not be empty"},{"source":"field","subject":"items[0].grn","description":"field \"items[0].grn\" with value \"\" must be a GRN: missing GRN root tag"}]}]}]

  - `errors.httpStatusCode` (integer, required)
    The HTTP equivalent status code

  - `errors.errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings.

  - `errors.message` (string, required)
    A user-friendly error message

  - `errors.debugId` (string, required)
    A unique identifier for the instance of this error.

  - `errors.errorDetails` (array)
    Additional detailed information about the error

  - `errors.errorDetails.source` (string)

  - `errors.errorDetails.metadata` (object)
    Present if type is hpe.greenlake.metadata.

  - `errors.errorDetails.issues` (array)
    Details about specific issues related to the scope being added

  - `errors.errorDetails.issues.source` (string)
    Indicates the source of the error

  - `errors.errorDetails.issues.subject` (string)
    The specific value that caused the error

  - `errors.errorDetails.issues.description` (string)
    A detailed message about the error

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


