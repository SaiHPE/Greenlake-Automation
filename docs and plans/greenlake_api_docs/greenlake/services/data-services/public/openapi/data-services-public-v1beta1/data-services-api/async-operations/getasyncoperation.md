---
title: "GET /data-services/v1beta1/async-operations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/async-operations/getasyncoperation.md"
scraped_at: "2026-06-07T06:15:15.938153+00:00Z"
---

# Returns details of a specific async-operation

Returns the async-operation with the given id.

Endpoint: GET /data-services/v1beta1/async-operations/{id}
Version: 1.3.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the object
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

## Query parameters:

  - `select` (string)
    A list of properties to include in the response.
    Example: "id,name"

## Response 200 fields (application/json):

  - `id` (string, required)
    An identifier for the resource, usually a UUID.

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    The time this operation was created.

  - `updatedAt` (string, required)
    The time this operation was last updated.

  - `resourceUri` (string, required)
    The self reference for this resource.

  - `customerId` (string, required)
    The customer application identifier

  - `name` (string)
    A system specified name for the resource.

  - `additionalDetails` (object)
    A link to be displayed in the Operations UI. This can be used when a operation is paused to take the user to the console UI page with information on how to unpause the operation, or for more general information when the operation is in other states.

  - `additionalDetails.consoleUri` (string, required)

  - `associatedResources` (array)
    Resources that are associated with the operation. These may be created by the operation or other resources that are involved in the operation.

  - `associatedResources.type` (string, required)

  - `associatedResources.resourceUri` (string, required)

  - `associatedResources.name` (string)

  - `displayName` (string)
    The displayed name for the operation.

  - `endedAt` (string,null)
    The time this operation completed.

  - `error` (object,null)
    The error response status of the operation.

  - `error.error` (string, required)
    A user friendly error message
    Example: "An example error message."

  - `error.errorCode` (string, required)
    A machine-friendly identifier for the error response

  - `error.traceId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

  - `estimatedRunningDurationMinutes` (integer)
    An estimate of how long the operation will run before completing.

  - `groups` (array)
    A list of groups associated with this operation.

  - `groups.id` (string, required)
    ID of the associated group

  - `groups.name` (string, required)
    Name of the associated group

  - `hasChildOperations` (boolean)
    Indicates this operation possesses child operations. The list of child operations for a given operation may be acquired by querying /data-services/v1beta1/async-operations?filter=parent/id+eq+'{id}' with pagination parameters added as needed to retrieve the full list.

  - `healthStatus` (string)
    The health status indicates if any errors or problems have been encountered during the operation. 
Expected values are OK, ERROR, WARNING, UNKNOWN, and UNSPECIFIED.

  - `logMessages` (array)
    Time stamped messages that record the progress of the operation. The number of messages presented is limited in number and only the most recent messages are included. Some older log messages may therefore be removed to make room for newer messages.

  - `logMessages.timestamp` (string, required)

  - `logMessages.message` (string, required)

  - `parent` (object,null)
    The parent is the operation that initiated this sub-operation. If this operation is not a sub-operation this will be null.

  - `progressPercent` (integer)
    A percentage representation of progress to completion.

  - `recommendations` (array)
    Recommendations on how to fix failing operations.

  - `rootOperation` (object,null)
    The root of the tree of operations. If this operation is not part of a tree this will be null.

  - `services` (array)
    List of services this operation belongs to, can be used to filter to specific services in the UI.

  - `sourceResourceUri` (string,null)
    The resource that was used to initiate the operation.

  - `startedAt` (string,null)
    The time this operation was started.

  - `state` (string)
    A message to indicate the current state of the operation, for example the current step in a workflow.
Expected values are INITIALIZED, RUNNING, FAILED, SUCCEEDED, TIMEDOUT, PAUSED, CANCELLED, and UNSPECIFIED.

  - `subtreeOperationCount` (integer)
    The count of the number of child Operations below this one, recursively.

  - `suggestedPollingIntervalSeconds` (integer)
    This attribute suggests a suitable interval to use when polling for progress. Where specified this will be based on the frequency with which the operation is likely to be updated.

  - `userId` (string)
    The ID or email address of the user that initiated the operation.

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

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    Possible values: NOT_FOUND

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


