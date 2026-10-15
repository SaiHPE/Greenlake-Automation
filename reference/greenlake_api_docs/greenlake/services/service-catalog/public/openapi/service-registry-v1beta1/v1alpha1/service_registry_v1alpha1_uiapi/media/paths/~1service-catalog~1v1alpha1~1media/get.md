---
title: "GET /service-catalog/v1alpha1/media"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_uiapi/media/paths/~1service-catalog~1v1alpha1~1media/get.md"
scraped_at: "2026-06-07T06:16:47.749593+00:00Z"
---

# Get overall media

Endpoint: GET /service-catalog/v1alpha1/media
Version: v1alpha1
Security: bearerAuth

## Query parameters:

  - `category` (string, required)
    category

  - `service_offer_id` (string)
    Service Offer ID

  - `next` (string)
    Specifies the start-id for the next page of media.

  - `limit` (integer)
    Number of entries per page

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Service offer media identifier
    Example: "9ff8ff64-c939-457f-a1ef-7d528e7169f6"

  - `items.category` (string, required)
    File category LOGO/SCREENSHOT
    Enum: "LOGO", "SCREENSHOT", "VIDEO", "TUTORIAL"

  - `items.url` (string, required)
    S3/minio URL
    Example: "https://test-url.com/3fa85f64-5717-4562-b3fc-2c963f66afa6/logo/cia85f64-5717-4562-b3fc-2c963f66afa6.png"

  - `items.upload_status` (string, required)
    File upload status UPLOAD_PENDING/UPLOADED
    Enum: "UPLOAD_PENDING", "UPLOADED"

  - `items.description` (string, required)
    summary about the media
    Example: "desc"

  - `items.sequence` (integer, required)
    sequence number
    Example: 2

  - `items.type` (string, required)
    resource type
    Example: "/service-catalog/media"

  - `items.created_by` (string, required)
    Example: "user@company.com"

  - `items.created_at` (string, required)
    Date and time at which the media was created.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.updated_at` (string, required)
    Date and time at which the media was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.generation` (integer, required)
    Generated/updated version
    Example: 1

  - `paginate` (object)

  - `paginate.next` (string)

  - `paginate.count_per_page` (integer)

  - `paginate.total_count` (integer)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GLCP_ERROR_EXPIRED_TOKEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
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
    Example: "HPE_GLCP_ERROR_EXPIRED_TOKEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details
    Example: "hpe.greenlake.metadata"

  - `errorDetails.source` (string, required)
    The source of the error. Typically a registered API group
    Example: "hpe.greenlake.organizations"

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines

  - `errorDetails.metadata.recommendedActions` (array)
    Example: ["Contact admin to perform operation"]

## Response 409 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GLCP_ERROR_EXPIRED_TOKEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details
    Example: "hpe.greenlake.metadata"

  - `errorDetails.source` (string, required)
    The source of the error. Typically a registered API group
    Example: "hpe.greenlake.organizations"

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines

  - `errorDetails.metadata.recommendedActions` (array)
    Example: ["Contact admin to perform operation"]

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GLCP_ERROR_EXPIRED_TOKEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "12312-123123-123123-1231212"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


