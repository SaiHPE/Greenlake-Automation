---
title: "POST /service-catalog/v1beta1/service-provisions/{id}/retry-workspace-transfer"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1/service-provisions/retryworkspacetransfer.md"
scraped_at: "2026-06-07T06:15:43.896183+00:00Z"
---

# Retry Workspace Transfer

Retry the workspace transfer for a given service provision ID

Endpoint: POST /service-catalog/v1beta1/service-provisions/{id}/retry-workspace-transfer
Version: v1beta1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    Service provision ID

## Response 202 fields (application/json):

  - `id` (string, required)
    Service provision identifier
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `resourceUri` (string, required)
    Example: "/service-catalog/{version}/service-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `serviceOffer` (object, required)

  - `serviceOffer.id` (string)
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `serviceOffer.name` (string)
    Name of the service offer
    Example: "Aruba Central"

  - `serviceOffer.resourceUri` (string)
    Resource URI
    Example: "/service-catalog/v1alpha1/service-offers/4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `region` (string, required)
    Example: "us-west"

  - `workspace` (object, required)

  - `workspace.name` (string)
    Workspace Name
    Example: "Hewlett Packard Enterprise"

  - `workspace.organizationId` (string)
    Example: "5ab85f64-6717-5562-c3fc-3c963f66afa6"

  - `workspace.workspaceTransferStatus` (string)
    Enum: "TRANSFER_INITIATED", "TRANSFER_COMPLETED", "TRANSFER_FAILED"

  - `workspace.mspId` (string)
    Identifier of Tenant Account's MspID
    Example: "3ca24f18-5013-4562-b3fc-2d992f22ade2"

  - `retryCount` (integer, required)

  - `type` (string, required)
    Example: "/service-catalog/service-provision"

  - `createdAt` (string, required)
    Date and time at which the service offer was created or upgraded.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `updatedAt` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `generation` (integer, required)
    Generated/updated version
    Example: 1

  - `serviceManager` (object)

  - `serviceManagerProvision` (object)

  - `serviceManagerProvision.accountType` (string)
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `serviceManagerProvision.operationalMode` (string)
    Enum: "DEFAULT", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `serviceManagerProvision.provisionStatus` (string)
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `serviceManagerProvision.mspConversionStatus` (string)
    Enum: "MSP_CONVERSION_INITIATED", "MSP_CONVERTED", "MSP_CONVERSION_FAILED"

  - `serviceManagerProvision.reason` (string)
    Example: "Failed to configure IDP."

  - `serviceManagerInstanceId` (string)
    Example: "2fc85f64-5717-4562-b3fc-2c963f66afa3"

  - `createdBy` (string)
    Example: "user@company.com"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_BAD_REQUEST"

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

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 404

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_NOT_FOUND"

  - `message` (string, required)
    A user-friendly error message
    Example: "No service provision found for ID: 64136af7-cd64-4b4e-88a8-150ab51a920d"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

## Response 412 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code
    Example: 412

  - `errorCode` (string, required)
    A unique machine-friendly identifier for the error from a global list of enumerated identifier strings
    Example: "HPE_GL_ERROR_PRECONDITION_FAILED"

  - `message` (string, required)
    A user-friendly error message
    Example: "Server preconditions; missing request headers"

  - `debugId` (string, required)
    A unique identifier for the instance of this error. Maybe same as trace Id
    Example: "64136af7-cd64-4b4e-88a8-150ab51a969d"

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


