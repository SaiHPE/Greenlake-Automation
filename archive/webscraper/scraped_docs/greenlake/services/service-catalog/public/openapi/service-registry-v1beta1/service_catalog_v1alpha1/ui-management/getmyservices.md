---
title: "GET /service-catalog/v1alpha1/my-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1alpha1/ui-management/getmyservices.md"
scraped_at: "2026-06-07T06:15:49.942431+00:00Z"
---

# Get My Services

Get data to populate My Services

Endpoint: GET /service-catalog/v1alpha1/my-services
Version: v1alpha1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of my services.

  - `limit` (integer)
    Number of entries per page

  - `include_omnipresent` (boolean)
    Specifies whether to include omnipresent service offers in response
    Example: true

## Response 200 fields (application/json):

  - `items` (array, required)
    Data pertaining to service and app provisions

  - `items.region` (string, required)
    Displayable region-name derived from region enum value
    Example: "US West"

  - `items.provisions` (array, required)

  - `items.provisions.name` (string, required)
    Name of the Service Offer. In case of an app-provision, name of service-manager will be picked. If absent, name of app will be picked.
    Example: "Aruba Central"

  - `items.provisions.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.provisions.service_offer_id` (string, required)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.provisions.slug` (string, required)
    Short identifier for a service offer. In case of an app-provision, slug will be picked from service-manager. If absent, slug will be picked from application.
    Example: "CENTRAL"

  - `items.provisions.static_launch_url` (string, required)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `items.provisions.workspace_types` (array, required)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.provisions.workspace_op_modes` (array, required)
    Types of Workspace Operational Modes for Tenant Workspaces
    Enum: "ALL", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `items.provisions.application_provision` (object, required)
    Example: {"username":"user@customer.com","provision_status":"PROVISIONED","account_type":"STANDALONE","region":"us-west","application_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","platform_customer_id":"8fa85f64-5717-4562-b3fc-2c963f66afa3","application_instance_id":"1fa85f64-5717-4562-b3fc-2c963f66afa2","msp_id":"STANDALONE","msp_conversion_status":"DEFAULT","application_customer_id":"9fa85f64-5717-4562-b3fc-2c963f66afa0","created_at":"2021-04-23T10:20:30.400+02:30","updated_at":"2021-04-23T10:20:30.400+02:30","workspace_transfer_status":"TRANSFER_COMPLETED","Reason":"Failed to configure IDP."}

  - `items.provisions.application_provision.region` (string, required)
    Example: "us-west"

  - `items.provisions.application_provision.application_id` (string, required)
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.provisions.application_provision.platform_customer_id` (string, required)
    Example: "8fa85f64-5717-4562-b3fc-2c963f66afa3"

  - `items.provisions.application_provision.msp_conversion_status` (string, required)
    Enum: "MSP_CONVERSION_INITIATED", "MSP_CONVERTED", "MSP_CONVERSION_FAILED"

  - `items.provisions.application_provision.operational_mode` (string, required)
    Enum: "ALL", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `items.provisions.application_provision.application_customer_id` (string, required)
    Example: "9fa85f64-5717-4562-b3fc-2c963f66afa0"

  - `items.provisions.application_provision.application_instance_id` (string, required)
    Example: "1fa85f64-5717-4562-b3fc-2c963f66afa2"

  - `items.provisions.application_provision.provision_status` (string, required)
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `items.provisions.application_provision.created_at` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.provisions.application_provision.updated_at` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.provisions.application_provision.reason` (string, required)
    Reason for failure
    Example: "Failed to configure IDP."

  - `items.provisions.application_provision.username` (string)
    Example: "user@customer.com"

  - `items.provisions.application_provision.account_type` (string)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.provisions.application_provision.msp_id` (string)
    Example: "STANDALONE"

  - `items.provisions.application_provision.workspace_transfer_status` (string)
    Enum: "TRANSFER_INITIATED", "TRANSFER_COMPLETED", "TRANSFER_FAILED"

  - `items.provisions.service_provision` (object, required)
    Example: {"service_offer_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","region":"us-west","platform_customer_id":"8fa85f6457174562b3fc2c963f66afa3","platform_customer_name":"Hewlett Packard Enterprise","organization_id":"5ab85f64-6717-5562-c3fc-3c963f66afa6","id":"2fa85f64-5717-4562-b3fc-2c963f66afa9","application_customer_id":"9fa85f6457174562b3fc2c963f66afa0","application_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","application_instance_id":"1fa85f64-5717-4562-b3fc-2c963f66afa2","provision_status":"PROVISIONED","msp_id":"3da85f64-5717-4562-b3fc-2c963f66afa3","workspace_transfer_status":"TRANSFER_COMPLETED","reason":"Failed to configure IDP.","created_by":"user@customer.com","created_at":"2021-04-23T10:20:30.400+02:30","updated_at":"2021-04-23T10:20:30.400+02:30"}

  - `items.provisions.service_provision.platform_customer_name` (string, required)
    Example: "Hewlett Packard Enterprise"

  - `items.provisions.service_provision.organization_id` (string, required)
    Example: "5ab85f64-6717-5562-c3fc-3c963f66afa6"

  - `items.provisions.service_provision.id` (string, required)
    Service provision identifier
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.provisions.service_provision.reason` (string, required)
    Example: "Failed to configure IDP."

  - `items.provisions.service_provision.created_by` (string, required)
    Example: "user@customer.com"

  - `items.provisions.service_provision.generation` (integer)
    Generated/updated version
    Example: 1

  - `items.provisions.service_provision.type` (string)
    Example: "/service-catalog/service-provision"

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


