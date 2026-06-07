---
title: "GET /workspaces/v1beta1/groups/{groupId}/group-workspaces"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/listgroupworkspaces.md"
scraped_at: "2026-06-07T06:16:55.711856+00:00Z"
---

# List of paginated workspaces associated with the group ID

Get the paginated list of workspaces associated with the group ID

Endpoint: GET /workspaces/v1beta1/groups/{groupId}/group-workspaces
Version: 1.0.0-beta
Security: bearerAuth

## Path parameters:

  - `groupId` (string, required)
    HPE GreenLake group ID
    Example: "93313ca9-6a6a-48d3-8f91-da639c0b5173"

## Query parameters:

  - `limit` (integer)
    Specifies the number of query results to be returned in a query response page

  - `offset` (integer)
    The starting offset from which to begin retrieving items

## Response 200 fields (application/json):

  - `items` (array, required)
    list of member objects

  - `items.id` (string, required)
    HPE GreenLake unique resource ID for this workspace belonging to the group
    Example: "119363f3-4408-44c4-840a-99e1c9db64c1"

  - `items.type` (string, required)
    Example: "/workspaces/group/group-workspace"

  - `items.workspace` (object, required)
    workspace resource metadata

  - `items.workspace.id` (string, required)
    HPE GreenLake global ID unique resource identifier for workspace
    Example: "5a4af781011e423ba6bd554dc73ae5a5"

  - `items.workspace.description` (string, required)
    Description of the workspace
    Example: "US-E Workspace"

  - `items.workspace.name` (string, required)
    name for the workspace
    Example: "US-E workspace"

  - `items.grn` (string, required)
    Example: "grn:glp/workspaces/05f0523cfd0347fc981b9c4333a37b60/regions/default/providers/msp/tenant-groups/93313ca9-6a6a-48d3-8f91-da639c0b5173"

  - `items.generation` (integer, required)
    Number of times the resource updated

  - `items.createdAt` (string, required)
    Example: "2024-01-08 22:59:17.424801 +0000 UTC"

  - `items.updatedAt` (string, required)
    Example: "2024-01-08 23:00:22.320646 +0000 UTC"

  - `count` (integer, required)

  - `total` (integer, required)

  - `offset` (integer)
    The starting offset from which to begin retrieving items

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


