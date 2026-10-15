---
title: "GET /data-services/v1beta1/software-releases"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-releases/softwarereleaseslist.md"
scraped_at: "2026-06-07T06:15:22.810637+00:00Z"
---

# List Software Releases

List multiple Software Releases with filtering, sorting and pagination.

Filtering is supported on the softwareComponent/id and version properties using the
eq, in, and and or operators. Sorting is supported on the id and version properties.

Endpoint: GET /data-services/v1beta1/software-releases
Version: 1.3.0
Security: bearer

## Query parameters:

  - `filter` (string)
    An expression to filter list query results. Query result items that match the given
filter are returned.

Expressions must be in the format \  \ or
\  \. The available operators are:

- eq: Test whether a property's value is equal to a literal.
- in: Test whether a property's value appears in a list of literals.

Literals can be:

- GUIDs, such as ae09cc99-57e1-4f82-9d80-e68698da641b.
- Strings, such as 'hello', 'world'.

Expressions can also be joined using the and and or logical operators.

  - `limit` (integer)
    The number of query results to return. Use limit in conjuction with offset for paging.

  - `offset` (integer)
    The offset to use for paging through the result set. Use offset in conjunction with limit for paging.

  - `select` (array)
    Comma separated properties to return in the result. If omitted, all properties will be returned. This is applied to sub-properties of the objects in the items array. Selecting nested properties of an object is not supported.

  - `sort` (string)
    One or more properties and directions to sort query results by. A direction is optional and can be either asc or desc for ascending and descending order respectively. If the direction is omitted it defaults to asc.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.
    Example: 1

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)
    The software releases returned by the query.
    Example: [{"createdAt":"2019-08-24T14:15:22Z","customerId":"00000000000000000000000000000000","downloadable":true,"generation":1,"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example v1.0.0","resourceUri":"/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08","signature":{"filename":"example.ova.sig","sha256Checksum":"c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6","sizeInBytes":1000},"software":{"filename\"":"example.ova","sha256Checksum\"":"d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505","sizeInBytes\"":10000},"softwareComponent":{"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example","type":"data-services/software-component"},"stability":"GENERAL_AVAILABILITY","type":"data-services/software-release","updatedAt":"2019-08-24T14:15:22Z","usage":"INSTALL","version":"1.0.0"}]

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.
    Example: "497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `items.type` (string, required)
    The type of resource.
    Example: "data-services/software-release"

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1

  - `items.createdAt` (string, required)
    Example: "2019-08-24T14:15:22Z"

  - `items.updatedAt` (string, required)
    Example: "2019-08-24T14:15:22Z"

  - `items.resourceUri` (string, required)
    The self reference for this resource.
    Example: "/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `items.customerId` (string, required)
    The customer application identifier
    Example: "00000000000000000000000000000000"

  - `items.name` (string)
    A system specified name for the resource.
    Example: "Example v1.0.0"

  - `items.downloadable` (boolean)
    Whether the files within the Software Release can be downloaded.
    Example: true

  - `items.signature` (any)
    The metadata for files within a Software Release.
    Example: {"filename":"example.ova.sig","sha256Checksum":"c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6","sizeInBytes":1000}

  - `items.software` (object)
    The metadata for files within a Software Release.
    Example: {"filename\"":"example.ova","sha256Checksum\"":"d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505","sizeInBytes\"":10000}

  - `items.software.filename` (string)
    The name of a file in a Software Release.

  - `items.software.sha256Checksum` (string)
    The SHA-256 checksum of a file in a Software Release in hexadecimal.

  - `items.software.sizeInBytes` (integer)

  - `items.softwareComponent` (object)
    The Software Component a Software Release belongs to.
    Example: {"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example","type":"data-services/software-component"}

  - `items.softwareComponent.id` (string)
    The ID of the resource.
    Example: "497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `items.softwareComponent.name` (string)
    Example: "Example"

  - `items.softwareComponent.type` (string)
    Example: "data-services/software-component"

  - `items.stability` (string)
    The stabilities that can be assigned to a Software Release.
    Enum: "GENERAL_AVAILABILITY"

  - `items.usage` (string)
    An indicator of how a Software Release should be used:

- INSTALL: Used for an initial install, such as the OVA for a virtual machine.
- UPGRADE: Upgrades an existing release.
- UNIVERSAL: Acts as both an install and upgrade media.
    Enum: "INSTALL", "UPGRADE", "UNIVERSAL"

  - `items.version` (string)
    The version of a Software Release.
    Example: "1.0.0"

  - `total` (integer)
    Total number of items matching the filter parameter in the request.
    Example: 1

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


