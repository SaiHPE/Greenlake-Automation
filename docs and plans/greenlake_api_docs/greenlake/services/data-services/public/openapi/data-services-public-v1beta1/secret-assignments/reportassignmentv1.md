---
title: "GET /data-services/v1beta1/secret-assignments/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/secret-assignments/reportassignmentv1.md"
scraped_at: "2026-06-07T06:15:22.066432+00:00Z"
---

# Reports a specific assignment

Reports the attributes of the specified assignment.

Endpoint: GET /data-services/v1beta1/secret-assignments/{id}
Version: 1.3.0
Security: 

## Path parameters:

  - `id` (string, required)
    UUID of the secret

## Response 200 fields (application/json):

  - `customerId` (string, required)
    Identifier of the customer owning the resource

  - `service` (string, required)
    Name of the service originating the resource

  - `id` (string, required)
    Identifier of the resource

  - `name` (string, required)
    Name of the resource

  - `type` (string, required)
    Type of the resource

  - `resourceUri` (string, required)
    URI of the resource

  - `generation` (integer, required)
    Update generation number

  - `updatedAt` (string, required)
    Timestamp of the last resource update

  - `createdAt` (string, required)
    Timestamp of the resource creation

  - `status` (string, required)
    Current status of the assignment

  - `statusUpdatedAt` (string, required)
    Timestamp of the last status update

  - `goal` (string, required)
    Current goal of the assignment

  - `goalUpdatedAt` (string, required)
    Timestamp of the last goal update

  - `secret` (object, required)
    Secret resource reference

  - `appliance` (object, required)
    Appliance identifier

  - `appliance.id` (string, required)
    Identity of the appliance

  - `groups` (array)
    Groups associated with the resource

  - `groups.id` (string, required)
    Identifier of the associated group

  - `groups.name` (string)
    Name of the associated group

  - `groups.resourceUri` (string)
    URI of the associated group

  - `label` (string)
    Consumer-defined label of the assignment

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


