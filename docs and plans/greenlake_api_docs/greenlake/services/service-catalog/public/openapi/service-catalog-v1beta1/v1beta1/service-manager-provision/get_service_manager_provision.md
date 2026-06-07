---
title: "GET /service-catalog/v1beta1/service-manager-provisions/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager-provision/get_service_manager_provision.md"
scraped_at: "2026-06-07T06:15:41.284025+00:00Z"
---

# Get a specific service manager provision entry (deprecated)

Retrieve details for a specific service manager provision entry using the ID for the entry.

Endpoint: GET /service-catalog/v1beta1/service-manager-provisions/{id}
Version: v1beta1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    Service manager provision ID

## Response 200 fields (application/json):

  - `id` (string, required)

  - `resourceUri` (string, required)
    URI to the service manager provision resource

  - `serviceManager` (object, required)
    A reference to a service manager resource.

  - `serviceManager.resourceUri` (string)
    URI to the service manager resource

  - `region` (string, required)

  - `provisionStatus` (string, required)
    The current provisioning status.
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `createdBy` (string, required)
    The HPE GreenLake platform username that provisioned the service manager.

  - `createdAt` (string, required)
    Date and time the service offer was created or upgraded.

  - `updatedAt` (string, required)
    Date and time the service offer was updated.

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `type` (string, required)
    Type of resource

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.


