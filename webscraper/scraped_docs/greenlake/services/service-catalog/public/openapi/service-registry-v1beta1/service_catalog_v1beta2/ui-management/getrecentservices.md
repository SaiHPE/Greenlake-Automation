---
title: "GET /service-catalog/v1beta2/recent-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta2/ui-management/getrecentservices.md"
scraped_at: "2026-06-07T06:15:52.106434+00:00Z"
---

# Get Recent Services

Get data to populate Recent Services

Endpoint: GET /service-catalog/v1beta2/recent-services
Version: v1beta2
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of recent services.
    Example: ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]

  - `limit` (integer)
    Number of entries per page

## Response 200 fields (application/json):

  - `items` (array, required)
    Service offer with provisions and last accessed timestamp

  - `items.id` (string, required)
    Id of service-manager-provision entry or service-provision entry

  - `items.type` (string, required)
    Resource Type

  - `items.region` (object, required)

  - `items.region.id` (string)
    Code-name for a geo-region supported by GLP

  - `items.region.type` (string)
    Type of resource

  - `items.region.name` (string)
    Human readable name for the geo-region supported by GLP

  - `items.lastAccessedTime` (string, required)
    Most recent date and time at which service was launched

  - `items.serviceOffer` (object, required)
    Service offer abraged information. Typically used when only available service-offers in a workspace are to be reported.

  - `items.serviceOffer.id` (string, required)
    Identifier of service offer

  - `items.serviceOffer.resourceUri` (string, required)
    Resource URI

  - `items.serviceOffer.name` (string, required)
    Name of the Service Offer. In case of an app-provision, name of service-manager will be picked. If absent, name of app will be picked.

  - `items.serviceOffer.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.serviceOffer.slug` (string, required)
    Short identifier for a service offer. In case of an app-provision, slug will be picked from service-manager. If absent, slug will be picked from application.

  - `items.serviceOffer.staticLaunchUrl` (string, required)
    Relative URLs to launch

  - `items.serviceOffer.serviceManager` (object)

  - `items.serviceOffer.serviceManager.id` (string)
    Service Manager ID

  - `items.serviceManagerProvision` (object)
    Service manager provision abraged information. Typically used when only fully provisioned entries are needed.

  - `items.serviceManagerProvision.id` (string, required)

  - `items.serviceManagerProvision.resourceUri` (string, required)
    URI to the service manager provision resource

  - `items.serviceManagerProvision.serviceManagerInstanceId` (string, required)

  - `items.serviceManagerProvision.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.serviceManagerProvision.createdBy` (string)

  - `items.serviceManagerProvision.createdAt` (string)
    Date and time at which the service offer was created or upgraded.

  - `items.serviceManagerProvision.updatedAt` (string)
    Date and time at which the service offer was updated.

  - `items.serviceProvision` (object)
    Service provision abraged information. Typically used when only fully provisioned entries are needed.

  - `items.serviceProvision.id` (string, required)
    Service provision identifier

  - `items.serviceProvision.resourceUri` (string, required)

  - `items.serviceProvision.generation` (integer, required)
    Generated/updated version

  - `next` (string, required)

  - `count` (integer, required)
    Count Per Page

  - `total` (integer, required)
    Total Count

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

## Response 409 fields (application/json):

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


