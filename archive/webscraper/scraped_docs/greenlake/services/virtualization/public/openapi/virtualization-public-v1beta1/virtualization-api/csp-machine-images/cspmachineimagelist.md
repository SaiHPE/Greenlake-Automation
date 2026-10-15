---
title: "GET /virtualization/v1beta1/csp-machine-images"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/csp-machine-images/cspmachineimagelist.md"
scraped_at: "2026-06-07T06:16:27.345623+00:00Z"
---

# Get a list of CSP machine images

Returns a list of cloud service provider (CSP) machine images based on the query
parameters for paging, filtering, and sorting.

Endpoint: GET /virtualization/v1beta1/csp-machine-images
Version: 1.2.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to omit from the beginning of the result set.
Use offset in conjunction with limit for pagination,
for example "offset=30&limit=10" indicates the fourth page of 10 items.
    Example: 30

  - `limit` (integer)
    The maximum number of items to include in the response.
Use offset in conjunction with limit for pagination,
for example "offset=30&limit=10" indicates the fourth page of 10 items.
    Example: 10

  - `filter` (string)
    An expression to filter the results.

Filtering is supported with following attributes:
 * name
 * cspInfo.id 
 * cspInfo.region
 * cspInfo.architecture
 * cspInfo.state
 * cspInfo.hypervisor
 * cspInfo.rootDeviceType
 * cspInfo.rootDeviceName
 * cspInfo.virtualizationType
 * cspType
 * cspInfo.location
 * cspInfo.ownerId
    Example: "filter=hypervisor eq 'hvm' and region eq 'eu-west-3'"

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc").
    Example: "name asc"

  - `select` (string)
    A list of properties to include in the response.
    Example: "id,name,state"

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

  - `items.consoleUri` (string)
    URI for the console screen that displays this resource

  - `items.cspInfo` (any)

  - `items.cspType` (string)
    The cloud service provider type
    Enum: "AWS", "AZURE"

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


