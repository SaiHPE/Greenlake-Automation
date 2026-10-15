---
title: "GET /service-catalog/v1beta1/featured-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getfeaturedservices.md"
scraped_at: "2026-06-07T06:16:45.776905+00:00Z"
---

# Get Featured Service Offers

Get Featured Service Offers

Endpoint: GET /service-catalog/v1beta1/featured-services
Version: v1beta1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the category for the next page of featured services.
    Example: "STORAGE"

  - `limit` (integer)
    Number of entries per page

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    An enumeration.
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.type` (string, required)
    Type of resource
    Example: "/service-catalog/featured-service"

  - `items.servicesWithRegions` (array)

  - `items.servicesWithRegions.serviceOffer` (object, required)

  - `items.servicesWithRegions.serviceOffer.id` (string, required)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.servicesWithRegions.serviceOffer.resourceUri` (string, required)
    Example: "/service-catalog/v1beta1/service-offers/3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.servicesWithRegions.serviceOffer.capabilities` (array, required)
    List of capabilities
    Example: ["Capability 1","Capability 2"]

  - `items.servicesWithRegions.serviceOffer.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.servicesWithRegions.serviceOffer.serviceManager` (object, required)

  - `items.servicesWithRegions.serviceOffer.serviceManager.id` (string)
    Service Manager ID
    Example: "7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.servicesWithRegions.serviceOffer.serviceManager.resourceUri` (string)
    Resource URI
    Example: "/service-catalog/v1beta1/service-managers/7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.servicesWithRegions.serviceOffer.languagesSupported` (array, required)
    Codenames for supported languages
    Example: ["en-US","de-DE"]

  - `items.servicesWithRegions.serviceOffer.type` (string, required)
    Resource Type
    Example: "/service-catalog/service-offer"

  - `items.servicesWithRegions.serviceOffer.name` (string)
    Name of the service offer
    Example: "Aruba Central"

  - `items.servicesWithRegions.serviceOffer.slug` (string)
    Short identifier of an service offer
    Example: "AC"

  - `items.servicesWithRegions.serviceOffer.overview` (string)
    Overview of the service offer
    Example: "Aruba Central overview"

  - `items.servicesWithRegions.serviceOffer.serviceOfferType` (string)
    Service Offer Type
    Enum: "FREE", "COMMON_TOOLS", "SAAS", "DEVICE_SAAS", "IAAS", "ORGANIZATION"

  - `items.servicesWithRegions.serviceOffer.isDefault` (boolean)
    Boolean to define a service offer is service manager
    Example: true

  - `items.servicesWithRegions.serviceOffer.featuresSupported` (array)
    Enum: "DEEP_LINKING", "EVALUATION", "SERVICE_PROVISIONING", "ORG_SINGLETON_SERVICE_PROVISIONING", "SKIP_SERVICE_MGR_PROVISIONING", "SKIP_SERVICE_UNPROVISIONING", "RBAC", "HONOR_UNPROVISION_RESPONSE"

  - `items.servicesWithRegions.serviceOffer.documentationUrl` (string)
    HTTPS URL for documentation
    Example: "https://www.arubanetworks.com/techdocs/central/latest/content/home.htm"

  - `items.servicesWithRegions.serviceOffer.termsOfServiceUrl` (string)
    HTTPS URL for terms of service
    Example: "https://www.hpe.com/us/en/about/legal/ccs-terms.html#Storage"

  - `items.servicesWithRegions.serviceOffer.testDriveUrl` (string)
    HTTPS URL for test drive
    Example: "https://testdrive.greenlake.hpe.com"

  - `items.servicesWithRegions.serviceOffer.contactSalesUrl` (string)
    HTTPS URL for contacting sales team
    Example: "https://contact-sales.hpe.com/"

  - `items.servicesWithRegions.serviceOffer.status` (string)
    Status of a service offer
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED"

  - `items.servicesWithRegions.serviceOffer.createdAt` (string)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.servicesWithRegions.serviceOffer.updatedAt` (string)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.servicesWithRegions.serviceOffer.generation` (integer)
    Generated/updated version
    Example: 1

  - `items.servicesWithRegions.serviceOffer.shortDescription` (string)
    short-descriptive line displayed on the service-offer title
    Example: "description"

  - `items.servicesWithRegions.serviceOffer.staticLaunchUrl` (string)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `items.servicesWithRegions.serviceOffer.evalUrl` (string)
    URL to sign-up for evaluation of the service-offer for a limited time-period
    Example: "https://connect.hpe.com/HPE_Backup_and_Recovery_Trial"

  - `items.servicesWithRegions.serviceOffer.brokerUri` (string)
    Applicable only to internal service-offers. Relative path starting with api-group. API-group suffices. Base-URI will be the api-gateway for the GLP cluster.
    Example: "/igc"

  - `items.servicesWithRegions.serviceOffer.preProvisionMessage` (string)
    Short warning/message displayed in the service-provision dialog box
    Example: "Users will be logged out during provisioning."

  - `items.servicesWithRegions.serviceOffer.workspaceTypes` (array)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.servicesWithRegions.serviceOffer.workspaceOpModes` (array)
    Enum: "CUSTOMER_OWNED_INVENTORY", "MSP_OWNED_INVENTORY", "ALL", "NONE"

  - `items.servicesWithRegions.availableRegions` (array, required)
    Names of the regions where the Service Offer is available for the logged in user/customer.

  - `items.servicesWithRegions.availableRegions.id` (string)
    Code-name for a geo-region supported by GLP
    Example: "us-east"

  - `items.servicesWithRegions.availableRegions.name` (string)
    Human readable name for the geo-region supported by GLP
    Example: "US East"

  - `items.servicesWithRegions.id` (string)
    Service Offer With Regions ID
    Example: 1

  - `next` (string, required)
    Example: "STORAGE"

  - `count` (integer, required)
    Count Per Page

  - `total` (integer, required)
    Total Count

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

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_SERVICE_CATALOG_FORBIDDEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "The user is not authorized to perform the request"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
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
    Status of access token.
    Example: "Failed"

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


