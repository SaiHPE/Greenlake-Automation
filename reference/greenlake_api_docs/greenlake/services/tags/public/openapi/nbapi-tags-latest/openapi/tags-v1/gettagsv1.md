---
title: "GET /tags/v1/tags"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/tags/public/openapi/nbapi-tags-latest/openapi/tags-v1/gettagsv1.md"
scraped_at: "2026-06-07T06:16:26.519642+00:00Z"
---

# Get tags associated to a workspace

Retrieve a list of tags associated to a workspace. Various query parameters can be passed to filter, limit, or sort the returned tags.

Endpoint: GET /tags/v1/tags
Version: v1
Security: Bearer

## Query parameters:

  - `filter` (string)
    Filter expressions consisting of simple comparison operations joined
by logical operators. 
| CLASS      |   EXAMPLES                                         |
|------------|----------------------------------------------------|
| Types      | string                                             |
| Operations | eq, contains()                                     |
| Logic      | and, or                                            |
| Properties | id, key, value                               |

The examples are not an exhaustive list of all possible filtering options.

  - `sort` (string)
    A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator 'asc' or 'desc'. If no direction is provided, ascending order is followed by  default. If no sort expressions are specified for this query parameter, the response will be sorted by the createdAt timestamp in descending order. type and resourceCount are not supported for sorting.

  - `select` (array)
    A comma separated list of select properties to display in the response. The default is that all properties are returned.

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 100.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `items` (array)

  - `items.id` (string, required)
    The unique identifier of the tag.

  - `items.type` (string, required)
    The resource type.

  - `items.key` (string, required)
    The tag key. A tag key is the name used to refer to the tag.

  - `items.value` (string, required)
    The tag value. A tag value is a value applied to the tag key.

  - `items.resourceCount` (integer, required)
    The number of resources associated with the tag.

  - `items.createdAt` (string, required)
    The timestamp of the tag creation.

  - `items.updatedAt` (string, required)
    The timestamp of the last update to the tag.

  - `items.generation` (integer, required)
    Revision number of the record

  - `offset` (integer)
    Zero-based resource offset

  - `count` (integer)
    Number of items returned

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)


