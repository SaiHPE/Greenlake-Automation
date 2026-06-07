---
title: "GET /service-catalog/v1beta1/service-manager-provisions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1beta1/service-manager-provision/get_service_manager_provisions.md"
scraped_at: "2026-06-07T06:15:41.008081+00:00Z"
---

# Get service manager provisions (deprecated)

Retrieve a list of all service manager provision entries.

Endpoint: GET /service-catalog/v1beta1/service-manager-provisions
Version: v1beta1
Security: bearerAuth

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from.

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)

  - `items.resourceUri` (string, required)
    URI to the service manager provision resource

  - `items.serviceManager` (object, required)
    A reference to a service manager resource.

  - `items.serviceManager.resourceUri` (string)
    URI to the service manager resource

  - `items.region` (string, required)

  - `items.provisionStatus` (string, required)
    The current provisioning status.
    Enum: "PROVISION_INITIATED", "PROVISIONED", "PROVISION_FAILED", "UNPROVISION_INITIATED", "UNPROVISIONED", "UNPROVISION_FAILED"

  - `items.createdBy` (string, required)
    The HPE GreenLake platform username that provisioned the service manager.

  - `items.createdAt` (string, required)
    Date and time the service offer was created or upgraded.

  - `items.updatedAt` (string, required)
    Date and time the service offer was updated.

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.type` (string, required)
    Type of resource

  - `count` (integer, required)
    Number of items returned

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer)
    Total count of items in the collection after applying the provided query parameters.

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


