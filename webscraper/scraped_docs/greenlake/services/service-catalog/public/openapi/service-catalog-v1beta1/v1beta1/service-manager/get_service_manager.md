---
title: "GET /service-catalog/v1beta1/service-managers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager/get_service_manager.md"
scraped_at: "2026-06-07T06:15:40.938680+00:00Z"
---

# Get a specific service manager (deprecated)

Retrieve details for a specific service manager by passing the service manager ID.

Endpoint: GET /service-catalog/v1beta1/service-managers/{id}
Version: v1beta1
Security: bearerAuth

## Path parameters:

  - `id` (string, required)
    Service manager ID

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique ID of the service manager.

  - `resourceUri` (string, required)
    URI to the service manager resource

  - `name` (string, required)
    Name of the service manager

  - `standaloneSupported` (boolean, required)
    Service manager supports Standalone or not

  - `mspSupported` (boolean, required)
    Service manager supports Managed Service Provider (MSP) or not

  - `honorUnprovisionResponse` (boolean, required)
    Honor Unprovision or not

  - `tenantOnlySupported` (boolean, required)
    Service manager supports Tenant only Supported or not

  - `createdAt` (string, required)
    Date and time the service was created.

  - `updatedAt` (string, required)
    Date and time the service manager metadata was updated.

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `type` (string, required)
    Type of resource

  - `mspOnlySupported` (boolean)
    Service Manager supports only Managed Service Provider (MSP) or not

  - `workspaceTransferSupported` (boolean)
    Service Manager supports Workspace Transfer or not

  - `workspaceOpModesSupported` (string)
    Types of tenants supported by the service manager

  - `description` (string)
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


