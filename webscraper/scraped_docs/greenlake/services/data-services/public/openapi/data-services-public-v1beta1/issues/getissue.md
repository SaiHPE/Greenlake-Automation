---
title: "GET /data-services/v1beta1/issues/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/issues/getissue.md"
scraped_at: "2026-06-07T06:15:21.304078+00:00Z"
---

# Get a singular issue

Returns an active issue with the specified id for the account obtained from the request header. The issue must be in the CREATED state

Endpoint: GET /data-services/v1beta1/issues/{id}
Version: 1.3.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the issue

## Query parameters:

  - `select` (string)
    Limits the properties returned with a resource or collection-level GET. Specify a comma-separated list of properties.
(e.g.: "?select=id,type,customerId,services,createdAt,lastOccurredAt,generation,resourceUri")

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

  - `body` (string)
    Long description with more details including possible remediations.

  - `category` (string)
    Category of the issue. PERFORMANCE, CAPACITY, etc

  - `clearedAt` (string)
    Time when the issue was cleared. RFC 3339 timestamp

  - `groups` (array)
    Groups this issue is associated with.

  - `groups.id` (string, required)
    ID of the associated group

  - `groups.name` (string, required)
    Name of the associated group

  - `issueType` (string)
    The type of the issue. Eg: ISSUE

  - `lastOccurredAt` (string)
    Time when the issue last occurred. RFC 3339 timestamp

  - `occurrenceCount` (integer)
    Indicates the number of occurrences of the issue

  - `recommendation` (string)
    Recommendation to address the underlying issue.

  - `relatedResources` (array)
    Details of the resources related to the issue

  - `relatedResources.type` (string, required)

  - `relatedResources.resourceUri` (string, required)

  - `relatedResources.id` (string, required)

  - `relatedResources.name` (string)

  - `relatedResources.consoleUri` (string)
    console URI of the related object resource that is the source of the issue

  - `services` (array)
    Details of the services this issue belongs to

  - `severity` (string)
    Severity of the issue. For issue: CRITICAL, WARNING, INFO. For reco: HIGH, MEDIUM, LOW

  - `snoozed` (boolean)
    An auxiliary calculated attribute to help the end-user filter snoozed and un-snoozed issues

  - `snoozedBy` (string)
    The email id of the last user who snoozed this issue.

  - `snoozedFor` (string)
    Enum: "NONE", "DAY", "WEEK", "MONTH", "INFINITE"

  - `snoozedUntil` (string)
    Date-time until this issue will be considered snoozed/inactive until this time. RFC 3339

  - `sourceResourceId` (string)
    Identifier for the source resource that is contained in relatedResources

  - `sourceResourceType` (string)
    Type of the source resource that is contained in the relatedResources

  - `state` (string)
    State of the issue. Eg: CREATED, ASSIGNED, CLOSED, SNOOZED, DELETED, etc

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

## Response 405 fields (application/json):

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

## Response 409 fields (application/json):

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


