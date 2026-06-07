---
title: "GET /workspaces/v1/msp-tenants"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb-api-workspaces/get_tenants_workspaces_v1_msp_tenants_get.md"
scraped_at: "2026-06-07T06:16:36.763108+00:00Z"
---

# Get list of MSP Tenants

Retrieve a list of managed service provider (MSP) tenants.

Endpoint: GET /workspaces/v1/msp-tenants
Version: 1.0.0
Security: BearerAuth

## Query parameters:

  - `filter` (string)
    Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter.

Get list of MSP Tenants API can be filtered by:
- id
- createdAt
- updatedAt
- workspaceName
- createdBy
- inventoryOwnership

  - `offset` (integer)
    Specify pagination offset. An offset argument defines how many pages to skip before returning results.

  - `limit` (integer)
    Specify the maximum number of entries per page. NOTE: The maximum value accepted is 300.

## Response 200 fields (application/json):

  - `offset` (integer, required)
    Specifies the offset of the returned page

  - `count` (integer, required)
    The number of returned items

  - `total` (integer, required)
    The total number of items in the result set

  - `items` (array, required)
    List of Workspaces

  - `items.id` (string, required)
    Resource unique identification

  - `items.type` (string, required)
    Type of data

  - `items.workspaceName` (string, required)
    Company name of the workspace.

  - `items.generation` (integer)
    Resource history of updates

  - `items.createdAt` (string)
    The time the resource was created.

  - `items.updatedAt` (string)
    The time the resource was last updated.

  - `items.createdBy` (string)
    Email address of the user that created the account.

  - `items.resourceUri` (string)
    Full path of the resource

  - `items.inventoryOwnership` (string)
    Devices and Subscriptions Ownership for this tenant.
    Enum: "MSP_OWNED_INVENTORY", "CUSTOMER_OWNED_INVENTORY"

## Response 401 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 403 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 412 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 422 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

## Response 500 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.


