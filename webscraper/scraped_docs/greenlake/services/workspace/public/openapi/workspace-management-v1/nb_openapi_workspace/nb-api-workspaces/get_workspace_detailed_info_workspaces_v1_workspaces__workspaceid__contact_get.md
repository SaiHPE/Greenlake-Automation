---
title: "GET /workspaces/v1/workspaces/{workspaceId}/contact"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/get_workspace_detailed_info_workspaces_v1_workspaces__workspaceid__contact_get.md"
scraped_at: "2026-06-07T06:16:36.277360+00:00Z"
---

# Get detailed workspace information

Retrieve detailed workspace information.

Endpoint: GET /workspaces/v1/workspaces/{workspaceId}/contact
Version: 1.0.0
Security: BearerAuth

## Path parameters:

  - `workspaceId` (string, required)
    The unique identifier of the workspace.
    Example: "7600415a-8876-5722-9f3c-b0fd11112283"

## Response 200 fields (application/json):

  - `address` (object)
    Company address.

  - `address.streetAddress` (string)
    Street address

  - `address.streetAddressComplement` (string)
    Apt or suite or building

  - `address.city` (string)

  - `address.stateOrRegion` (string)
    State or region

  - `address.zip` (string)

  - `address.countryCode` (string)
    Country code

  - `phoneNumber` (string)
    The phone number associated with this workspace.

  - `email` (string)
    The primary email address associated with the workspace.

  - `resourceUri` (string)
    Full path of the resource

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

## Response 404 fields (application/json):

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


