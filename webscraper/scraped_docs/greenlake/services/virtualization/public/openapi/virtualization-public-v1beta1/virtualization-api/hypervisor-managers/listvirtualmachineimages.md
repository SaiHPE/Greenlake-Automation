---
title: "GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-managers/listvirtualmachineimages.md"
scraped_at: "2026-06-07T06:16:28.908073+00:00Z"
---

# Get all virtual machine images from the hypervisor library.

List all virtual machine images from the hypervisor library.

Endpoint: GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images
Version: 1.2.0
Security: bearer

## Path parameters:

  - `hypervisor-id` (string, required)
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

A comparison compares a property name to a literal. The following comparisons are supported:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /api/v1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images?filter="filetype eq OVF"

Filters are supported on the following attributes:
* fileType
* name
* services
* sizeInBytes
* subscribed

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
    UUID string uniquely identifying the virtual machine image from the hypervisor image library
    Example: "9476c228-d128-519c-a2ac-a4932ff2109b"

  - `items.type` (string, required)
    Hypervisor object type
    Example: "HypervisorLibraryImages"

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time at which the virtual machine image was created
    Example: "2022-02-04T07:43:27Z"

  - `items.updatedAt` (string, required)
    Time at which the virtual machine image was updated
    Example: "2022-02-04T08:43:27Z"

  - `items.customerId` (string)
    The customer application identifier.
    Example: "90299b6c06aa283091cd4a89298b5471"

  - `items.description` (string)
    Description given for the virtual machine image from the hypervisor image library
    Example: "This is a sample virtual machine image description"

  - `items.displayName` (string)
    Name of the virtual machine image
    Example: "CentOS.ova"

  - `items.fileType` (string)
    The type of the virtual machine image from the hypervisor manager image library
    Enum: "OVF"

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `items.hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `items.hypervisorManagerInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.hypervisorManagerInfo.type` (string)
    The type of resource.

  - `items.libraryName` (string)
    Name of the hypervisor library
    Example: "LibraryImages"

  - `items.name` (string)
    Virtual machine image name
    Example: "Centos.ova"

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "The URI reference for this resource."

  - `items.size` (integer)
    Size of the virtual machine image from the hypervisor manager image library in bytes
    Example: 15344

  - `items.subscribed` (boolean)
    True if the image will be pulled from a remote hypervisor image library (ex. vCenter subscribed content library).

  - `items.uid` (string)
    Hypervisor provided identifier of the virtual machine image from the hypervisor image library
    Example: "9476c228-d128-519c-a2ac-a4932ff2109b"

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


