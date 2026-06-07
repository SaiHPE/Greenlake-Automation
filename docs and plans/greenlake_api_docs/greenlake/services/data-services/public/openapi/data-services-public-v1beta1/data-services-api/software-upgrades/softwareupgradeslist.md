---
title: "GET /data-services/v1beta1/software-upgrades"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/software-upgrades/softwareupgradeslist.md"
scraped_at: "2026-06-07T06:15:17.606283+00:00Z"
---

# List upgrades for a Software Release

List the available upgrades for an installed Software Release, identified by a version and
Software Component ID. Pagination is not supported on the returned items.

The returned items are upgrades that can be applied to an existing installation of a Software
Release. Some releases can be applied immediately, while others may require corrective
actions to be completed before the release is allowed.

Upgrades beyond those initially returned can be found by recursively calling this API with
the new Software Release version. This can be useful for presenting the series of updates
required to bring an installation to the latest version.

Endpoint: GET /data-services/v1beta1/software-upgrades
Version: 1.3.0
Security: bearer

## Query parameters:

  - `software-component-id` (string, required)
    The ID of a Software Component.

  - `version` (string, required)
    The version of an installed Software Release that is being upgraded.

  - `serial-number` (string)
    The serial number of the hardware being upgraded. Either agent-id or serial-number must
be supplied.
    Example: "AC-109329"

  - `agent-id` (string)
    The identifier for the virtual machine being upgraded. Either agent-id or serial-number
must be supplied.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.
    Example: 2

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)
    The software upgrades.
    Example: [{"allowed":true,"id":"497f6eca-6276-5993-bfeb-53cbbbba6f08","notes":[],"softwareRelease":{"createdAt":"2019-08-24T14:15:22Z","customerId":"00000000000000000000000000000000","downloadable":true,"generation":1,"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example v1.0.0","resourceUri":"/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08","signature":{"filename":"example.iso.sig","sha256Checksum":"c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6","sizeInBytes":1000},"software":{"filename\"":"example.iso","sha256Checksum\"":"d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505","sizeInBytes\"":10000},"softwareComponent":{"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example","type":"data-services/software-component"},"stability":"GENERAL_AVAILABILITY","type":"data-services/software-release","updatedAt":"2019-08-24T14:15:22Z","usage":"UPGRADE","version":"1.0.0"},"type":"data-services/software-upgrade"},{"allowed":false,"id":"example-2","notes":["Action required"],"softwareRelease":{"createdAt":"2019-08-24T14:15:22Z","customerId":"00000000000000000000000000000000","downloadable":true,"generation":1,"id":"497f6eca-6276-5993-bfeb-53cbbbba6f07","name":"Example v2.0.0","resourceUri":"/data-services/v1beta1/software-releases/497f6eca-6276-4993-bfeb-53cbbbba6f08","signature":{"filename":"example.iso.sig","sha256Checksum":"c6a73c39b2c0d1f91594f81d01f0b79f40f6cd7a939cb3b6f1775fcf939ab3e6","sizeInBytes":1000},"software":{"filename\"":"example.iso","sha256Checksum\"":"d63c742ff2c761619914400c18f34d2368ae84babc7eac9ffcaea8f40b68b505","sizeInBytes\"":10000},"softwareComponent":{"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","name":"Example","type":"data-services/software-component"},"stability":"GENERAL_AVAILABILITY","type":"data-services/software-release","updatedAt":"2019-08-24T14:15:22Z","usage":"UPGRADE","version":"2.0.0"},"type":"data-services/software-upgrade"}]

  - `items.id` (string, required)
    The ID of the resource.

  - `items.type` (string, required)
    The type of resource.

  - `items.allowed` (boolean)
    Whether access to the release is currently allowed. If it is not allowed, the
notes property contains actions to complete to make it allowed.

  - `items.notes` (array)
    Actions to completed before the upgrade is allowed. Empty if allowed is true.

  - `items.softwareRelease` (object)
    A release of software.

  - `items.softwareRelease.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.softwareRelease.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.softwareRelease.createdAt` (string, required)

  - `items.softwareRelease.updatedAt` (string, required)

  - `items.softwareRelease.resourceUri` (string, required)
    The self reference for this resource.

  - `items.softwareRelease.customerId` (string, required)
    The customer application identifier

  - `items.softwareRelease.name` (string)
    A system specified name for the resource.

  - `items.softwareRelease.downloadable` (boolean)
    Whether the files within the Software Release can be downloaded.

  - `items.softwareRelease.signature` (any)
    The metadata for files within a Software Release.

  - `items.softwareRelease.software` (object)
    The metadata for files within a Software Release.

  - `items.softwareRelease.software.filename` (string)
    The name of a file in a Software Release.

  - `items.softwareRelease.software.sha256Checksum` (string)
    The SHA-256 checksum of a file in a Software Release in hexadecimal.

  - `items.softwareRelease.software.sizeInBytes` (integer)

  - `items.softwareRelease.softwareComponent` (object)
    The Software Component a Software Release belongs to.

  - `items.softwareRelease.softwareComponent.name` (string)

  - `items.softwareRelease.softwareComponent.type` (string)

  - `items.softwareRelease.stability` (string)
    The stabilities that can be assigned to a Software Release.
    Enum: "GENERAL_AVAILABILITY"

  - `items.softwareRelease.usage` (string)
    An indicator of how a Software Release should be used:

- INSTALL: Used for an initial install, such as the OVA for a virtual machine.
- UPGRADE: Upgrades an existing release.
- UNIVERSAL: Acts as both an install and upgrade media.
    Enum: "INSTALL", "UPGRADE", "UNIVERSAL"

  - `items.softwareRelease.version` (string)
    The version of a Software Release.

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


