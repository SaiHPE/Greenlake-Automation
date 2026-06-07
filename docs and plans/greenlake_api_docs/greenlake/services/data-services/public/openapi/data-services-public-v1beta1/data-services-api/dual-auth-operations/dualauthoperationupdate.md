---
title: "PATCH /data-services/v1beta1/dual-auth-operations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/dual-auth-operations/dualauthoperationupdate.md"
scraped_at: "2026-06-07T06:15:16.384543+00:00Z"
---

# Changes the value of the given Dual Authorization operation. Approve/Deny the pending operation by changing its state in DB

Approve/Deny the pending operation by changing its state in DB.

Endpoint: PATCH /data-services/v1beta1/dual-auth-operations/{id}
Version: 1.3.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    the ID of the operation
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

## Request fields (application/merge-patch+json):

  - `state` (string, required)
    new value of the "state" setting
    Enum: "APPROVED", "CANCELLED"

## Response 200 fields (application/json):

  - `id` (string, required)
    An identifier for the resource, usually a UUID.

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)

  - `updatedAt` (string, required)

  - `resourceUri` (string, required)
    The self reference for this resource.

  - `customerId` (string, required)
    The customer application identifier

  - `name` (string)
    A system specified name for the resource.

  - `associatedResources` (array)
    Resources associated with this operation

  - `associatedResources.groups` (array)
    Groups this resource is associated with

  - `associatedResources.groups.id` (string, required)
    ID of the associated group

  - `associatedResources.groups.name` (string, required)
    Name of the associated group

  - `associatedResources.resource` (object)
    Resource associated with this operation

  - `associatedResources.resource.type` (string, required)

  - `associatedResources.resource.resourceUri` (string, required)

  - `associatedResources.resource.name` (string)

  - `associatedResources.resource.consoleUri` (string)
    The URI for the console screen that displays this resource

  - `checkedAt` (string)
    Time when this operation was checked. RFC 3339 Timestamp

  - `checkedByEmail` (string)
    Email of the user who checked (second authorization) this operation

  - `checkedByUri` (string)
    URI of the user who checked (second authorization) this operation

  - `description` (string)
    Detailed description of the operation

  - `requestedAt` (string)
    Time when this operation was requested. RFC 3339 Timestamp

  - `requestedByEmail` (string)
    Email of the user who performed this operation

  - `requestedByUri` (string)
    URI of the user who performed this operation

  - `requestedOperation` (string)
    One word description of the operation

  - `sourceServiceExternalName` (string)
    External Service Name from where this request was sent

  - `state` (string)
    state of this operation

  - `consoleUri` (string)
    The URI for console screen that displays this resource. Deprecated - use associatedResources instead

  - `groups` (array)
    Groups this operation is associated with. Deprecated - use associatedResources instead

  - `operationResource` (object)
    Operation resource on which the operation is taking place. Deprecated - use associatedResources instead

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

## Response 412 fields (application/json):

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


