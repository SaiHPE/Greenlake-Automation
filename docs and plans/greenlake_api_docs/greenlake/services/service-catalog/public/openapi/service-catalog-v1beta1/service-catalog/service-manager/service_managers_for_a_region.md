---
title: "GET /service-catalog/v1beta1/per-region-service-managers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/service-catalog/service-manager/service_managers_for_a_region.md"
scraped_at: "2026-06-07T06:15:42.392804+00:00Z"
---

# Get service managers deployed in a specific region. (deprecated)

Retrieve a list of service managers deployed to a particular region.

Endpoint: GET /service-catalog/v1beta1/per-region-service-managers/{id}
Version: v1beta1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    HPE GreenLake platform defined region code.

## Response 200 fields (application/json):

  - `id` (string, required)
    HPE GreenLake platform defined region where the service manager is available.

  - `regionName` (string, required)
    The name of geographical region where the service manager is available.

  - `serviceManagers` (array, required)

  - `serviceManagers.id` (string, required)
    The unique ID of the service manager.

  - `serviceManagers.resourceUri` (string, required)
    URI to the service manager resource

  - `serviceManagers.name` (string, required)
    Name of the service manager

  - `serviceManagers.standaloneSupported` (boolean, required)
    Service manager supports Standalone or not

  - `serviceManagers.mspSupported` (boolean, required)
    Service manager supports Managed Service Provider (MSP) or not

  - `serviceManagers.honorUnprovisionResponse` (boolean, required)
    Honor Unprovision or not

  - `serviceManagers.tenantOnlySupported` (boolean, required)
    Service manager supports Tenant only Supported or not

  - `serviceManagers.createdAt` (string, required)
    Date and time the service was created.

  - `serviceManagers.updatedAt` (string, required)
    Date and time the service manager metadata was updated.

  - `serviceManagers.generation` (integer, required)
    Monotonically increasing update counter.

  - `serviceManagers.type` (string, required)
    Type of resource

  - `serviceManagers.mspOnlySupported` (boolean)
    Service Manager supports only Managed Service Provider (MSP) or not

  - `serviceManagers.workspaceTransferSupported` (boolean)
    Service Manager supports Workspace Transfer or not

  - `serviceManagers.workspaceOpModesSupported` (string)
    Types of tenants supported by the service manager

  - `serviceManagers.description` (string)
    Description of the service manager.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.

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


