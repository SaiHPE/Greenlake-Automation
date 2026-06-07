---
title: "PUT /authorization/v1beta1/role-assignments/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/role-assignments/updateroleassignmentv1beta1.md"
scraped_at: "2026-06-07T06:13:55.687917+00:00Z"
---

# Update a role assignment instance by ID

Allows updating scopes of an existing role assignment. Request body must contain id, principal and role attributes even though they are immutable.  The id can be found in the response body of POST /authorization/v1beta1/role-assignments.  Note: For assistance finding the principal, scope, and role identifiers, see the developer guide.

Endpoint: PUT /authorization/v1beta1/role-assignments/{id}
Version: 1.0.0-beta
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    The role assignment instance identifier. The ID can be found in the response body of POST /authorization/v1beta1/role-assignments.

## Request fields (application/json):

  - `id` (string, required)
    The unique identifier of the object. Immutable.

  - `principal` (string, required)
    The security principal identifier {type}:{id}. A principal is the entity that receives a role. The supported types are user, user-group, and api-client.
    Example: "user:123981y2zxhiz1890"

  - `scope` (array, required)
    Fully qualified scope string in GRN syntax. A scope is the specific resource or set of resources to which the role and its permissions apply. The scopes can be at the workspace level (limited to 1), tenant groups (up to 10), and scope groups (up to 10), and can be combined: Workspace + Tenant Group or Tenant Group + Scope Group.
    Example: ["grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/msp/tenant-groups/d88d38c9-8cf7-4ab8-a808-126b47bb787d","grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/21e582d3-fb24-4162-9fca-350defe24d3c"]

  - `role` (string, required)
    The unique role identifier in GRN syntax. A role is a collection of permissions defining what actions the principal can perform.
    Example: "grn:glp/providers/authorization/roles/storageservices.LimitedAdmin"

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier of the object.

  - `type` (string, required)
    The type of the resource.
    Enum: "authorization/role-assignment"

  - `principal` (string, required)
    The security principal identifier {type}:{id}. A principal is the entity that receives a role. The supported types are user, user-group, and api-client.
    Example: "user:123981y2zxhiz1890"

  - `scope` (array, required)
    Fully qualified scope string in GRN syntax. A scope is the specific resource or set of resources to which the role and its permissions apply. The scopes can be at the workspace level (limited to 1), tenant groups (up to 10), and scope groups (up to 10), and can be combined: Workspace + Tenant Group or Tenant Group + Scope Group.
    Example: ["grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/msp/tenant-groups/d88d38c9-8cf7-4ab8-a808-126b47bb787d","grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/21e582d3-fb24-4162-9fca-350defe24d3c"]

  - `role` (string, required)
    The unique role identifier in GRN syntax. A role is a collection of permissions defining what actions the principal can perform.
    Example: "grn:glp/providers/authorization/roles/storageservices.LimitedAdmin"

  - `principalMetadata` (object, required)

  - `principalMetadata.id` (string, required)
    The unique identifier of the principal.
    Example: "123981y2zxhiz1890"

  - `principalMetadata.type` (string, required)
    The type of the principal.
    Enum: "identity/user", "identity/user-group", "identity/api-client"

  - `roleMetadata` (object, required)

  - `roleMetadata.id` (string, required)
    The unique identifier of the role.
    Example: "44f0443c-fd03-47fc-981b-9c4333a37b44"

  - `roleMetadata.type` (string, required)
    The type of the role.
    Example: "authorization/role"

  - `generation` (integer, required)

  - `createdAt` (string, required)
    The date and time the resource was created.

  - `updatedAt` (string, required)
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


