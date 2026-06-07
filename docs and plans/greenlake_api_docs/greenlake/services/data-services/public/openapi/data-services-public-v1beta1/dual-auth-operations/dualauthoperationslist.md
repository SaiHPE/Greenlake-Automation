---
title: "GET /data-services/v1beta1/dual-auth-operations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/dual-auth-operations/dualauthoperationslist.md"
scraped_at: "2026-06-07T06:15:21.311653+00:00Z"
---

# List Dual Authorization operations

Returns the list of Dual Authorization operations for the current account. The list will include only the resource types (Application Resource) the user has read permission for. The user must have permission to read pending operations.

Endpoint: GET /data-services/v1beta1/dual-auth-operations
Version: 1.3.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    Use offset in conjunction with limit for paging. The offset is the number of items from the beginning of the result set to the first item included in the response.

  - `limit` (integer)
    Use limit in conjunction with offset for paging. The limit is the maximum number of items to include in the response.

  - `filter` (string)
    The expression to use for filtering responses. The following comparisons are supported:
“eq” : Valid for number, boolean and string properties.
“gt” :  Valid for number or string timestamp properties.
“lt” :  Valid for number or string timestamp properties
“in” : Valid for an array of strings
Syntax:
“eq” : filter=\ eq \ {host:port}/data-services/v1beta1/dual-auth-operations?filter=\ eq \
“gt” : filter=\ gt \ {host:port}/data-services/v1beta1/dual-auth-operations?filter=\ gt \
“lt” : filter=\ lt \ {host:port}/data-services/v1beta1/dual-auth-operations?filter=\ lt \
“in” : filter=\ in \ {host:port}/data-services/v1beta1/dual-auth-operations?filter=\ in \
* Use "and" to combine filter inputs {host:port}/data-services/v1beta1/dual-auth-operations?filter=\ eq \ and \ lt \
* To filter multiple values on one property e.g. filter=resourceType in ('foo','bar') {host:port}/data-services/v1beta1/dual-auth-operations?filter=foo%bar%20in%20resourceType
Examples:
GET /data-services/v1beta1/dual-auth-operations?filter=resourceType eq 'ISSUE'
GET /data-services/v1beta1/dual-auth-operations?filter=resourceType eq 'ISSUE' and state eq 'CREATED'
GET /data-services/v1beta1/dual-auth-operations?filter=relatedObjectType in ('NIMBLE-VOLUME')
Filters are supported on following attributes:
resourceUri,
resourceName,
resourceType,
requestedOperation,
operationDescription,
requestedByUri,
requestedByEmail,
requestedAt,
customerId,
checkedByUri,
checkedByEmail,
checkedAt,
sourceServiceExternalName,
state

  - `sort` (string)
    The property to sort by followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified the default order is ascending.

  - `select` (string)
    Limits the properties returned with a resource or collection-level GET. Specify a comma-separated list of properties. If this is omitted, all properties are returned.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)

  - `items.updatedAt` (string, required)

  - `items.resourceUri` (string, required)
    The self reference for this resource.

  - `items.customerId` (string, required)
    The customer application identifier

  - `items.name` (string)
    A system specified name for the resource.

  - `items.associatedResources` (array)
    Resources associated with this operation

  - `items.associatedResources.groups` (array)
    Groups this resource is associated with

  - `items.associatedResources.groups.id` (string, required)
    ID of the associated group

  - `items.associatedResources.groups.name` (string, required)
    Name of the associated group

  - `items.associatedResources.resource` (object)
    Resource associated with this operation

  - `items.associatedResources.resource.type` (string, required)

  - `items.associatedResources.resource.resourceUri` (string, required)

  - `items.associatedResources.resource.name` (string)

  - `items.associatedResources.resource.consoleUri` (string)
    The URI for the console screen that displays this resource

  - `items.checkedAt` (string)
    Time when this operation was checked. RFC 3339 Timestamp

  - `items.checkedByEmail` (string)
    Email of the user who checked (second authorization) this operation

  - `items.checkedByUri` (string)
    URI of the user who checked (second authorization) this operation

  - `items.description` (string)
    Detailed description of the operation

  - `items.requestedAt` (string)
    Time when this operation was requested. RFC 3339 Timestamp

  - `items.requestedByEmail` (string)
    Email of the user who performed this operation

  - `items.requestedByUri` (string)
    URI of the user who performed this operation

  - `items.requestedOperation` (string)
    One word description of the operation

  - `items.sourceServiceExternalName` (string)
    External Service Name from where this request was sent

  - `items.state` (string)
    state of this operation

  - `items.consoleUri` (string)
    The URI for console screen that displays this resource. Deprecated - use associatedResources instead

  - `items.groups` (array)
    Groups this operation is associated with. Deprecated - use associatedResources instead

  - `items.operationResource` (object)
    Operation resource on which the operation is taking place. Deprecated - use associatedResources instead

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

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
    A machine friendly identifier for the error response

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
    A machine friendly identifier for the error response

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
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

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
    A machine friendly identifier for the error response

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
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


