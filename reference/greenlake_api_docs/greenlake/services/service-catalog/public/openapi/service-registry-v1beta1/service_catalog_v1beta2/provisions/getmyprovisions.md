---
title: "GET /service-catalog/v1beta2/provisions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta2/provisions/getmyprovisions.md"
scraped_at: "2026-06-07T06:15:52.067133+00:00Z"
---

# Get workspace services with provisions

Retrieves all services with their provisions for the authenticated user's workspace

Endpoint: GET /service-catalog/v1beta2/provisions
Version: v1beta2
Security: bearerAuth

## Header parameters:

  - `Hpe-Workspace-Id` (string, required)
    Required HPE workspace identifier

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of service offers.

  - `limit` (integer)
    Number of items per page

  - `include-omnipresent` (boolean)
    Include service offers that do not need provisioning

## Response 200 fields (application/json):

  - `items` (array, required)
    List of workspace service provisions

  - `items.id` (string, required)
    Unique identifier for the provision item

  - `items.type` (string, required)
    Resource type

  - `items.serviceOffer` (object, required)

  - `items.serviceOffer.name` (string, required)

  - `items.serviceOffer.slug` (string, required)

  - `items.serviceOffer.categories` (array, required)

  - `items.serviceOffer.staticLaunchUrl` (string)

  - `items.serviceOffer.workspaceTypes` (array)

  - `items.serviceOffer.workspaceOpModes` (array)

  - `items.provisions` (array, required)

  - `items.provisions.region` (object, required)

  - `items.provisions.region.id` (string, required)
    Region identifier

  - `items.provisions.region.name` (string, required)
    Full name of the region

  - `items.provisions.serviceManagerProvision` (object,null, required)

  - `items.provisions.serviceManagerProvision.id` (string, required)

  - `items.provisions.serviceManagerProvision.type` (string, required)

  - `items.provisions.serviceManagerProvision.serviceManager` (object, required)

  - `items.provisions.serviceManagerProvision.serviceManagerInstanceId` (string, required)

  - `items.provisions.serviceManagerProvision.workspaceTransferStatus` (string)

  - `items.provisions.serviceProvision` (object,null, required)

  - `items.provisions.serviceProvision.generation` (integer, required)

  - `items.provisions.serviceProvision.createdAt` (string, required)

  - `items.provisions.serviceProvision.updatedAt` (string, required)

  - `count` (integer, required)

  - `total` (integer, required)

  - `next` (string, required)
    Pagination cursor for next page

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


