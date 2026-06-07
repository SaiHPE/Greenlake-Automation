---
title: "GET /service-catalog/v1beta1/service-provisions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_internal_api/service-provisions/getserviceprovisions.md"
scraped_at: "2026-06-07T06:15:43.943939+00:00Z"
---

# Get Service Provisions

Get Service Provision list by filters applied

Endpoint: GET /service-catalog/v1beta1/service-provisions
Version: v1beta1

## Header parameters:

  - `Hpe-workspace-id` (string)
    Hpe worksapce id

## Query parameters:

  - `next` (string)
    Specifies the start-id for the next page of service offers.

  - `limit` (integer)
    Number of entries per page

  - `filter` (string)
    Supports Odata format.  Supported Fields: id, ServiceOfferId, workspaceId, serviceManagerProvisionId, serviceManagerId, serviceManagerInstanceId, status, organizationId, slug.  Supported operand: _eq_  Supported operations: _and_

  - `unredacted` (boolean)
    Get entire entry along with sensitive fields corresponding to user workspace
    Example: true

  - `all` (boolean)
    Get unredacted entries for all workspaces
    Example: true

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Service provision identifier
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.resourceUri` (string, required)
    Example: "/service-catalog/{version}/service-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `items.serviceOffer` (object, required)

  - `items.serviceOffer.id` (string)
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.serviceOffer.name` (string)
    Name of the service offer
    Example: "Aruba Central"

  - `items.serviceOffer.resourceUri` (string)
    Resource URI
    Example: "/service-catalog/v1alpha1/service-offers/4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `items.region` (string, required)
    Example: "us-west"

  - `items.workspace` (object, required)

  - `items.workspace.name` (string)
    Workspace Name
    Example: "Hewlett Packard Enterprise"

  - `items.workspace.organizationId` (string)
    Example: "5ab85f64-6717-5562-c3fc-3c963f66afa6"

  - `items.workspace.workspaceTransferStatus` (string)
    Enum: "TRANSFER_INITIATED", "TRANSFER_COMPLETED", "TRANSFER_FAILED"

  - `items.workspace.mspId` (string)
    Identifier of Tenant Account's MspID
    Example: "3ca24f18-5013-4562-b3fc-2d992f22ade2"

  - `items.retryCount` (integer, required)

  - `items.type` (string, required)
    Example: "/service-catalog/service-provision"

  - `items.createdAt` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `items.updatedAt` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `items.generation` (integer, required)
    Generated/updated version
    Example: 1

  - `items.serviceManager` (object)

  - `items.serviceManagerProvision` (object)

  - `items.serviceManagerProvision.accountType` (string)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `items.serviceManagerProvision.operationalMode` (string)
    Enum: "DEFAULT", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `items.serviceManagerProvision.provisionStatus` (string)
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `items.serviceManagerProvision.mspConversionStatus` (string)
    Enum: "MSP_CONVERSION_INITIATED", "MSP_CONVERTED", "MSP_CONVERSION_FAILED"

  - `items.serviceManagerProvision.reason` (string)
    Example: "Failed to configure IDP."

  - `items.serviceManagerInstanceId` (string)
    Example: "2fc85f64-5717-4562-b3fc-2c963f66afa3"

  - `items.createdBy` (string)
    Example: "user@company.com"

  - `count` (integer, required)

  - `next` (string, required)
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `total` (integer, required)

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_UNAUTHORIZED"

  - `message` (string, required)
    A user-friendly error message
    Example: "Authentication error - token expired"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_FORBIDDEN"

  - `message` (string, required)
    A user-friendly error message
    Example: "UI Authorization Failed for current Route"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "8567e466-7322-414a-b7d4-6832c3ce8f47"

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 422

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_UNPROCESSABLE_ENTITY"

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid UUID: 5221850a-dae8-4bdf-ae69-021e3bbf80a"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    A user-friendly error message
    Example: "Internal Server Error"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "e0a0d57d-30cb-45f8-90cb-d6ea3501f70b"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


