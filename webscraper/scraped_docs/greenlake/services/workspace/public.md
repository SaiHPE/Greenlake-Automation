---
title: "HPE GreenLake for Workspace Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public.md"
scraped_at: "2026-06-07T05:46:16.691311+00:00Z"
---

# HPE GreenLake for Workspace Management

This page provides an introduction and quick start guide for the Workspace Management API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

HPE GreenLake for Workspace Management APIs allow programmatic access to the records of workspaces and workspace-user relationships. The Workspace Management APIs allow you to perform tasks without the user interface. You can:

- Retrieve information about workspaces.
- Create, delete, update, and check tenant information using a token from their workspaces.


### Features

- API to retrieve workspace information
- Managed Service Provider (MSP) tenant management


### API availability across platforms

| Endpoint | HPE GreenLake cloud | HPE GreenLake Dedicated Platform |
|  --- | --- | --- |
| `GET /workspaces/v1/workspaces/{workspaceId}` | Yes | Yes |
| `GET /workspaces/v1/msp-tenants` | Yes | Yes |
| `POST /workspaces/v1/msp-tenants` | Yes | Yes |
| `PUT /workspaces/v1/msp-tenants/{tenantId}` | Yes | Yes |
| `DELETE /workspaces/v1/msp-tenants/{tenantId}` | Yes | Yes |


### What's new

June 2024

The HPE GreenLake for Workspace Management APIs were relocated to the main navigation menu to make them easier to find.

[View the changelog to view a history of changes](/docs/greenlake/services/workspace/public/openapi/changelog).

## Developer guide

The examples in this guide help you use the Workspace Management APIs for workspace and tenant management.

### Prerequisites

#### Endpoints

Endpoints are the host URLs to which you will submit your API requests. To access Workspace Management APIs, use the unified API:

- `https://global.api.greenlake.hpe.com`


#### URIs

Unique Resource Identifiers (URIs) are used to identify a server or resources. A URI is a full API path ending in an identification number. For example:

- `/workspaces/v1/msp-tenants/{tenantId}`


#### Access and permissions

You need the correct role and permissions to use the HPE GreenLake Workspaces API. A role is a group of permissions that you can specify and assign to users in your HPE GreenLake workspace. There are 3 basic role types distinguished by the privileges defined in the authorization service:

- Administrator—has view, edit, and delete privileges in the workspace.
- Operator—has view and edit privileges in the workspace.
- Observer—has only view privileges in the workspace.


The following table lists Workspaces API calls along with the resource and permission required to make the call:

| Workspaces API call | Resource | Permission  required |
|  --- | --- | --- |
| `GET /workspaces/v1/workspaces/{workspaceId}` | Platform Customer Account | View |
| `GET /workspaces/v1/msp-tenants` | Platform Customer Account | View |
| `POST /workspaces/v1/msp-tenants` | Platform Customer Account | Edit |
| `PUT /workspaces/v1/msp-tenants/{tenantId}` | Platform Customer Account | Edit |
| `DELETE /workspaces/v1/msp-tenants/{tenantId}` | Platform Customer Account | Delete |


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making It all work

#### Workspace

With the workspace API, you can discover information about the workspace the API is configured for.

##### Get basic workspace information

To see information on the workspace, submit the following `GET` request
specifying the workspace ID:


```sh
GET https://global.api.greenlake.hpe.com/workspaces/v1/workspaces/<id>
```

This API call returns workspace information like ID, type, creation, created date and time, updated date and time, created by, and the workspace's name.

Sample response:


```json
{
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "type": "string",
    "generation": 0,
    "createdAt": "2019-08-24T14:15:22Z",
    "updatedAt": "2019-08-24T14:15:22Z",
    "workspaceName": "string",
    "createdBy": "user@example.com"
}
```

##### Get detailed workspace information

To retrieve the workspace address and contact details, use the following `GET` API call specifying the workspace ID:


```sh
GET https://global.api.greenlake.hpe.com/workspaces/v1/workspaces/<id>/contact
```

Sample response:


```json
{
    "address": {
        "streetAddress": "string",
        "streetAddressComplement": "string",
        "city": "string",
        "stateOrRegion": "string",
        "zip": "string",
        "countryCode": "string"
    },
    "phoneNumber": "string",
    "email": "user@example.com"
}
```

#### Tenant management

With the tenant management APIs, you can:

- Get a list of tenants
- Create a tenant
- Update tenant information
- Delete a tenant


##### Obtain a list of tenants

To retrieve a list of tenants in a managed service provider (MSP) workspace, submit the following `GET` request:


```sh
GET https://global.api.greenlake.hpe.com/workspaces/v1/msp-tenants
```

This API call returns:

- Workspace ID, workspace name, and creator
- Pagination information: offset, count, items, and total


Sample response:


```json
{
    "offset": 0,
    "count": 0,
    "total": 0,
    "items": [
        {
        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        "type": "string",
        "generation": 0,
        "createdAt": "2019-08-24T14:15:22Z",
        "updatedAt": "2019-08-24T14:15:22Z",
        "workspaceName": "string",
        "createdBy": "user@example.com"
        }
    ]
}
```

##### Create a tenant

To create a new tenant in an MSP workspace, submit a `POST` request:


```sh
POST https://global.api.greenlake.hpe.com/workspaces/v1/msp-tenants
```

Payload:


```json
{
    "address": {
        "streetAddress": "string",
        "streetAddressComplement": "string",
        "city": "string",
        "stateOrRegion": "string",
        "zip": "string",
        "countryCode": "AW"
    },
    "phoneNumber": "string",
    "email": "user@example.com",
    "workspaceName": "string",
    "description": "string"
}
```

A valid response generates a location header, and the response payload returns a tenant-created message.

##### Update tenant information

To update tenant information, submit the following `PUT` request:


```sh
PUT https://global.api.greenlake.hpe.com/workspaces/v1/msp-tenants/<id>
```

Payload:


```json
{
    "address": {
        "streetAddress": "string",
        "streetAddressComplement": "string",
        "city": "string",
        "stateOrRegion": "string",
        "zip": "string",
        "countryCode": "AW"
    },
    "phoneNumber": "string",
    "email": "user@example.com",
    "workspaceName": "string",
    "description": "string"
}
```

The response payload returns a tenant-created message.

##### Delete a tenant

To delete a tenant from an MSP workspace, submit the following `DELETE` request specifying the tenant ID in the path:


```sh
DELETE https://global.api.greenlake.hpe.com/workspaces/v1/msp-tenants/<id>
```