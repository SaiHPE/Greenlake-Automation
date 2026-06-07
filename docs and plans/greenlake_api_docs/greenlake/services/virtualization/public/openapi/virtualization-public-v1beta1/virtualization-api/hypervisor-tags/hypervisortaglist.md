---
title: "GET /virtualization/v1beta1/hypervisor-managers/{uuid}/tags"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-tags/hypervisortaglist.md"
scraped_at: "2026-06-07T06:16:29.457040+00:00Z"
---

# Get all tag resources in a registered hypervisor manager.

List all the tag resources in a registered hypervisor manager.

Endpoint: GET /virtualization/v1beta1/hypervisor-managers/{uuid}/tags
Version: 1.2.0
Security: bearer

## Path parameters:

  - `uuid` (string, required)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set

  - `limit` (integer)
    The numbers of items to return

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.
The returned set of resources must match the criteria in the filter query parameter.

A comparision compares a property name to a literal. The comparisons supported are the following:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “ne” : Is a property not equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /virtualization/v1beta1/hypervisor-managers/{uuid}/tags?filter="state eq OK"

Filters are supported on the following attributes:
* state
* createdAt
* name
* services
* displayName
* associatedResources/id
* categoryName

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified, the
default order is ascending.

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the hypervisor tag resource.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created.

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `items.associatedResources` (array)
    List of resources to which this tag is associated.

  - `items.associatedResources.id` (string)
    An identifier for the resource, usually a UUID.

  - `items.associatedResources.resourceUri` (string)
    The URI reference for this resource.

  - `items.categoryName` (string)
    The category name is unique to the currently selected hypervisor manager.

  - `items.customerId` (string)
    The customer application identifier.

  - `items.displayName` (string)
    This will always be same as name since add or update of hypervisor tags are not supported when it is managed from a manager like vCenter.
    Example: "T-5"

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `items.hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `items.name` (string)
    Name of the tag as reported by the hypervisor manager.
    Example: "T-5"

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/tags/{tag-id}"

  - `items.services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `items.state` (string)
    The current state of the hypervisor tag.
    Enum: "OK", "DELETED"

  - `items.uid` (string)
    Hypervisor provided identifier of the hypervisor tag.
    Example: "8476c228-d128-519c-a2ac-a4932ff2109b"

  - `items.vmProtectionGroupsInfo` (array)
    Protection groups related to the hypervisor-tag.

  - `items.vmProtectionGroupsInfo.id` (string)
    Unique identifier for the Protection Group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.vmProtectionGroupsInfo.name` (string)
    Name of the Protection Group.
    Example: "myProtectionGroup"

  - `items.vmProtectionGroupsInfo.resourceUri` (string)
    Reference to resource.

  - `offset` (integer, required)
    The number of items to skip before starting to collect the result set

  - `total` (integer)
    Total number of documents matching filter criteria.

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


