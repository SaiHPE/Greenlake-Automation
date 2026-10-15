---
title: "GET /data-services/v1beta1/async-operations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/async-operations/listasyncoperations.md"
scraped_at: "2026-06-07T06:15:21.295456+00:00Z"
---

# Returns a list of async-operations accessible by the user

Returns a list of async-operations that are visible to the user. The response can
be paged by using the limit and offset query parameters and filtered and
sorted by using the filter and sort query parameters.

Endpoint: GET /data-services/v1beta1/async-operations
Version: 1.3.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The offset query parameter should be used in conjunction with limit
for paging, e.g.: offset=30&&limit=10. The offset is the number of
items from the beginning of the result set to the first item
included in the response.
    Example: 30

  - `limit` (integer)
    The limit query parameter should be used in conjunction with offset
for paging, e.g.: offset=30&&limit=10. The limit is the maximum
number of items to include in the response.
    Example: 10

  - `filter` (string)
    The expression to filter responses.
    Example: "parent/id eq '73c161c4-4d56-4f31-8dc2-06400a5b36d4'"

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction 
indicator ("asc" or "desc"). If no direction indicator is specified the 
default order is ascending.
    Example: "id desc,name asc"

  - `select` (string)
    A list of properties to include in the response.
    Example: "id,name"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    The time this operation was created.

  - `items.updatedAt` (string, required)
    The time this operation was last updated.

  - `items.resourceUri` (string, required)
    The self reference for this resource.

  - `items.customerId` (string, required)
    The customer application identifier

  - `items.name` (string)
    A system specified name for the resource.

  - `items.additionalDetails` (object)
    A link to be displayed in the Operations UI. This can be used when a operation is paused to take the user to the console UI page with information on how to unpause the operation, or for more general information when the operation is in other states.

  - `items.additionalDetails.consoleUri` (string, required)

  - `items.associatedResources` (array)
    Resources that are associated with the operation. These may be created by the operation or other resources that are involved in the operation.

  - `items.associatedResources.type` (string, required)

  - `items.associatedResources.resourceUri` (string, required)

  - `items.associatedResources.name` (string)

  - `items.displayName` (string)
    The displayed name for the operation.

  - `items.endedAt` (string,null)
    The time this operation completed.

  - `items.error` (object,null)
    The error response status of the operation.

  - `items.error.error` (string, required)
    A user friendly error message
    Example: "An example error message."

  - `items.error.errorCode` (string, required)
    A machine-friendly identifier for the error response

  - `items.error.traceId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

  - `items.estimatedRunningDurationMinutes` (integer)
    An estimate of how long the operation will run before completing.

  - `items.groups` (array)
    A list of groups associated with this operation.

  - `items.groups.id` (string, required)
    ID of the associated group

  - `items.groups.name` (string, required)
    Name of the associated group

  - `items.hasChildOperations` (boolean)
    Indicates this operation possesses child operations. The list of child operations for a given operation may be acquired by querying /data-services/v1beta1/async-operations?filter=parent/id+eq+'{id}' with pagination parameters added as needed to retrieve the full list.

  - `items.healthStatus` (string)
    The health status indicates if any errors or problems have been encountered during the operation. 
Expected values are OK, ERROR, WARNING, UNKNOWN, and UNSPECIFIED.

  - `items.logMessages` (array)
    Time stamped messages that record the progress of the operation. The number of messages presented is limited in number and only the most recent messages are included. Some older log messages may therefore be removed to make room for newer messages.

  - `items.logMessages.timestamp` (string, required)

  - `items.logMessages.message` (string, required)

  - `items.parent` (object,null)
    The parent is the operation that initiated this sub-operation. If this operation is not a sub-operation this will be null.

  - `items.progressPercent` (integer)
    A percentage representation of progress to completion.

  - `items.recommendations` (array)
    Recommendations on how to fix failing operations.

  - `items.rootOperation` (object,null)
    The root of the tree of operations. If this operation is not part of a tree this will be null.

  - `items.services` (array)
    List of services this operation belongs to, can be used to filter to specific services in the UI.

  - `items.sourceResourceUri` (string,null)
    The resource that was used to initiate the operation.

  - `items.startedAt` (string,null)
    The time this operation was started.

  - `items.state` (string)
    A message to indicate the current state of the operation, for example the current step in a workflow.
Expected values are INITIALIZED, RUNNING, FAILED, SUCCEEDED, TIMEDOUT, PAUSED, CANCELLED, and UNSPECIFIED.

  - `items.subtreeOperationCount` (integer)
    The count of the number of child Operations below this one, recursively.

  - `items.suggestedPollingIntervalSeconds` (integer)
    This attribute suggests a suitable interval to use when polling for progress. Where specified this will be based on the frequency with which the operation is likely to be updated.

  - `items.userId` (string)
    The ID or email address of the user that initiated the operation.

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
    Possible values: BAD_REQUEST, INVALID_PARAMETER

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
    Possible values: UNAUTHENTICATED

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
    Possible values: FORBIDDEN

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
    Possible values: INTERNAL_ERROR

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
    Possible values: SERVICE_UNAVAILABLE

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


