---
title: "GET /service-catalog/v1alpha1/featured-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getfeaturedservices.md"
scraped_at: "2026-06-07T06:15:49.761451+00:00Z"
---

# Get Featured Service Offers

Get Featured Service Offers

Endpoint: GET /service-catalog/v1alpha1/featured-services
Version: v1alpha1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of featured services.

  - `limit` (integer)
    Number of entries per page

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.category` (string, required)
    An enumeration.
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.services` (array, required)

  - `items.services.service_offer` (object)
    Service Offer

  - `items.services.service_offer.id` (string, required)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.services.service_offer.name` (string, required)
    Name of the service offer
    Example: "Aruba Central"

  - `items.services.service_offer.slug` (string, required)
    Short identifier of an service offer
    Example: "AC"

  - `items.services.service_offer.overview` (string, required)
    Overview of the service offer
    Example: "Aruba Central overview"

  - `items.services.service_offer.capabilities` (array, required)
    List of capabilities
    Example: ["Capability 1","Capability 2"]

  - `items.services.service_offer.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.services.service_offer.service_offer_type` (string, required)
    Service Offer Type
    Enum: "FREE", "COMMON_TOOLS", "SAAS", "DEVICE_SAAS", "IAAS", "ORGANIZATION"

  - `items.services.service_offer.application_id` (string, required)
    Unique application to which this service-offer is associated with
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.services.service_offer.workspace_types` (array, required)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.services.service_offer.features_supported` (array, required)
    Features supported
    Enum: "DEEP_LINKING", "SERVICE_PROVISIONING", "ORG_SINGLETON_SERVICE_PROVISIONING", "SKIP_SERVICE_MGR_PROVISIONING", "SKIP_SERVICE_UNPROVISIONING", "EVALUATION", "RBAC", "UI_DISABLE_PROVISIONING", "UI_DISABLE_UNPROVISIONING", "HONOR_UNPROVISION_RESPONSE", "ORG_PARENT_SUPPORTED"

  - `items.services.service_offer.languages_supported` (array, required)
    Codenames for supported languages
    Example: ["en-US","de-DE"]

  - `items.services.service_offer.logo` (object, required)
    S3/minio URL

  - `items.services.service_offer.logo.image` (string, required)
    S3/minio URL
    Example: "https://test-url.com/3fa85f64-5717-4562-b3fc-2c963f66afa6/logo/cia85f64-5717-4562-b3fc-2c963f66afa6.png"

  - `items.services.service_offer.logo.description` (string, required)
    summary about the media
    Example: "This is sample description"

  - `items.services.service_offer.screenshots` (array, required)
    S3/minio URLs for the screenshots

  - `items.services.service_offer.videos` (array, required)
    S3/minio URLs for the videos

  - `items.services.service_offer.videos.video` (string, required)
    S3/minio URL
    Example: "https://test-url.com/3fa85f64-5717-4562-b3fc-2c963f66afa6/logo/cia85f64-5717-4562-b3fc-2c963f66afa6.mp4"

  - `items.services.service_offer.documentation_url` (string, required)
    HTTPS URL for documentation
    Example: "https://"

  - `items.services.service_offer.terms_of_service_url` (string, required)
    HTTPS URL for terms of service
    Example: "https://www.hpe.com/us/en/about/legal/ccs-terms.html#Storage"

  - `items.services.service_offer.test_drive_url` (string, required)
    HTTPS URL for test drive
    Example: "https://testdrive.greenlake.hpe.com"

  - `items.services.service_offer.contact_sales_url` (string, required)
    HTTPS URL for contacting sales team
    Example: "https://contact-sales.hpe.com/"

  - `items.services.service_offer.status` (string, required)
    Status of a service offer
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

  - `items.services.service_offer.created_at` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.services.service_offer.type` (string, required)
    Type of resource
    Example: "/service-catalog/service-offers"

  - `items.services.service_offer.short_description` (string, required)
    short-descriptive line displayed on the service-offer title
    Example: "desc"

  - `items.services.service_offer.static_launch_url` (string, required)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `items.services.service_offer.eval_url` (string, required)
    URL to sign-up for evaluation of the service-offer for a limited time-period
    Example: "https://connect.hpe.com/HPE_Backup_and_Recovery_Trial"

  - `items.services.service_offer.broker_uri` (string, required)
    Applicable only to internal service-offers. Relative path starting with api-group. API-group suffices. Base-URI will be the api-gateway for the GLP cluster.
    Example: "/igc"

  - `items.services.service_offer.pre_provision_message` (string, required)
    Short warning/message displayed in the service-provision dialog box
    Example: "Users will be logged out during provisioning."

  - `items.services.service_offer.workspace_op_modes` (array, required)
    Types of Workspace Operational Modes for Tenant Workspaces
    Enum: "ALL", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `items.services.service_offer.is_service_manager` (boolean)
    Boolean to define a service offer is service manager
    Example: true

  - `items.services.service_offer.updated_at` (string)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.services.service_offer.generation` (integer)
    Generated/updated version
    Example: 1

  - `items.services.available_regions` (array)
    Names of the regions where the Service Offer is available for the logged in user/customer.

  - `items.services.available_regions.code` (string)
    Example: "us-east"

  - `items.services.available_regions.name` (string)
    Example: "US East"

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


