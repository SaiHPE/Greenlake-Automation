---
title: "GET /service-catalog/v1beta1/my-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/v1beta1/service_registry_v1beta1_uiapi/ui-management/getmyservices.md"
scraped_at: "2026-06-07T06:16:46.240519+00:00Z"
---

# Get My Services

Get data to populate My Services

Endpoint: GET /service-catalog/v1beta1/my-services
Version: v1beta1
Security: bearerAuth

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of my services.
    Example: "us-west"

  - `limit` (integer)
    Number of entries per page

  - `include-omnipresent` (boolean)
    Specifies whether to include omnipresent service offers in response
    Example: true

## Response 200 fields (application/json):

  - `items` (array, required)
    Data pertaining to service and app provisions

  - `items.id` (string, required)
    Region with Detailed Provisions identifier
    Example: "us-east"

  - `items.type` (string, required)
    Resource Type
    Example: "/service-catalog/my-service"

  - `items.provisions` (array, required)

  - `items.provisions.serviceOffer` (object)
    Partial details for a service offer

  - `items.provisions.serviceOffer.id` (string, required)
    Identifier of service offer
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.provisions.serviceOffer.resourceUri` (string, required)
    Resource URI
    Example: "/service-catalog/v1beta1/service-offers/7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.provisions.serviceOffer.name` (string, required)
    Name of the Service Offer. In case of an app-provision, name of service-manager will be picked. If absent, name of app will be picked.
    Example: "Aruba Central"

  - `items.provisions.serviceOffer.categories` (array, required)
    Types of categories
    Enum: "COMPUTE", "NETWORKING", "STORAGE", "PRIVATE_CLOUD", "MGMT_GOV", "WORKLOADS", "AI_ML_ANALYTICS"

  - `items.provisions.serviceOffer.slug` (string, required)
    Short identifier for a service offer. In case of an app-provision, slug will be picked from service-manager. If absent, slug will be picked from application.
    Example: "CENTRAL"

  - `items.provisions.serviceOffer.staticLaunchUrl` (string, required)
    Relative URLs to launch
    Example: "https://${sub-domain}/infosight.hpe.com"

  - `items.provisions.serviceOffer.workspaceTypes` (array, required)
    Workspace Types supported
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.provisions.serviceOffer.workspaceOpModes` (array, required)
    Types of Workspace Operational Modes for Tenant Workspaces
    Enum: "CUSTOMER_OWNED_INVENTORY", "MSP_OWNED_INVENTORY", "ALL", "NONE"

  - `items.provisions.serviceManagerProvision` (object)
    Service manager provision details

  - `items.provisions.serviceManagerProvision.id` (string, required)
    Example: "2fa85f6457174562b3fc2c963f66afa1"

  - `items.provisions.serviceManagerProvision.resourceUri` (string, required)
    URI to the service manager provision resource
    Example: "/service-catalog/v1beta1/service-manager-provisions/2fa85f6457174562b3fc2c963f66afa1"

  - `items.provisions.serviceManagerProvision.serviceManager` (object, required)

  - `items.provisions.serviceManagerProvision.serviceManager.id` (string)
    Service Manager ID
    Example: "7267b0e0-013c-4181-8c27-01b395ed0b61"

  - `items.provisions.serviceManagerProvision.region` (string, required)
    Example: "us-east"

  - `items.provisions.serviceManagerProvision.provisionStatus` (string, required)
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `items.provisions.serviceManagerProvision.serviceManagerInstanceId` (string, required)
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.provisions.serviceManagerProvision.createdAt` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.provisions.serviceManagerProvision.updatedAt` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.provisions.serviceManagerProvision.generation` (integer, required)
    Monotonically increasing update counter.
    Example: 1

  - `items.provisions.serviceManagerProvision.workspaceTransferStatus` (string)
    Workspace transfer status
    Enum: "TRANSFER_INITIATED", "TRANSFER_COMPLETED", "TRANSFER_FAILED"

  - `items.provisions.serviceProvision` (object)

  - `items.provisions.serviceProvision.id` (string, required)
    Service provision identifier
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.provisions.serviceProvision.resourceUri` (string, required)
    Example: "/service-catalog/v1beta1/service-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.provisions.serviceProvision.serviceOffer` (object, required)

  - `items.provisions.serviceProvision.serviceOffer.id` (string)
    Service Offer ID
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.provisions.serviceProvision.workspace` (object, required)

  - `items.provisions.serviceProvision.workspace.id` (string)
    Workspace ID
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.provisions.serviceProvision.workspace.name` (string)
    Workspace Name
    Example: "Hewlett Packard Enterprise"

  - `items.provisions.serviceProvision.workspace.organizationId` (string)
    Example: "5ab85f64-6717-5562-c3fc-3c963f66afa6"

  - `items.provisions.serviceProvision.generation` (integer, required)
    Generated/updated version
    Example: 1

  - `items.provisions.serviceProvision.serviceManagerProvision` (object)

  - `items.provisions.serviceProvision.serviceManagerProvision.id` (string)
    Service Manager Provision ID
    Example: "2fb85f6457174562b3fc2c963f66afa2"

  - `items.provisions.serviceProvision.reason` (string)
    Example: "Failed to configure IDP."

  - `items.provisions.serviceProvision.createdBy` (string)
    Example: "user@company.com"

  - `next` (string, required)
    Example: "us-west"

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


