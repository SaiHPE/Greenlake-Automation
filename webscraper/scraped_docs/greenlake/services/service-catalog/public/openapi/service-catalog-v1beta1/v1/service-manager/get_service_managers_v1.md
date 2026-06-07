---
title: "GET /service-catalog/v1/service-managers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1/service-manager/get_service_managers_v1.md"
scraped_at: "2026-06-07T06:15:40.037244+00:00Z"
---

# Get service managers

Get a list of available service managers.

Endpoint: GET /service-catalog/v1/service-managers
Version: v1
Security: bearerAuth

## Query parameters:

  - `offset` (integer)
    Specify pagination offset

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique ID of the service manager.

  - `items.resourceUri` (string, required)
    URI to the service manager resource

  - `items.name` (string, required)
    Name of the service manager

  - `items.standaloneSupported` (boolean, required)
    Service manager supports Standalone or not

  - `items.mspSupported` (boolean, required)
    Service manager supports Managed Service Provider (MSP) or not

  - `items.honorUnprovisionResponse` (boolean, required)
    Honor Unprovision or not

  - `items.tenantOnlySupported` (boolean, required)
    Service manager supports Tenant only Supported or not

  - `items.createdAt` (string, required)
    Date and time the service was created.

  - `items.updatedAt` (string, required)
    Date and time the service manager metadata was updated.

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.type` (string, required)
    Type of resource

  - `items.mspOnlySupported` (boolean)
    Service Manager supports only Managed Service Provider (MSP) or not

  - `items.workspaceTransferSupported` (boolean)
    Service Manager supports Workspace Transfer or not

  - `items.workspaceOpModesSupported` (string)
    Types of tenants supported by the service manager

  - `items.description` (string)
    Description of the service manager.

  - `count` (integer, required)
    Number of items returned

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer)
    Total count of items in the collection after applying the provided query parameters.

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


