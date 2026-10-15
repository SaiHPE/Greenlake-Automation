---
title: "GET /authorization/v1beta1/role-assignments"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/authz-v2/external/openapi/authz-v2alpha2/role-assignments/getroleassignmentsv1beta1.md"
scraped_at: "2026-06-07T06:16:53.910787+00:00Z"
---

# Retrieve all role assignments

Retrieves role assignments by applying OData 4.0 filters. Use the filter parameter to provide a filter string. Supports in and and operators on role, scope and principal attributes. Example Request: /authorization/v1beta1/role-assignments?filter=role in ('grn:glp/providers/authorization/roles/storageservices.LimitedAdmin') and principal in ('user:123981y2zxhiz1890')
Note:
- No duplicate attributes in OData filter: Each attribute (role, scope, principal) can only appear once in the OData filter expression. Multiple occurrences will result in a 400 Bad Request error.
- Supported operators: Only the in and and operators are supported.

Endpoint: GET /authorization/v1beta1/role-assignments
Version: 1.0.0-beta
Security: bearerAuth

## Query parameters:

  - `limit` (integer)
    Total number of results to be returned

  - `offset` (integer)
    Zero-based resource offset to start the response from

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in a collection-level GET. The returned set of resources matches the criteria in the filter query parameter. Supports in and and operators on role, scope and principal attributes.
    Example: "role in ('grn:glp/providers/authorization/roles/storageservices.LimitedAdmin') and principal in ('user:123981y2zxhiz1890')"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the object.

  - `items.type` (string, required)
    The type of the resource.
    Enum: "authorization/role-assignment"

  - `items.principal` (string, required)
    The security principal identifier {type}:{id}. A principal is the entity that receives a role. The supported types are user, user-group, and api-client.
    Example: "user:123981y2zxhiz1890"

  - `items.scope` (array, required)
    Fully qualified scope string in GRN syntax. A scope is the specific resource or set of resources to which the role and its permissions apply. The scopes can be at the workspace level (limited to 1), tenant groups (up to 10), and scope groups (up to 10), and can be combined: Workspace + Tenant Group or Tenant Group + Scope Group.
    Example: ["grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/msp/tenant-groups/d88d38c9-8cf7-4ab8-a808-126b47bb787d","grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/21e582d3-fb24-4162-9fca-350defe24d3c"]

  - `items.role` (string, required)
    The unique role identifier in GRN syntax. A role is a collection of permissions defining what actions the principal can perform.
    Example: "grn:glp/providers/authorization/roles/storageservices.LimitedAdmin"

  - `items.principalMetadata` (object, required)

  - `items.principalMetadata.id` (string, required)
    The unique identifier of the principal.
    Example: "123981y2zxhiz1890"

  - `items.principalMetadata.type` (string, required)
    The type of the principal.
    Enum: "identity/user", "identity/user-group", "identity/api-client"

  - `items.roleMetadata` (object, required)

  - `items.roleMetadata.id` (string, required)
    The unique identifier of the role.
    Example: "44f0443c-fd03-47fc-981b-9c4333a37b44"

  - `items.roleMetadata.type` (string, required)
    The type of the role.
    Example: "authorization/role"

  - `items.generation` (integer, required)

  - `items.createdAt` (string, required)
    The date and time the resource was created.

  - `items.updatedAt` (string, required)
    The date and time the resource was last updated.

  - `items.source` (string)
    The location where the configuration item is defined and managed

  LOCAL:
  The object is managed in the current workspace.
  EXTERNAL:
  The object is managed in another workspace or organization and projected into the current context.
    Enum: "LOCAL", "EXTERNAL"

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


