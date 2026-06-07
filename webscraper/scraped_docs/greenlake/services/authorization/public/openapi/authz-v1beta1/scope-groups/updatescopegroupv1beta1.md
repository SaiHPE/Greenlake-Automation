---
title: "PUT /authorization/v1beta1/scope-groups/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/scope-groups/updatescopegroupv1beta1.md"
scraped_at: "2026-06-07T06:13:57.564020+00:00Z"
---

# Update a scope group instance by ID

Request body must contain id attribute even though it is immutable.

Endpoint: PUT /authorization/v1beta1/scope-groups/{id}
Version: 1.0.0-beta
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    The scope group instance identifier. The ID can be found in the response body of POST /authorization/v1beta1/scope-groups.

## Request fields (application/json):

  - `id` (string, required)
    The unique identifier of the object. Immutable

  - `name` (string, required)
    Must be unique within the context it is being created (organization or organization + workspace). Most ASCII characters are allowed, except [&, `, |, :, ,`] and leading or trailing space.
    Example: "sg1"

  - `description` (string)
    A short description of the scope group.
    Example: "This group gives access to resource \"host/123\""

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the object.

  - `type` (string, required)
    Enum: "authorization/scope-group"

  - `name` (string, required)
    Must be unique within the context it is being created (organization or organization + workspace). Most ASCII characters are allowed, except [&, `, |, :, ,`] and leading or trailing space.
    Example: "sg1"

  - `description` (string)
    A short description of the scope group.
    Example: "This group gives access to resource \"host/123\""

  - `grn` (string)
    The HPE GreenLake Resource Notation (GRN) is the standardized, URI-compatible syntax used to define and specify this scope within the HPE GreenLake.
    Example: "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/authorization/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `serviceMetadata` (object)

  - `serviceMetadata.id` (string, required)
    It can be empty if the object was just created.
    Example: "44f0443c-fd03-47fc-981b-9c4333a37b44"

  - `serviceMetadata.type` (string, required)
    It can be empty if the object was just created.
    Enum: "/service-catalog/service-manager", "/service-catalog/service-offer"

  - `generation` (integer)

  - `createdAt` (string)
    The date and time the resource was created.

  - `updatedAt` (string)
    The date and time the resource was last updated.

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

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 409

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.

  HPE_GL_AUTHORIZATION_ALREADY_CREATED:
  An exact copy of this resource already exists
  HPE_GL_AUTHORIZATION_RESOURCE_CONFLICT:
  An instance with same unique identifier(s) already exists
    Enum: "HPE_GL_AUTHORIZATION_ALREADY_CREATED", "HPE_GL_AUTHORIZATION_RESOURCE_CONFLICT"

  - `message` (string, required)
    A user-friendly error message.
    Example: "There is a conflict with the current state of the target resource"

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


