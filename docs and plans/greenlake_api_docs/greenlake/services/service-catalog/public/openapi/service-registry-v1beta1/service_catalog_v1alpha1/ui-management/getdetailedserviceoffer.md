---
title: "GET /service-catalog/v1alpha1/detailed-service-offers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getdetailedserviceoffer.md"
scraped_at: "2026-06-07T06:15:49.819407+00:00Z"
---

# Get Service Offer Details

Get Detailed Service Offer

Endpoint: GET /service-catalog/v1alpha1/detailed-service-offers/{id}
Version: v1alpha1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    Service Offer ID or SLUG
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6 or ABC"

## Response 200 fields (application/json):

  - `service_offer` (object, required)

  - `service_offer.id` (string, required)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `service_offer.name` (string, required)
    Name of the service offer
    Example: "Aruba Central"

  - `service_offer.slug` (string, required)
    Short identifier of an service offer
    Example: "AC"

  - `service_offer.overview` (string, required)
    Overview of the service offer
    Example: "Aruba Central overview"

  - `service_offer.capabilities` (array, required)
    List of capabilities
    Example: ["Capability 1","Capability 2"]

  - `service_offer.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `service_offer.service_offer_type` (string, required)
    Service Offer Type
    Enum: "FREE", "COMMON_TOOLS", "SAAS", "DEVICE_SAAS", "IAAS", "ORGANIZATION"

  - `service_offer.application_id` (string, required)
    Unique application to which this service-offer is associated with
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `service_offer.workspace_types` (array, required)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `service_offer.features_supported` (array, required)
    Features supported
    Enum: "DEEP_LINKING", "SERVICE_PROVISIONING", "ORG_SINGLETON_SERVICE_PROVISIONING", "SKIP_SERVICE_MGR_PROVISIONING", "SKIP_SERVICE_UNPROVISIONING", "EVALUATION", "RBAC", "UI_DISABLE_PROVISIONING", "UI_DISABLE_UNPROVISIONING", "HONOR_UNPROVISION_RESPONSE", "ORG_PARENT_SUPPORTED"

  - `service_offer.languages_supported` (array, required)
    Codenames for supported languages
    Example: ["en-US","de-DE"]

  - `service_offer.logo` (object, required)
    S3/minio URL

  - `service_offer.logo.image` (string, required)
    S3/minio URL
    Example: "https://test-url.com/3fa85f64-5717-4562-b3fc-2c963f66afa6/logo/cia85f64-5717-4562-b3fc-2c963f66afa6.png"

  - `service_offer.logo.description` (string, required)
    summary about the media
    Example: "This is sample description"

  - `service_offer.screenshots` (array, required)
    S3/minio URLs for the screenshots

  - `service_offer.videos` (array, required)
    S3/minio URLs for the videos

  - `service_offer.videos.video` (string, required)
    S3/minio URL
    Example: "https://test-url.com/3fa85f64-5717-4562-b3fc-2c963f66afa6/logo/cia85f64-5717-4562-b3fc-2c963f66afa6.mp4"

  - `service_offer.documentation_url` (string, required)
    HTTPS URL for documentation
    Example: "https://"

  - `service_offer.terms_of_service_url` (string, required)
    HTTPS URL for terms of service
    Example: "https://www.hpe.com/us/en/about/legal/ccs-terms.html#Storage"

  - `service_offer.test_drive_url` (string, required)
    HTTPS URL for test drive
    Example: "https://testdrive.greenlake.hpe.com"

  - `service_offer.contact_sales_url` (string, required)
    HTTPS URL for contacting sales team
    Example: "https://contact-sales.hpe.com/"

  - `service_offer.status` (string, required)
    Status of a service offer
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED", "HIDDEN"

  - `service_offer.created_at` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `service_offer.type` (string, required)
    Type of resource
    Example: "/service-catalog/service-offers"

  - `service_offer.short_description` (string, required)
    short-descriptive line displayed on the service-offer title
    Example: "desc"

  - `service_offer.static_launch_url` (string, required)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `service_offer.eval_url` (string, required)
    URL to sign-up for evaluation of the service-offer for a limited time-period
    Example: "https://connect.hpe.com/HPE_Backup_and_Recovery_Trial"

  - `service_offer.broker_uri` (string, required)
    Applicable only to internal service-offers. Relative path starting with api-group. API-group suffices. Base-URI will be the api-gateway for the GLP cluster.
    Example: "/igc"

  - `service_offer.pre_provision_message` (string, required)
    Short warning/message displayed in the service-provision dialog box
    Example: "Users will be logged out during provisioning."

  - `service_offer.workspace_op_modes` (array, required)
    Types of Workspace Operational Modes for Tenant Workspaces
    Enum: "ALL", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `service_offer.is_service_manager` (boolean)
    Boolean to define a service offer is service manager
    Example: true

  - `service_offer.updated_at` (string)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `service_offer.generation` (integer)
    Generated/updated version
    Example: 1

  - `available_regions` (array, required)
    Names of the regions where the Service Offer is available for the logged in user/customer.

  - `available_regions.code` (string)
    Example: "us-east"

  - `available_regions.name` (string)
    Example: "US East"

  - `available_regions.locations` (array)
    Example: ["Viriginia","California"]

  - `service_manager` (object, required)

  - `provisions` (array, required)
    Data pertaining to service and app provisions

  - `provisions.name` (string, required)
    Name of the Service Offer. In case of an app-provision, name of service-manager will be picked. If absent, name of app will be picked.
    Example: "Aruba Central"

  - `provisions.service_offer_id` (string, required)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `provisions.slug` (string, required)
    Short identifier for a service offer. In case of an app-provision, slug will be picked from service-manager. If absent, slug will be picked from application.
    Example: "CENTRAL"

  - `provisions.application_provision` (object, required)
    Example: {"username":"user@customer.com","provision_status":"PROVISIONED","account_type":"STANDALONE","region":"us-west","application_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","platform_customer_id":"8fa85f64-5717-4562-b3fc-2c963f66afa3","application_instance_id":"1fa85f64-5717-4562-b3fc-2c963f66afa2","msp_id":"STANDALONE","msp_conversion_status":"DEFAULT","application_customer_id":"9fa85f64-5717-4562-b3fc-2c963f66afa0","created_at":"2021-04-23T10:20:30.400+02:30","updated_at":"2021-04-23T10:20:30.400+02:30","workspace_transfer_status":"TRANSFER_COMPLETED","Reason":"Failed to configure IDP."}

  - `provisions.application_provision.region` (string, required)
    Example: "us-west"

  - `provisions.application_provision.application_id` (string, required)
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `provisions.application_provision.platform_customer_id` (string, required)
    Example: "8fa85f64-5717-4562-b3fc-2c963f66afa3"

  - `provisions.application_provision.msp_conversion_status` (string, required)
    Enum: "MSP_CONVERSION_INITIATED", "MSP_CONVERTED", "MSP_CONVERSION_FAILED"

  - `provisions.application_provision.operational_mode` (string, required)
    Enum: "ALL", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `provisions.application_provision.application_customer_id` (string, required)
    Example: "9fa85f64-5717-4562-b3fc-2c963f66afa0"

  - `provisions.application_provision.application_instance_id` (string, required)
    Example: "1fa85f64-5717-4562-b3fc-2c963f66afa2"

  - `provisions.application_provision.provision_status` (string, required)
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `provisions.application_provision.reason` (string, required)
    Reason for failure
    Example: "Failed to configure IDP."

  - `provisions.application_provision.username` (string)
    Example: "user@customer.com"

  - `provisions.application_provision.account_type` (string)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `provisions.application_provision.msp_id` (string)
    Example: "STANDALONE"

  - `provisions.application_provision.workspace_transfer_status` (string)
    Enum: "TRANSFER_INITIATED", "TRANSFER_COMPLETED", "TRANSFER_FAILED"

  - `provisions.service_provision` (object, required)
    Example: {"service_offer_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","region":"us-west","platform_customer_id":"8fa85f6457174562b3fc2c963f66afa3","platform_customer_name":"Hewlett Packard Enterprise","organization_id":"5ab85f64-6717-5562-c3fc-3c963f66afa6","id":"2fa85f64-5717-4562-b3fc-2c963f66afa9","application_customer_id":"9fa85f6457174562b3fc2c963f66afa0","application_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","application_instance_id":"1fa85f64-5717-4562-b3fc-2c963f66afa2","provision_status":"PROVISIONED","msp_id":"3da85f64-5717-4562-b3fc-2c963f66afa3","workspace_transfer_status":"TRANSFER_COMPLETED","reason":"Failed to configure IDP.","created_by":"user@customer.com","created_at":"2021-04-23T10:20:30.400+02:30","updated_at":"2021-04-23T10:20:30.400+02:30"}

  - `provisions.service_provision.platform_customer_name` (string, required)
    Example: "Hewlett Packard Enterprise"

  - `provisions.service_provision.organization_id` (string, required)
    Example: "5ab85f64-6717-5562-c3fc-3c963f66afa6"

  - `provisions.service_provision.id` (string, required)
    Service provision identifier
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `provisions.service_provision.reason` (string, required)
    Example: "Failed to configure IDP."

  - `provisions.service_provision.created_by` (string, required)
    Example: "user@customer.com"

  - `provisions.service_provision.type` (string)
    Example: "/service-catalog/service-provision"

  - `org_singleton_service_provisions` (array, required)
    Service-provision entry for the organization that the current workspace belongs to.

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


