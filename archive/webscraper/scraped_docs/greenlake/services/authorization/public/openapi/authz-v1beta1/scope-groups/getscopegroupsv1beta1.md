---
title: "GET /authorization/v1beta1/scope-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/scope-groups/getscopegroupsv1beta1.md"
scraped_at: "2026-06-07T06:13:57.414519+00:00Z"
---

# Retrieve all scope groups

Retrieves scope groups by applying OData 4.0 filters. Use the filter parameter to provide a filter string. Supports in operator on serviceMetadata/id, name or grn attributes. Example Request: /authorization/v1beta1/scope-groups?filter=grn in ('grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/123')
Note:
- No duplicate attributes in OData filter: Each attribute (serviceMetadata/id, name, grn) can only appear once in the OData filter expression. Multiple occurrences will result in a 400 Bad Request error.
- Only one attribute in OData filter: Only one attribute (serviceMetadata/id, name or grn) can be used at a time, otherwise it will result in a 400 Bad Request error.
- Supported operators: Only in operator is supported.

Endpoint: GET /authorization/v1beta1/scope-groups
Version: 1.0.0-beta
Security: bearerAuth

## Query parameters:

  - `limit` (integer)
    Total number of results to be returned. If the parameter is not provided, it will return all records found.

  - `offset` (integer)
    Zero-based resource offset to start the response from

  - `filter` (string)
    OData style filter for filtering scope groups. Supports in operator on serviceMetadata/id, name or grn attributes.
    Example: "grn in ('grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/123')"

  - `sort` (string)
    Sort results by a single attribute and allow setting a sorting direction as ascending (asc) or descending (desc). Sorting is valid only for name attribute. Default sorting direction if omitted is ascending.
    Example: "name desc"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the object.

  - `items.type` (string, required)
    Enum: "authorization/scope-group"

  - `items.name` (string, required)
    Must be unique within the context it is being created (organization or organization + workspace). Most ASCII characters are allowed, except [&, `, |, :, ,`] and leading or trailing space.
    Example: "sg1"

  - `items.description` (string)
    A short description of the scope group.
    Example: "This group gives access to resource \"host/123\""

  - `items.grn` (string)
    The HPE GreenLake Resource Notation (GRN) is the standardized, URI-compatible syntax used to define and specify this scope within the HPE GreenLake.
    Example: "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/authorization/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `items.serviceMetadata` (object)

  - `items.serviceMetadata.id` (string, required)
    It can be empty if the object was just created.
    Example: "44f0443c-fd03-47fc-981b-9c4333a37b44"

  - `items.serviceMetadata.type` (string, required)
    It can be empty if the object was just created.
    Enum: "/service-catalog/service-manager", "/service-catalog/service-offer"

  - `items.generation` (integer)

  - `items.createdAt` (string)
    The date and time the resource was created.

  - `items.updatedAt` (string)
    The date and time the resource was last updated.

  - `offset` (integer, required)
    The zero-based resource offset.

  - `count` (integer, required)
    The number of items returned.

  - `total` (integer, required)
    The total number of items in the collection that match the filter query, if one was provided in the request.

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


