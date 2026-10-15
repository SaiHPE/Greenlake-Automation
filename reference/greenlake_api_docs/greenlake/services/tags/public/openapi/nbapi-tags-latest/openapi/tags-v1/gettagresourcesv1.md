---
title: "GET /tags/v1/tag-resources"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/tags/public/openapi/nbapi-tags-latest/openapi/tags-v1/gettagresourcesv1.md"
scraped_at: "2026-06-07T06:16:26.576255+00:00Z"
---

# Get all the tagged resources for a workspace

Retrieve all the tagged resources for a workspace. Various query parameters can be passed to filter, limit, or sort the returned tagged resources.

Endpoint: GET /tags/v1/tag-resources
Version: v1
Security: Bearer

## Query parameters:

  - `filter` (string)
    Filter expressions consisting of simple comparison operations joined
by logical operators. 
| CLASS      |   EXAMPLES                                         |
|------------|----------------------------------------------------|
| Types      | string                                             |
| Operations | eq                                                 |
| Logic      | and, or                                            |
| Properties | id, resourceType                               |

NOTE: Use the filter-tags query parameter to filter tags. 

The examples are not an exhaustive list of all possible filtering options.

  - `filter-tags` (string)
    Filter expressions consisting of simple comparison operations applied on the assigned tags or their values. The comparison operations are case-insensitive. 
| CLASS      |   EXAMPLES                                         |
|------------|----------------------------------------------------|
| Types      | string                                             |
| Operations | eq, ne, contains()                                 |

NOTE: Logical operators are not currently supported.  

The examples are not an exhaustive list of all possible filtering on tags options.

  - `sort` (string)
    A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator asc or desc. If no direction is provided, ascending order is followed by default. If no sort expressions are specified for this query parameter, the response will be sorted by the createdAt timestamp in descending order. Only id, createdAt, and updatedAt are supported for sorting.

  - `select` (array)
    A comma separated list of select properties to display in the response. The default is that all properties are returned.

  - `limit` (integer)
    Specifies the number of results to be returned. The default value is 100.

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from. The default value is 0.

## Response 200 fields (application/json):

  - `items` (array)

  - `items.type` (string, required)
    The resource type.

  - `items.resource` (object, required)

  - `items.resource.resourceUri` (string, required)
    The resource URL.

  - `items.resource.resourceType` (string, required)
    The type of the resource to which the tag is associated.
    Enum: "DEVICE", "DEVICE_SUBSCRIPTION", "SERVICE_SUBSCRIPTION", "LOCATION"

  - `items.createdAt` (string, required)
    The timestamp of the tag resource creation.

  - `items.updatedAt` (string, required)
    The timestamp of the last update to the tag resource.

  - `items.generation` (integer, required)
    Revision number of the record

  - `items.tags` (object, required)

  - `items.id` (string)
    The unique identifier of the tagged resource.

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


