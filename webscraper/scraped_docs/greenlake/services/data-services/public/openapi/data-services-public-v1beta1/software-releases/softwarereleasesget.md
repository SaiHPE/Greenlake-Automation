---
title: "GET /data-services/v1beta1/software-releases/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/software-releases/softwarereleasesget.md"
scraped_at: "2026-06-07T06:15:22.906305+00:00Z"
---

# Get a Software Release

Get a single Software Release by its ID.

Endpoint: GET /data-services/v1beta1/software-releases/{id}
Version: 1.3.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The ID of a Software Release.

## Query parameters:

  - `select` (array)
    Comma separated properties to return in the result. If omitted, all properties will be returned. Selecting nested properties of an object is not supported.

## Response 200 fields (application/json):

  - `id` (string, required)
    An identifier for the resource, usually a UUID.
    Example: "497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `type` (string, required)
    The type of resource.
    Example: "data-services/software-release"

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1

  - `createdAt` (string, required)
    Example: "2019-08-24T14:15:22Z"

  - `updatedAt` (string, required)
    Example: "2019-08-24T14:15:22Z"

  - `resourceUri` (string, required)
    The self reference for this resource.
    Example: "/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `customerId` (string, required)
    The customer application identifier
    Example: "00000000000000000000000000000000"

  - `name` (string)
    A system specified name for the resource.
    Example: "Example v1.0.0"

  - `downloadable` (boolean)
    Whether the files within the Software Release can be downloaded.
    Example: true

  - `signature` (any)
    The metadata for files within a Software Release.
    Example: {"filename":"example.ova.sig","sha256Checksum":"c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6","sizeInBytes":1000}

  - `software` (object)
    The metadata for files within a Software Release.
    Example: {"filename\"":"example.ova","sha256Checksum\"":"d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505","sizeInBytes\"":10000}

  - `software.filename` (string)
    The name of a file in a Software Release.

  - `software.sha256Checksum` (string)
    The SHA-256 checksum of a file in a Software Release in hexadecimal.

  - `software.sizeInBytes` (integer)

  - `softwareComponent` (object)
    The Software Component a Software Release belongs to.
    Example: {"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example","type":"data-services/software-component"}

  - `softwareComponent.id` (string)
    The ID of the resource.
    Example: "497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `softwareComponent.name` (string)
    Example: "Example"

  - `softwareComponent.type` (string)
    Example: "data-services/software-component"

  - `stability` (string)
    The stabilities that can be assigned to a Software Release.
    Enum: "GENERAL_AVAILABILITY"

  - `usage` (string)
    An indicator of how a Software Release should be used:

- INSTALL: Used for an initial install, such as the OVA for a virtual machine.
- UPGRADE: Upgrades an existing release.
- UNIVERSAL: Acts as both an install and upgrade media.
    Enum: "INSTALL", "UPGRADE", "UNIVERSAL"

  - `version` (string)
    The version of a Software Release.
    Example: "1.0.0"

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


