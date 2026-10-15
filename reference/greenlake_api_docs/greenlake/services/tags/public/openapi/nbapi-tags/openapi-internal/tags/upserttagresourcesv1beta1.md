---
title: "PUT /tags/v1beta1/tag-resources/upsert"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/tags/public/openapi/nbapi-tags/openapi-internal/tags/upserttagresourcesv1beta1.md"
scraped_at: "2026-06-07T06:16:25.726466+00:00Z"
---

# Insert or update the tagged resources for a workspace (deprecated)

Insert or update a list of tagged resources for a workspace.

Endpoint: PUT /tags/v1beta1/tag-resources/upsert
Version: v1
Security: Bearer

## Header parameters:

  - `Hpe-Workspace-Id` (string, required)
    The uniquer identifier of the workspace to which the tagged resources are associated.

  - `Hpe-Username` (string)
    The username of the user who triggered the insertion or update of the tagged resource.

## Request fields (application/json):

  - `resources` (array, required)

  - `resources.resource` (object, required)
    The detail of the tagged resource.

  - `resources.resource.id` (string, required)
    The unique identifier of the tagged resource, if there is any associated tag.

  - `resources.resource.resourceType` (string, required)
    The type of the tagged resource, if there is any associated tag.

  - `resources.tags` (object, required)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer)

  - `errorCode` (string)

  - `message` (string)

  - `debugId` (string)

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 401 fields (application/json):

  - `httpStatusCode` (integer)

  - `errorCode` (string)

  - `message` (string)

  - `debugId` (string)

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 403 fields (application/json):

  - `httpStatusCode` (integer)

  - `errorCode` (string)

  - `message` (string)

  - `debugId` (string)

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 429 fields (application/json):

  - `httpStatusCode` (integer)

  - `errorCode` (string)

  - `message` (string)

  - `debugId` (string)

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)

## Response 500 fields (application/json):

  - `httpStatusCode` (integer)

  - `errorCode` (string)

  - `message` (string)

  - `debugId` (string)

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    The source of the error, typically a registered API group.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.recommendedActions` (array)


## Response 204 fields
