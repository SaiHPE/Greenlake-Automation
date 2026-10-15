---
title: "DELETE /workspaces/v1/credentials/{credentialId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/delete_credentials_workspaces_v1_msp_tenants__tenantid__credentials__credentialid__delete.md"
scraped_at: "2026-06-07T06:15:15.738538+00:00Z"
---

# Delete a credential

Delete a credential for a user in a standard enterprise, managed service provider (MSP), or MSP tenant workspace.

Endpoint: DELETE /workspaces/v1/credentials/{credentialId}
Version: 1.0.0
Security: BearerAuth

## Path parameters:

  - `credentialId` (string, required)
    The unique ID of the credential
    Example: "7600415a-8876-5722-9f3c-b0fd11112283"

## Response 400 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.

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

## Response 500 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for this error used to help with troubleshooting.

  - `httpStatusCode` (integer, required)
    HTTP status code

  - `errorCode` (string, required)
    HPE GreenLake standard error code

  - `message` (string, required)
    A user-friendly error message.


## Response 204 fields
