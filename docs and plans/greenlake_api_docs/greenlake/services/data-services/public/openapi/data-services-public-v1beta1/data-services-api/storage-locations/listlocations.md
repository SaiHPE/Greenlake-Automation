---
title: "GET /data-services/v1beta1/storage-locations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/storage-locations/listlocations.md"
scraped_at: "2026-06-07T06:15:17.907709+00:00Z"
---

# List storage locations

Returns a list of enabled storage locations. The following parameters are supported to
reduce the collection according to the specified criteria:

- filtering locations by capabilities;

Endpoint: GET /data-services/v1beta1/storage-locations
Version: 1.3.0
Security: bearer

## Query parameters:

  - `filter` (string)
    The expression to use for filtering responses.

The filter expression for this endpoint accepts the following operators on the following
properties:

- in operator on the capabilities property;

For example:

- 'backup-and-recovery' in capabilities;

Grouping of expressions to change the evaluation precedence is NOT supported.
    Example: "'backup-and-recovery' in capabilities\n"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)
    The storage locations returned by the query.

  - `items.id` (string, required)
    An identifier for the resource.

  - `items.name` (string, required)
    A system specified name for the resource.

  - `items.cloudServiceProvider` (string, required)
    The Cloud Service Provider (CSP) of the location.
    Enum: "AWS", "AZURE", "GCP"

  - `items.cloudServiceProviderId` (string, required)
    The Cloud Service Provider (CSP) ID.

  - `items.geography` (string, required)
    The geographical location of the storage location.
    Enum: "North America", "Europe", "Asia Pacific"

  - `items.city` (string, required)
    The city the storage location is in.

  - `items.timezone` (string, required)
    The Timezone of the location as defined by the local standard time (non summer time) offset from UTC.

  - `items.capabilities` (array, required)
    The list of features that support the storage location.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)

  - `items.updatedAt` (string, required)

  - `items.resourceUri` (string, required)
    The 'self' reference for this resource.

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


