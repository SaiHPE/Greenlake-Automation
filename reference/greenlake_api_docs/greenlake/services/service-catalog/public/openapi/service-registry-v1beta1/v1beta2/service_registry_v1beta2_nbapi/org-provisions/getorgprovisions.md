---
title: "GET /service-catalog/v1beta2/org-provisions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta2/service_registry_v1beta2_nbapi/org-provisions/getorgprovisions.md"
scraped_at: "2026-06-07T06:16:52.320045+00:00Z"
---

# Get Organization Provisions

Retrieve list of workspaces with their service offers and provisions at organization level. If parent workspace returns child workspaces with parent. For child workspaces returns only the child workspace.

Endpoint: GET /service-catalog/v1beta2/org-provisions
Version: v1beta2
Security: bearerAuth

## Header parameters:

  - `Hpe-Workspace-Id` (string, required)
    Required HPE workspace identifier

## Query parameters:

  - `organization-id` (string)
    organization id to filter the workspaces

  - `limit` (integer)
    Number of entries per page

  - `next` (string)
    Cursor for pagination to fetch the next page

  - `include-omnipresent` (boolean)
    Include service offers that do not need provisioning

## Response 200 fields (application/json):

  - `items` (array, required)
    List of workspace provisions

  - `items.id` (string, required)
    Unique identifier for the workspace

  - `items.type` (string, required)

  - `items.workspace` (object, required)

  - `items.workspace.id` (string, required)

  - `items.workspace.name` (string, required)

  - `items.workspace.parentId` (object, required)

  - `items.workspace.organizationId` (object, required)

  - `items.services` (array, required)

  - `items.services.serviceOffer` (object, required)

  - `items.services.serviceOffer.slug` (string, required)

  - `items.services.serviceOffer.staticLaunchUrl` (string)

  - `items.services.serviceOffer.workspaceTypes` (array)

  - `items.services.serviceOffer.workspaceOpModes` (array)

  - `items.services.serviceOffer.categories` (array)

  - `items.services.provisions` (array, required)

  - `items.services.provisions.region` (object, required)

  - `items.services.provisions.serviceManagerProvision` (object,null, required)

  - `items.services.provisions.serviceManagerProvision.serviceManager` (object, required)

  - `items.services.provisions.serviceManagerProvision.serviceManagerInstanceId` (string, required)

  - `items.services.provisions.serviceManagerProvision.workspaceTransferStatus` (string)

  - `items.services.provisions.serviceProvision` (object,null, required)

  - `items.services.provisions.serviceProvision.generation` (integer, required)

  - `items.services.provisions.serviceProvision.createdAt` (string, required)

  - `items.services.provisions.serviceProvision.updatedAt` (string, required)

  - `count` (integer, required)

  - `total` (integer, required)

  - `next` (string, required)
    Cursor for fetching the next page of results

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings

  - `message` (string, required)
    A user-friendly error message

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id

  - `errorDetails` (array, required)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Enum: "field", "header", "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.

  - `errorDetails.issues.description` (string, required)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings

  - `message` (string, required)
    A user-friendly error message

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    Source of the error.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.accessToken` (string)
    Status of access token.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings

  - `message` (string, required)
    A user-friendly error message

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    Source of the error.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.uiAuthorization` (string)
    Status of access token.

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings

  - `message` (string, required)
    A user-friendly error message

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.

  - `errorDetails.source` (string, required)
    Source of the error.

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.requestedItem` (string)
    Status of access token.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)

  - `errorCode` (string, required)

  - `message` (string, required)

  - `debugId` (string, required)

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)

  - `errorCode` (string, required)

  - `message` (string, required)

  - `debugId` (string, required)

  - `errorDetails` (array, required)

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


