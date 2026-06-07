---
title: "GET /workspaces/v1/workspaces/{workspaceId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/identity-v1/nb_openapi_workspace/nb-api-workspaces/get_workspace_workspaces_v1_workspaces__workspaceid__get.md"
scraped_at: "2026-06-07T06:15:28.160991+00:00Z"
---

# Get workspace information

Retrieve basic workspace information for a provided workspace identifier.

Endpoint: GET /workspaces/v1/workspaces/{workspaceId}
Version: 1.0.0
Security: BearerAuth

## Path parameters:

  - `workspaceId` (string, required)
    The unique identifier of the workspace.
    Example: "7600415a-8876-5722-9f3c-b0fd11112283"

## Response 200 fields (application/json):

  - `id` (string, required)
    Resource unique identification

  - `type` (string, required)
    Type of data

  - `workspaceName` (string, required)
    Company name of the workspace.

  - `generation` (integer)
    Resource history of updates

  - `createdAt` (string)
    The time the resource was created.

  - `updatedAt` (string)
    The time the resource was last updated.

  - `workspaceType` (string)
    Type of the workspace.
    Enum: "STANDARD_ENTERPRISE", "MSP", "MSP_TENANT"

  - `createdBy` (string)
    Email address of the user that created the account.

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


