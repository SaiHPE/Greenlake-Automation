---
title: "GET /service-catalog/v1/per-region-service-managers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1/service-manager/per_region_service_managers_v1.md"
scraped_at: "2026-06-07T06:15:40.186795+00:00Z"
---

# Get service managers by region

Retrieve a list of available service managers categorized by region.

Endpoint: GET /service-catalog/v1/per-region-service-managers
Version: v1
Security: bearerAuth

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from.

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint and return only the subset of resources that match the filter using an OData V4 formatted filter string. Service manager by region can be filtered by mspsupported See examples of filtering options.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    HPE GreenLake platform defined region where the service manager is available.

  - `items.regionName` (string, required)
    The name of geographical region where the service manager is available.

  - `items.serviceManagers` (array, required)

  - `items.serviceManagers.id` (string, required)
    The unique ID of the service manager.

  - `items.serviceManagers.resourceUri` (string, required)
    URI to the service manager resource

  - `items.serviceManagers.name` (string, required)
    Name of the service manager

  - `items.serviceManagers.standaloneSupported` (boolean, required)
    Service manager supports Standalone or not

  - `items.serviceManagers.mspSupported` (boolean, required)
    Service manager supports Managed Service Provider (MSP) or not

  - `items.serviceManagers.honorUnprovisionResponse` (boolean, required)
    Honor Unprovision or not

  - `items.serviceManagers.tenantOnlySupported` (boolean, required)
    Service manager supports Tenant only Supported or not

  - `items.serviceManagers.createdAt` (string, required)
    Date and time the service was created.

  - `items.serviceManagers.updatedAt` (string, required)
    Date and time the service manager metadata was updated.

  - `items.serviceManagers.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.serviceManagers.type` (string, required)
    Type of resource

  - `items.serviceManagers.mspOnlySupported` (boolean)
    Service Manager supports only Managed Service Provider (MSP) or not

  - `items.serviceManagers.workspaceTransferSupported` (boolean)
    Service Manager supports Workspace Transfer or not

  - `items.serviceManagers.workspaceOpModesSupported` (string)
    Types of tenants supported by the service manager

  - `items.serviceManagers.description` (string)
    Description of the service manager.

  - `count` (integer, required)
    Number of items returned

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer)
    Total number of items  that match the filter query, if one was provided in the request

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

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error.

  - `message` (string, required)
    A user-friendly error message.

  - `debugId` (string, required)
    A unique identifier for the instance of this error.


