---
title: "GET /service-catalog/v1beta1/service-offers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_v1beta1_nbapi/service-offers/getserviceoffer.md"
scraped_at: "2026-06-07T06:15:50.481355+00:00Z"
---

# Get a service offer

Retrieve detailed information about a specific service offer by supplying its unique identifier in the request path.
To obtain valid service offer IDs, use the Get service offers endpoint to list available offers.

Endpoint: GET /service-catalog/v1beta1/service-offers/{id}
Version: v1beta1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    The unique identifier of the service offer.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique identifier for the service offer.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `resourceUri` (string, required)
    The URI reference to this resource.
    Example: "/service-catalog/v1beta1/service-offers/3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `name` (string, required)
    The name of the service offer.
    Example: "Aruba Central"

  - `slug` (string, required)
    A short identifier for the service offer.
    Example: "AC"

  - `overview` (string, required)
    A brief overview of the service offer.
    Example: "Aruba Central overview"

  - `capabilities` (array, required)
    A list of key features or functionalities provided by the service offer.
    Example: ["Capability 1","Capability 2"]

  - `categories` (array, required)
    The categories to which the service offer belongs.
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `serviceOfferType` (string, required)
    The type of service offer.
    Enum: "FREE", "COMMON_TOOLS", "SAAS", "DEVICE_SAAS", "IAAS", "ORGANIZATION"

  - `serviceManager` (object, required)
    The associated service manager application for this service offer, including its ID and resource URI.

  - `serviceManager.id` (string)
    The unique identifier for the service manager.
    Example: "7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `serviceManager.resourceUri` (string)
    The URI reference to the service manager resource.
    Example: "/service-catalog/v1beta1/service-managers/7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `featuresSupported` (array, required)
    The features supported by this service offer, such as deep linking or RBAC.
    Enum: "DEEP_LINKING", "EVALUATION", "SERVICE_PROVISIONING", "ORG_SINGLETON_SERVICE_PROVISIONING", "SKIP_SERVICE_MGR_PROVISIONING", "SKIP_SERVICE_UNPROVISIONING", "RBAC", "UI_DISABLE_PROVISIONING", "HONOR_UNPROVISION_RESPONSE", "ORG_PARENT_SUPPORTED"

  - `languagesSupported` (array, required)
    The ISO codes for languages supported by this service offer.
    Example: ["en-US","de-DE"]

  - `documentationUrl` (string, required)
    An HTTPS URL to the documentation.
    Example: "https://www.arubanetworks.com/techdocs/central/latest/content/home.htm"

  - `termsOfServiceUrl` (string, required)
    An HTTPS URL to the terms of service.
    Example: "https://www.hpe.com/us/en/about/legal/ccs-terms.html#Storage"

  - `testDriveUrl` (string, required)
    An HTTPS URL to test drive.
    Example: "https://testdrive.greenlake.hpe.com"

  - `contactSalesUrl` (string, required)
    The HTTPS URL for contacting the sales team.
    Example: "https://contact-sales.hpe.com/"

  - `status` (string, required)
    The current status of the service offer.
    Enum: "ONBOARDING", "ONBOARDED", "PUBLISHED"

  - `createdAt` (string, required)
    Date and time at which the service offer was created.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `shortDescription` (string, required)
    A short description or tagline for the service offer.
    Example: "description"

  - `staticLaunchUrl` (string, required)
    The relative URL used to launch the service offer.
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `evalUrl` (string, required)
    The URL to sign up for a time-limited evaluation or trial of the service offer.
    Example: "https://connect.hpe.com/HPE_Backup_and_Recovery_Trial"

  - `brokerUri` (string, required)
    HPE Internal. Applies only to internal service offers. It is the relative path starting with API group (the API group is sufficient). The base URI is the API gateway for the HPE GreenLake cloud cluster. This is the application API endpoint exposed by application to be called from HPE GreenLake cloud.
    Example: "/igc"

  - `preProvisionMessage` (string, required)
    A message displayed to users before provisioning the service offer, such as warnings or important information.
    Example: "Users will be logged out during provisioning."

  - `isDefault` (boolean)
    Indicates whether this service offer is the default for its service manager.
    Example: true

  - `updatedAt` (string)
    Date and time at which the service offer was last updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `generation` (integer)
    A monotonically increasing update counter.
    Example: 1

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

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 404

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error.
    Example: "HPE_GL_SERVICE_CATALOG_NOT_FOUND"

  - `message` (string, required)
    A user-friendly error message.
    Example: "No service provision found for ID: 64136af7-cd64-4b4e-88a8-150ab51a920d"

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
    Example: "hpe.greenlake.service-catalog"

  - `errorDetails.metadata` (object, required)
    Any additional key value pairs that the service defines.

  - `errorDetails.metadata.requestedItem` (string)
    Status of the access token.
    Example: "Not Found"

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


