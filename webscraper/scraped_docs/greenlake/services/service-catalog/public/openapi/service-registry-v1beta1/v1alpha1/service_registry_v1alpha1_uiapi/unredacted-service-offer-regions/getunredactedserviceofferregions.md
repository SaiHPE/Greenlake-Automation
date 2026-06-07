---
title: "GET /service-catalog/v1alpha1/unredacted-service-offer-regions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_uiapi/unredacted-service-offer-regions/getunredactedserviceofferregions.md"
scraped_at: "2026-06-07T06:16:49.258272+00:00Z"
---

# Get Unredacted Service Offer Regions

Get all service offer regions list by filters applied

Endpoint: GET /service-catalog/v1alpha1/unredacted-service-offer-regions
Version: v1alpha1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of service offer regions.

  - `limit` (integer)
    Number of entries per page

  - `service_offer_id` (string)
    Get service offer regions of a service offer ID
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `region` (string)
    Get service offer regions by region
    Example: "us-east"

  - `status` (string)
    Get service offer regions by status
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Service offer region identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.service_offer_id` (string, required)
    Service offer identifier
    Example: "b93ebfc8-1589-11ee-be56-0242ac120002"

  - `items.region` (string, required)
    Example: "us-east"

  - `items.rules` (array, required)

  - `items.rules.email_domains_included` (array, required)
    Example: ["hpe.com"]

  - `items.rules.email_domains_excluded` (array, required)
    Example: ["gmail.com"]

  - `items.rules.customers_included` (array, required)
    Example: ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]

  - `items.rules.customers_excluded` (array, required)
    Example: ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]

  - `items.rules.countries_groups_included` (array, required)
    Example: ["US"]

  - `items.rules.countries_groups_excluded` (array, required)
    Example: ["DB"]

  - `items.rules.app_instance_id` (string)
    Application instance ID
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.rules.description` (string)
    Description of the service offer region rule
    Example: "Rule for appID 1234"

  - `items.status` (string, required)
    Status of a service offer
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

  - `items.created_at` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.updated_at` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.generation` (integer, required)
    Representing instance-version of this resource
    Example: 1

  - `items.submitter_type` (string, required)
    Enum: "USER", "SERVICEMANAGER"

  - `items.submitter` (string, required)
    Example: "abcd@hpe.com"

  - `items.type` (string, required)
    Type of resource
    Example: "/service-catalog/unredacted-service-offer-region"

  - `paginate` (object, required)

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


