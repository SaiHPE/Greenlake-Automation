---
title: "GET /service-catalog/v1beta2/recent-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/ui-management/getrecentservicesv2.md"
scraped_at: "2026-06-07T06:15:51.998236+00:00Z"
---

# Get Recent Services

Get data to populate Recent Services V2

Endpoint: GET /service-catalog/v1beta2/recent-services
Version: v1beta1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of recent services.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `limit` (integer)
    Number of entries per page

## Response 200 fields (application/json):

  - `items` (array, required)
    Service offer with provisions and last accessed timestamp

  - `items.id` (string, required)
    Id of service-manager-provision entry or service-provision entry
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.type` (string, required)
    Resource Type
    Example: "/service-catalog/recent-service"

  - `items.region` (object, required)

  - `items.region.id` (string)
    The code name for a geographical region supported by the HPE GreenLake cloud.
    Example: "us-east"

  - `items.region.type` (string)
    The resource type identifier for the region.
    Example: "/service-catalog/region"

  - `items.region.name` (string)
    The human-readable name for the geographical region.
    Example: "US East"

  - `items.lastAccessedTime` (string, required)
    Most recent date and time at which service was launched
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.serviceOffer` (object, required)
    Service offer abraged information. Typically used when only available service-offers in a workspace are to be reported.

  - `items.serviceOffer.id` (string, required)
    Identifier of service offer
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.serviceOffer.resourceUri` (string, required)
    Resource URI
    Example: "/service-catalog/v1beta1/service-offers/7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.serviceOffer.name` (string, required)
    Name of the Service Offer. In case of an app-provision, name of service-manager will be picked. If absent, name of app will be picked.
    Example: "Aruba Central"

  - `items.serviceOffer.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.serviceOffer.slug` (string, required)
    Short identifier for a service offer. In case of an app-provision, slug will be picked from service-manager. If absent, slug will be picked from application.
    Example: "CENTRAL"

  - `items.serviceOffer.staticLaunchUrl` (string, required)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `items.serviceOffer.serviceManager` (object)

  - `items.serviceOffer.serviceManager.id` (string)
    The unique identifier for the service manager.
    Example: "7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.serviceOffer.serviceManager.resourceUri` (string)
    The URI reference to the service manager resource.
    Example: "/service-catalog/v1beta1/service-managers/7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.serviceManagerProvision` (object)
    Service manager provision abraged information. Typically used when only fully provisioned entries are needed.

  - `items.serviceManagerProvision.id` (string, required)
    Example: "2fa85f6457174562b3fc2c963f66afa1"

  - `items.serviceManagerProvision.resourceUri` (string, required)
    URI to the service manager provision resource
    Example: "/service-catalog/v1beta1/service-manager-provisions/2fa85f6457174562b3fc2c963f66afa1"

  - `items.serviceManagerProvision.serviceManagerInstanceId` (string, required)
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.serviceManagerProvision.generation` (integer, required)
    Monotonically increasing update counter.
    Example: 1

  - `items.serviceManagerProvision.createdBy` (string)
    Example: "user@company.com"

  - `items.serviceManagerProvision.createdAt` (string)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.serviceManagerProvision.updatedAt` (string)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.serviceProvision` (object)
    Service provision abraged information. Typically used when only fully provisioned entries are needed.

  - `items.serviceProvision.id` (string, required)
    Service provision identifier
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.serviceProvision.resourceUri` (string, required)
    Example: "/service-catalog/v1beta1/service-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.serviceProvision.generation` (integer, required)
    Generated/updated version
    Example: 1

  - `next` (string, required)
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `count` (integer, required)
    Count Per Page

  - `total` (integer, required)
    Total Count

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_SERVICE_CATALOG_BAD_REQUEST"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Service Offer 6c4ec6df-1c23-460f-aece-34573e88de19 does not exist"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `errorDetails` (array, required)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.bad_request"

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Enum: "field", "header", "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "id"

  - `errorDetails.issues.description` (string, required)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Invalid format."

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_SERVICE_CATALOG_UNAUTHORIZED"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.metadata"

  - `errorDetails.source` (string, required)
    Source of the error.
    Example: "hpe.greenlake.iam"

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.accessToken` (string)
    Status of the access token.
    Example: "Expired"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_SERVICE_CATALOG_FORBIDDEN"

  - `message` (string, required)
    A user-friendly error message.
    Example: "The user is not authorized to perform the request"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "8567e466-7322-414a-b7d4-6832c3ce8f47"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.metadata"

  - `errorDetails.source` (string, required)
    Source of the error.
    Example: "hpe.greenlake.iam"

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.uiAuthorization` (string)
    Status of the access token.
    Example: "Failed"

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 429

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_SERVICE_CATALOG_ERROR_TOO_MANY_REQUESTS"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Current request can not be processed due to unknown issue."

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "64136af7-cd64-4b4e-88a8-150ab51a969d"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.metadata"

  - `errorDetails.source` (string, required)
    Source of the error.
    Example: "hpe.greenlake.service-catalog"

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.issue` (string)
    Status of the access token.
    Example: "Unknown"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_SERVICE_CATALOG_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    A user-friendly error message.
    Example: "Internal Server Error"

  - `debugId` (string, required)
    A unique identifier for the instance of this error.
    Example: "e0a0d57d-30cb-45f8-90cb-d6ea3501f70b"

  - `errorDetails` (array, required)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


