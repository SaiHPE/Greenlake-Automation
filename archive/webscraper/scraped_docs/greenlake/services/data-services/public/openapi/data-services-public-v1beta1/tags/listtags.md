---
title: "GET /data-services/v1beta1/tags"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/tags/listtags.md"
scraped_at: "2026-06-07T06:15:22.965595+00:00Z"
---

# GET tags

Returns a list of all tags when no select query parameter is provided. 
When a select query parameter is provided, then key or value of the tags are returned.

Endpoint: GET /data-services/v1beta1/tags
Version: 1.3.0
Security: bearer

## Query parameters:

  - `select` (string)
    A list of properties to include in the response. Service currently
only supports specification of all fields.

  - `filter` (string)
    The set of tags returned in the response.
The supported comparisons are:
  - “eq” : Valid for number, boolean and string properties.
  - “ne” : Valid for number, boolean and string properties.
  - "contains"

Syntax:
  - “eq” : filter=\ eq \
  - “ne” : filter=\ ne \
  - "startswith" : filter=startswith(key, 'Houston')
  - "startswith" : filter=startswith(value, 'Houston')
You can use "and" to filter on multiple fields 
  "filter=\ eq \ and \ ne \"
Examples:
  GET /data-services/v1beta1/tags?filter=key eq Houston
  GET /data-services/v1beta1/tags?filter=startswith(key, Houston) and value eq Volume
Filters are supported on following attributes:
  - key
  - value

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction 
indicator ("asc" or "desc"). Default order is ascending. 
Service only supports sorting by 1 property per request. Supported fields 
include:
- key
- value - If specified, a secondary sort by "key asc" is included to guarantee consistent paging behavior.
    Enum: "asc", "desc"

  - `offset` (integer)
    The number of results to skip. This is used for paging results.

  - `limit` (integer)
    The number of results to return.
    Example: 1

## Response 200 fields (application/json):

  - `items` (array, required)
    The tags returned by the query.

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.
    Example: "b253093a-a264-4185-b9f9-fc44d66e2841"

  - `items.type` (string, required)
    The type of resource.
    Example: "data-services/tag"

  - `items.customerId` (string, required)
    Primary identifier for the customer associated with the tag.
    Example: "a7d8c2f2e5ab11eb996bd6f781f4ee4e"

  - `items.key` (string)
    The tag key.

  - `items.value` (string)
    The tag value.

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine-friendly identifier for the error response. The following error codes may be
returned:
- HPE_GL_ERROR_BAD_REQUEST
    Example: "HPE_GL_ERROR_BAD_REQUEST"

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine-friendly identifier for the error response. The following error codes may be
returned:
- HPE_GL_ERROR_UNAUTHORIZED
    Example: "HPE_GL_ERROR_UNAUTHORIZED"

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine-friendly identifier for the error response. The following error codes may be
returned:
- HPE_GL_ERROR_FORBIDDEN
    Example: "HPE_GL_ERROR_FORBIDDEN"

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine-friendly identifier for the error response. The following error codes may be
returned:
- HPE_GL_ERROR_NOT_FOUND
    Example: "HPE_GL_ERROR_NOT_FOUND"

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine-friendly identifier for the error response. The following error codes may be
returned:
- HPE_GL_ERROR_INTERNAL_SERVER_ERROR
    Example: "HPE_GL_ERROR_INTERNAL_SERVER_ERROR"

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine-friendly identifier for the error response. The following error codes may be
returned:
- HPE_GL_ERROR_SERVICE_UNAVAILABLE
    Example: "HPE_GL_ERROR_SERVICE_UNAVAILABLE"

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


