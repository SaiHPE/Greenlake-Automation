---
title: "GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/tags/{tag-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/hypervisor-tags/hypervisortag.md"
scraped_at: "2026-06-07T06:16:32.416342+00:00Z"
---

# Get a hypervisor tag resource identified by {tag-id}

Details of a hypervisors tag resource.

Endpoint: GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/tags/{tag-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `hypervisor-id` (string, required)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `tag-id` (string, required)
    UUID string uniquely identifying the hypervisor tag resource.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the hypervisor tag resource.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created.

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `associatedResources` (array)
    List of resources to which this tag is associated.

  - `associatedResources.id` (string)
    An identifier for the resource, usually a UUID.

  - `associatedResources.resourceUri` (string)
    The URI reference for this resource.

  - `categoryName` (string)
    The category name is unique to the currently selected hypervisor manager.

  - `customerId` (string)
    The customer application identifier.

  - `displayName` (string)
    This will always be same as name since add or update of hypervisor tags are not supported when it is managed from a manager like vCenter.
    Example: "T-5"

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `name` (string)
    Name of the tag as reported by the hypervisor manager.
    Example: "T-5"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/tags/{tag-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the hypervisor tag.
    Enum: "OK", "DELETED"

  - `uid` (string)
    Hypervisor provided identifier of the hypervisor tag.
    Example: "8476c228-d128-519c-a2ac-a4932ff2109b"

  - `vmProtectionGroupsInfo` (array)
    Protection groups related to the hypervisor-tag.

  - `vmProtectionGroupsInfo.id` (string)
    Unique identifier for the Protection Group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `vmProtectionGroupsInfo.name` (string)
    Name of the Protection Group.
    Example: "myProtectionGroup"

  - `vmProtectionGroupsInfo.resourceUri` (string)
    Reference to resource.

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


