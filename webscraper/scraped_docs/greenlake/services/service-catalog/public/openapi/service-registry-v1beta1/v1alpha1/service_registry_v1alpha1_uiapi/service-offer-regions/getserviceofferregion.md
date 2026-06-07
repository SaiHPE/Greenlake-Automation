---
title: "GET /service-catalog/v1alpha1/service-offer-regions/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_uiapi/service-offer-regions/getserviceofferregion.md"
scraped_at: "2026-06-07T06:16:48.666102+00:00Z"
---

# Retrieve the service offer region details

Get Service Offer Region

Endpoint: GET /service-catalog/v1alpha1/service-offer-regions/{id}
Version: v1alpha1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    Service offer Region ID

## Response 200 fields (application/json):

  - `id` (string, required)
    Service offer region identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `service_offer_id` (string, required)
    Service offer identifier
    Example: "b93ebfc8-1589-11ee-be56-0242ac120002"

  - `region` (string, required)
    Example: "us-east"

  - `status` (string, required)
    Status of a service offer
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

  - `created_at` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `updated_at` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `generation` (integer, required)
    Representing instance-version of this resource
    Example: "1"

  - `type` (string, required)
    Type of resource
    Example: "/service-catalog/service-offer-region"

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

## Response 403 fields (application/json):

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


