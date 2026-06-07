---
title: "GET /service-catalog/v1beta1/service-provisions/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-provision-nbapi-v1beta1/service_provision_v1beta1_nbapi/service-provision/getserviceprovision.md"
scraped_at: "2026-06-07T06:15:46.399499+00:00Z"
---

# Get service provision

Fetch service provision details for an ID.

Endpoint: GET /service-catalog/v1beta1/service-provisions/{id}
Version: v1beta1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    The unique identifier of a service provision. The ID is returned by the Get service provisions endpoint.

## Query parameters:

  - `unredacted` (boolean)
    If set to true, get the entire entry along with sensitive fields.
    Example: true

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique service provision identifier.
    Example: "2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `resourceUri` (string, required)
    The URI of the resource.
    Example: "/service-catalog/{version}/service-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa9"

  - `serviceOffer` (object, required)
    Information about the associated service offer.

  - `serviceOffer.id` (string)
    The unique identifier of a service offer.
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `serviceOffer.name` (string)
    The name of the service offer
    Example: "Aruba Central"

  - `region` (string, required)
    The HPE GreenLake-defined region code.
    Example: "us-west"

  - `workspace` (object, required)
    Information about the associated workspace. In HPE GreenLake, a workspace is a secure, dedicated environment for managing resources.

  - `workspace.id` (string)
    The workspace ID.
    Example: "4ab85f64-5717-4562-b3fc-2c963f66afa6"

  - `workspace.name` (string)
    The workspace name.
    Example: "Hewlett Packard Enterprise"

  - `workspace.organizationId` (string)
    The organization ID. Each HPE GreenLake Organization operates as a distinct tenant with its own identity directory and unique organization ID.
    Example: "5ab85f64-6717-5562-c3fc-3c963f66afa6"

  - `workspace.workspaceTransferStatus` (string)
    The status of a workspace transfer from one type to another.
    Enum: "TRANSFER_INITIATED", "TRANSFER_COMPLETED", "TRANSFER_FAILED"

  - `workspace.mspId` (string)
    The unique identifier of an MSP tenant account.
    Example: "3ca24f18-5013-4562-b3fc-2d992f22ade2"

  - `retryCount` (integer, required)
    The number of times the operation has been retried.

  - `type` (string, required)
    The type of the resource.
    Example: "/service-catalog/service-provision"

  - `createdAt` (string, required)
    Date and time at which the service offer was created.
    Example: "2021-04-23T10:20:30.400+02:30"

  - `updatedAt` (string, required)
    Date and time at which the service offer was updated.
    Example: "2021-04-29T10:20:30.400+02:30"

  - `generation` (integer, required)
    A monotonically increasing update counter.
    Example: 1

  - `serviceManager` (object)
    Information about the associated service manager, including its ID and resource URI.

  - `serviceManager.id` (string)
    The unique identifier for the service manager.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `serviceManagerProvision` (object)
    Details of the provisioned service manager, including its ID, resource URI, account type, operational mode, provision status, and MSP conversion status.

  - `serviceManagerProvision.id` (string)
    The unique identifier for the provisioned service manager.
    Example: "2fb85f64-5717-4562-b3fc-2c963f66afa2"

  - `serviceManagerProvision.accountType` (string)
    The type of workspace associated with the account.
    Enum: "BASIC_ORGANIZATION", "STANDALONE", "MSP", "TENANT"

  - `serviceManagerProvision.operationalMode` (string)
    Indicates where the service offer can be viewed or provisioned.
    Enum: "DEFAULT", "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

  - `serviceManagerProvision.provisionStatus` (string)
    The current status of provisioning.
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `serviceManagerProvision.mspConversionStatus` (string)
    The current status of MSP conversion. Indicates whether a workspace has been converted to MSP.
    Enum: "MSP_CONVERSION_INITIATED", "MSP_CONVERTED", "MSP_CONVERSION_FAILED"

  - `serviceManagerProvision.reason` (string)
    Reason for failure in provisioning
    Example: "Failed to configure IDP."

  - `serviceManagerInstanceId` (any)
    The unique identifier of a service manager instance. This is the application instance ID of an application related to a service offer.
    Example: "2fc85f64-5717-4562-b3fc-2c963f66afa3"

  - `provisionStatus` (string)
    The provisioning status of the service in the workspace.
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `reason` (string)
    The reason the service provision creation failed.
    Example: "Failed to configure IDP."

  - `createdBy` (string)
    The email address of the user who created the service provision.
    Example: "user@company.com"

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
    A unique identifier for the instance of this error. Maybe same as trace ID.
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
    A unique identifier for the instance of this error. Maybe same as trace ID.
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
    A unique identifier for the instance of this error. Maybe same as trace ID.
    Example: "64136af7-cd64-4b4e-88a8-150ab51a920d"

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
    A unique identifier for the instance of this error. Maybe same as trace ID.
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
    A unique identifier for the instance of this error. Maybe same as trace ID.
    Example: "e0a0d57d-30cb-45f8-90cb-d6ea3501f70b"

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.type` (string, required)
    The type of error details.
    Example: "hpe.greenlake.retry_info"

  - `errorDetails.retryAfterSeconds` (integer, required)
    Seconds to wait before retrying.
    Example: 30


