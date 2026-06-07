---
title: "GET /data-services/v1beta1/secret-assignments"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secret-assignments/reportassignmentsv1.md"
scraped_at: "2026-06-07T06:15:22.067133+00:00Z"
---

# Reports filtered assignments

Reports the attributes of the assignments owned by the customer. The response can be paged by using the limit and offset query parameters and filtered and sorted by using the filter and sort query parameters.

Endpoint: GET /data-services/v1beta1/secret-assignments
Version: 1.3.0
Security: 

## Query parameters:

  - `filter` (string)
    An OData expression to filter responses by attribute. The OData logical operator "eq" is case-sensitive and supported for attributes "applianceId", "secretId", "goal", "service", or "status". The OData function "contains()" is not case-sensitive and supported for attribute "applianceId", "secretId", and "service". The OData logical operator "and" is supported for all attributes.

  - `sort` (string)
    A response attribute to sort by, followed by a direction indicator ("asc" or "desc"). The attribute may be one of "applianceId", "secretId", "createdAt", "goal", "id", "label", "service", "status" or "updatedAt". Default: ascending.

  - `offset` (integer)
    The offset query parameter should be used in conjunction with limit for paging within a batched result set. The offset is the number of items from the beginning of the batched result set to the first item included in the response. Example: offset=30&limit=10

  - `limit` (integer)
    The limit query parameter should be used in conjunction with offset for paging within a batched result set. The limit is the maximum number of items to include in the response. Example: offset=30&limit=10

## Response 200 fields (application/json):

  - `count` (integer, required)
    Current results page count

  - `items` (array, required)
    Assignment resource definitions

  - `items.customerId` (string, required)
    Identifier of the customer owning the resource

  - `items.service` (string, required)
    Name of the service originating the resource

  - `items.id` (string, required)
    Identifier of the resource

  - `items.name` (string, required)
    Name of the resource

  - `items.type` (string, required)
    Type of the resource

  - `items.resourceUri` (string, required)
    URI of the resource

  - `items.generation` (integer, required)
    Update generation number

  - `items.updatedAt` (string, required)
    Timestamp of the last resource update

  - `items.createdAt` (string, required)
    Timestamp of the resource creation

  - `items.status` (string, required)
    Current status of the assignment

  - `items.statusUpdatedAt` (string, required)
    Timestamp of the last status update

  - `items.goal` (string, required)
    Current goal of the assignment

  - `items.goalUpdatedAt` (string, required)
    Timestamp of the last goal update

  - `items.secret` (object, required)
    Secret resource reference

  - `items.appliance` (object, required)
    Appliance identifier

  - `items.appliance.id` (string, required)
    Identity of the appliance

  - `items.groups` (array)
    Groups associated with the resource

  - `items.groups.id` (string, required)
    Identifier of the associated group

  - `items.groups.name` (string)
    Name of the associated group

  - `items.groups.resourceUri` (string)
    URI of the associated group

  - `items.label` (string)
    Consumer-defined label of the assignment

  - `next` (string)
    Cursor for next results page

  - `offset` (integer)
    Offset of current results page

  - `total` (integer)
    Total results count

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    Error code

  - `message` (string, required)
    Error message

  - `debugId` (string, required)
    Debug ID


