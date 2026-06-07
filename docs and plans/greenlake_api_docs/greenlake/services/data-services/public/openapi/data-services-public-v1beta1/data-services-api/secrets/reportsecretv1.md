---
title: "GET /data-services/v1beta1/secrets/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/secrets/reportsecretv1.md"
scraped_at: "2026-06-07T06:15:17.108455+00:00Z"
---

# Reports a specific secret

Reports the attributes and properties of the specified secret.

Endpoint: GET /data-services/v1beta1/secrets/{id}
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

  - `domain` (object, required)
    Resource domain definition

  - `domain.name` (string, required)
    Name of the resource domain

  - `domain.properties` (object)
    Resource domain properties

  - `classifier` (object, required)
    Resource classifier definition

  - `classifier.name` (string, required)
    Name of the resource classifier

  - `subclassifier` (object, required)
    Resource subclassifier definition

  - `subclassifier.name` (string, required)
    Name of the resource subclassifier

  - `subclassifier.properties` (object)
    Resource subclassifier properties

  - `status` (string, required)
    Status of the resource

  - `statusUpdatedAt` (string, required)
    Timestamp of the last status update

  - `assignmentsCount` (integer)
    Count of associated assignment resources

  - `groups` (array)
    Groups associated with the resource

  - `groups.id` (string, required)
    Identifier of the associated group

  - `groups.name` (string)
    Name of the associated group

  - `groups.resourceUri` (string)
    URI of the associated group

  - `label` (string)
    Consumer-defined label of the resource

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


