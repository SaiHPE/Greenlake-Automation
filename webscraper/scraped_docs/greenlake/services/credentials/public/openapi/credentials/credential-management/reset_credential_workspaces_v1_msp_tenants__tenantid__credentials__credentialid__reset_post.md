---
title: "POST /workspaces/v1/credentials/{credentialId}/reset"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/reset_credential_workspaces_v1_msp_tenants__tenantid__credentials__credentialid__reset_post.md"
scraped_at: "2026-06-07T06:15:15.780678+00:00Z"
---

# Reset a credential

Reset the client secret for a credential in a standard enterprise, managed service provider (MSP), or MSP tenant workspace.

Endpoint: POST /workspaces/v1/credentials/{credentialId}/reset
Version: 1.0.0
Security: BearerAuth

## Path parameters:

  - `credentialId` (string, required)
    The unique ID of the credential.

## Response 200 fields (application/json):

  - `id` (string, required)
    The unique ID of the credential

  - `credentialName` (string, required)
    Name of the credential

  - `clientId` (string, required)
    The client ID of the credential

  - `clientSecret` (string, required)
    The client secret of the credential

  - `type` (string, required)
    The type of resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time the credential was created in UTC

  - `updatedAt` (string, required)
    Time the credential was updated in UTC

  - `associatedTenant` (object)
    Associated tenant for the credentials being created

  - `associatedTenant.resourceUri` (string, required)
    The unique URI of the MSPs reference to the tenant

  - `associatedTenant.tenantName` (string, required)
    The name of the tenant the resourceUri is associated with

  - `associatedServiceManagerProvision` (object)
    Service Manager Provision for the credentials.

  - `associatedServiceManagerProvision.resourceUri` (string, required)
    The resource URI of the service manager provision

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

## Response 409 fields (application/json):

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


