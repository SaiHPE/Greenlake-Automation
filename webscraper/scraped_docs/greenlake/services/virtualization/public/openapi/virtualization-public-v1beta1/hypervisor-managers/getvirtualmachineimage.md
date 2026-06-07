---
title: "GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images/{hypervisor-library-image-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/hypervisor-managers/getvirtualmachineimage.md"
scraped_at: "2026-06-07T06:16:32.505974+00:00Z"
---

# Get a hypervisor library image identified by {hypervisor-library-image-id}

Details of a virtual machine image

Endpoint: GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images/{hypervisor-library-image-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `hypervisor-id` (string, required)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `hypervisor-library-image-id` (string, required)
    UUID string uniquely identifying the virtual machine image from the hypervisor image library
    Example: "9476c228-d128-519c-a2ac-a4932ff2109b"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the virtual machine image from the hypervisor image library
    Example: "9476c228-d128-519c-a2ac-a4932ff2109b"

  - `type` (string, required)
    Hypervisor object type
    Example: "HypervisorLibraryImages"

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time at which the virtual machine image was created
    Example: "2022-02-04T07:43:27Z"

  - `updatedAt` (string, required)
    Time at which the virtual machine image was updated
    Example: "2022-02-04T08:43:27Z"

  - `customerId` (string)
    The customer application identifier.
    Example: "90299b6c06aa283091cd4a89298b5471"

  - `description` (string)
    Description given for the virtual machine image from the hypervisor image library
    Example: "This is a sample virtual machine image description"

  - `displayName` (string)
    Name of the virtual machine image
    Example: "CentOS.ova"

  - `fileType` (string)
    The type of the virtual machine image from the hypervisor manager image library
    Enum: "OVF"

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `hypervisorManagerInfo.resourceUri` (string)
    The URI reference for this resource.

  - `hypervisorManagerInfo.type` (string)
    The type of resource.

  - `libraryName` (string)
    Name of the hypervisor library
    Example: "LibraryImages"

  - `name` (string)
    Virtual machine image name
    Example: "Centos.ova"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "The URI reference for this resource."

  - `size` (integer)
    Size of the virtual machine image from the hypervisor manager image library in bytes
    Example: 15344

  - `subscribed` (boolean)
    True if the image will be pulled from a remote hypervisor image library (ex. vCenter subscribed content library).

  - `uid` (string)
    Hypervisor provided identifier of the virtual machine image from the hypervisor image library
    Example: "9476c228-d128-519c-a2ac-a4932ff2109b"

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


