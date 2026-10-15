---
title: "GET /service-catalog/v1beta1/media"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/media/paths/~1service-catalog~1v1beta1~1media/get.md"
scraped_at: "2026-06-07T06:16:45.588122+00:00Z"
---

# Get overall media

Endpoint: GET /service-catalog/v1beta1/media
Version: v1beta1
Security: bearerAuth

## Query parameters:

  - `filter` (string, required)
    Supports Odata format.  Supported Fields: category, serviceOfferId  Supported operand: _eq_  Supported operations: _and_

  - `next` (string)
    Specifies the start-id for the next page of media.

  - `limit` (integer)
    Number of entries per page

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Service offer media identifier
    Example: "9ff8ff64-c939-457f-a1ef-7d528e7169f6"

  - `items.resourceUri` (string, required)
    Service offer media URI
    Example: "/service-catalog/v1beta1/service-offers/4ab85f64-5717-4562-b3fc-2c963f66afa6/media/9ff8ff64-c939-457f-a1ef-7d528e7169f6"

  - `items.category` (string, required)
    File category LOGO/SCREENSHOT
    Enum: "LOGO", "SCREENSHOT", "VIDEO", "TUTORIAL"

  - `items.url` (string, required)
    S3/minio URL
    Example: "https://test-url.com/3fa85f64-5717-4562-b3fc-2c963f66afa6/logo/cia85f64-5717-4562-b3fc-2c963f66afa6.png"

  - `items.description` (string, required)
    summary about the media
    Example: "sample description"

  - `items.uploadStatus` (string, required)
    File upload status UPLOAD_PENDING/UPLOADED
    Enum: "UPLOAD_PENDING", "UPLOADED"

  - `items.sequence` (integer, required)
    sequence number
    Example: 2

  - `items.type` (string, required)
    resource type
    Example: "/service-catalog/media"

  - `items.createdBy` (string, required)
    Example: "user@company.com"

  - `items.createdAt` (string, required)
    Date and time at which the media was created.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.updatedAt` (string, required)
    Date and time at which the media was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.generation` (integer, required)
    Generated/updated version
    Example: 1

  - `next` (string, required)
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `count` (integer, required)

  - `total` (integer, required)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_SERVICE_CATALOG_BAD_REQUEST"

  - `message` (string, required)
    A user-friendly error message
    Example: "Service Offer 6c4ec6df-1c23-460f-aece-34573e88de19 does not exist"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
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
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_SERVICE_CATALOG_UNAUTHORIZED"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
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
    Status of access token.
    Example: "Expired"

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 409

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_SERVICE_CATALOG_CONFLICT"

  - `message` (string, required)
    A user-friendly error message
    Example: "Duplicate Service Provision."

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

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

  - `errorDetails.metadata.conflictType` (string)
    Status of access token.
    Example: "Duplicate"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_SERVICE_CATALOG_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    A user-friendly error message
    Example: "Internal Server Error"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "e0a0d57d-30cb-45f8-90cb-d6ea3501f70b"

  - `errorDetails` (array, required)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


