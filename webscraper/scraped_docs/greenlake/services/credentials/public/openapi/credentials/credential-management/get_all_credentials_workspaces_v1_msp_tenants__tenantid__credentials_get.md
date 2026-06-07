---
title: "GET /workspaces/v1/credentials"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/credentials/credential-management/get_all_credentials_workspaces_v1_msp_tenants__tenantid__credentials_get.md"
scraped_at: "2026-06-07T06:15:15.583971+00:00Z"
---

# Get list of credentials

Retrieve a list of all credentials for a user in a standard enterprise, managed service provider (MSP), or MSP tenant workspace. 

NOTE: Use the filter query parameter in an MSP tenant workspace and filter on the tenantId property.

Endpoint: GET /workspaces/v1/credentials
Version: 1.0.0
Security: BearerAuth

## Query parameters:

  - `filter` (string)
    Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter. 

Get list of credentials that can be filtered by:
  - tenantId

## Response 200 fields (application/json):

  - `items` (array, required)
    Multiple returned credential responses

  - `items.credentialName` (string, required)
    Name of the credential

  - `items.id` (string, required)
    The ID of the credential created

  - `items.clientId` (string, required)
    Client ID of the credential created

  - `items.type` (string, required)
    The type of resource

  - `items.generation` (integer, required)
    Monotonically increasing update counter

  - `items.createdAt` (string, required)
    Time the credential was created in UTC

  - `items.updatedAt` (string, required)
    Time the credential was updated in UTC

  - `items.associatedTenant` (object)
    Associated tenant for the credentials being created

  - `items.associatedTenant.resourceUri` (string, required)
    The unique URI of the MSPs reference to the tenant

  - `items.associatedTenant.tenantName` (string, required)
    The name of the tenant the resourceUri is associated with

  - `items.associatedServiceManagerProvision` (object)
    Service Manager Provision for the credentials.

  - `items.associatedServiceManagerProvision.resourceUri` (string, required)
    The resource URI of the service manager provision

  - `count` (integer, required)
    The number of credentials returned

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


