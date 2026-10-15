---
title: "GET /service-catalog/v1beta1/service-offer-regions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/service-offer-regions/getserviceofferregions.md"
scraped_at: "2026-06-07T06:15:50.366684+00:00Z"
---

# Get service offer regions

Retrieve a list of service offer regions by applying filters.
Each service offer region represents a service offer provisioned in a specific region.
Pagination: This API supports cursor-based pagination. Provide the cursor in the next query parameter to retrieve the next page.

Endpoint: GET /service-catalog/v1beta1/service-offer-regions
Version: v1beta1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the pagination cursor for the next page of service offer regions.
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `limit` (integer)
    Specifies the number of results to be returned.

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in a GET request. The returned set of resources must match the criteria in the filter query parameter. The value of the filter query parameter is a subset of OData 4.0 filter expressions consisting of simple comparison operations joined by logical operators.Supported fields: serviceOfferId, status, and region.Supported operand: eqSupported operations: and

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier for the service offer region.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.type` (string, required)
    The type of the resource.
    Example: "/service-catalog/service-offer-region"

  - `items.region` (string, required)
    The code name of the region where this service offer is available.
    Example: "us-east"

  - `items.status` (string, required)
    The current status of the service offer.
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED"

  - `items.createdAt` (string, required)
    Date and time at which the service offer was created.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.updatedAt` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.generation` (integer, required)
    A monotonically increasing update counter.
    Example: "1"

  - `items.resourceUri` (string)
    The URI reference to this resource.
    Example: "/service-catalog/v1beta1/service-offer-regions/3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.serviceOffer` (object)
    A service offer represents a specific set of features or capabilities that can be independently identified and assigned access. Service offers are typically associated with roles and permissions, commerce, metering, quote-to-cash, or trial evaluations.

  - `items.serviceOffer.id` (string)
    The unique identifier for the service offer.
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.serviceOffer.resourceUri` (string)
    The URI reference to the service offer resource.
    Example: "/service-catalog/v1beta1/service-offers/4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `next` (string, required)
    Cursor for the next page of resources.
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `count` (integer, required)
    The number of returned items per page.

  - `total` (integer, required)
    Total number of items in the result set.

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

## Response 429 fields (application/json):

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


