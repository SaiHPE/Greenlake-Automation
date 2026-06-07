---
title: "GET /service-catalog/v1alpha1/unredacted-service-offers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1alpha1/service_registry_v1alpha1_internal_api/unredacted-service-offers/getunredactedserviceoffers.md"
scraped_at: "2026-06-07T06:16:51.221009+00:00Z"
---

# Get Unredacted Service Offers

Get Unredacted Service Offer list by filters applied

Endpoint: GET /service-catalog/v1alpha1/unredacted-service-offers
Version: v1alpha1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of service offers.

  - `limit` (integer)
    Number of entries per page

  - `category` (string)
    Get service offer list by category
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `application_id` (string)
    Get service offer list of an application
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `status` (string)
    Get service offer list for a status
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

  - `is_service_manager` (boolean)
    Get list of service managers
    Example: true

  - `slug` (string)
    Get list of service offers by slug
    Example: "GLP"

  - `static_launch_url` (string)
    Get list of service offers by slug
    Example: "/Organization"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.name` (string, required)
    Name of the service offer
    Example: "Aruba Central"

  - `items.slug` (string, required)
    Short identifier of an service offer
    Example: "AC"

  - `items.overview` (string, required)
    Overview of the service offer
    Example: "Aruba Central overview"

  - `items.capabilities` (array, required)
    List of capabilities
    Example: ["Capability 1","Capability 2"]

  - `items.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.service_offer_type` (string, required)
    Service Offer Type
    Enum: "FREE", "COMMON_TOOLS", "SAAS", "DEVICE_SAAS", "IAAS", "ORGANIZATION"

  - `items.application_id` (string, required)
    Unique application to which this service-offer is associated with
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.workspace_types` (array, required)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.features_supported` (array, required)
    Features supported
    Enum: "DEEP_LINKING", "SERVICE_PROVISIONING", "ORG_SINGLETON_SERVICE_PROVISIONING", "SKIP_SERVICE_MGR_PROVISIONING", "SKIP_SERVICE_UNPROVISIONING", "EVALUATION", "RBAC", "HONOR_UNPROVISION_RESPONSE", "ORG_PARENT_SUPPORTED"

  - `items.languages_supported` (array, required)
    Codenames for Supported Languages
    Example: ["en-US","de-DE"]

  - `items.logo` (string, required)
    S3/minio URL

  - `items.screenshots` (array, required)
    S3/minio URLs for the screenshots
    Example: ["url1","url2"]

  - `items.documentation_url` (string, required)
    HTTPS URL for documentation
    Example: "https://"

  - `items.terms_of_service_url` (string, required)
    HTTPS URL for terms of service
    Example: "https://www.hpe.com/us/en/about/legal/ccs-terms.html#Storage"

  - `items.test_drive_url` (string, required)
    HTTPS URL for test drive
    Example: "https://testdrive.greenlake.hpe.com"

  - `items.contact_sales_url` (string, required)
    HTTPS URL for contacting sales team
    Example: "https://contact-sales.hpe.com/"

  - `items.status` (string, required)
    Status of a service offer
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

  - `items.created_at` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.dev_accounts` (array, required)
    Example: ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]

  - `items.submitter` (string, required)
    Example: "abcd@hpe.com"

  - `items.submitter_type` (string, required)
    Enum: "USER", "SERVICEMANAGER"

  - `items.type` (string, required)
    Type of resource
    Example: "/service-catalog/detailed-service-offers"

  - `items.short_description` (string, required)
    short-descriptive line displayed on the service-offer title
    Example: "desc"

  - `items.static_launch_url` (string, required)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `items.eval_url` (string, required)
    URL to sign-up for evaluation of the service-offer for a limited time-period
    Example: "https://connect.hpe.com/HPE_Backup_and_Recovery_Trial"

  - `items.broker_uri` (string, required)
    Applicable only to internal service-offers. Relative path starting with api-group. API-group suffices. Base-URI will be the api-gateway for the GLP cluster.
    Example: "/igc"

  - `items.pre_provision_message` (string, required)
    Short warning/message displayed in the service-provision dialog box
    Example: "Users will be logged out during provisioning."

  - `items.workspace_op_modes` (array, required)
    Types of Workspace Operational Modes for Tenant Workspaces
    Enum: "ALL", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `items.is_service_manager` (boolean)
    Boolean to define a service offer is service manager
    Example: true

  - `items.updated_at` (string)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.generation` (integer)
    Generated/updated version
    Example: 1

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


