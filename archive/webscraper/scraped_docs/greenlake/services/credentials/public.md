---
title: "HPE GreenLake API Client Credentials"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public.md"
scraped_at: "2026-06-07T06:13:26.888168+00:00Z"
---

# HPE GreenLake API Client Credentials

This page provides an introduction and quick start guide for the API Client Credentials API:

- [Overview](#overview)—See a high-level description of the service.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with token generation.


## Overview

HPE GreenLake API Client Credentials allow you to programmatically interact with HPE GreenLake services without requiring user interaction. These credentials are ideal for automation scenarios, scheduled tasks, CI/CD pipelines, and backend service integrations. These APIs enable developers to create, manage, and use credentials for authenticating automated workflows and applications across workspaces.

### Key features

- **Secure authentication**—Generate and manage client credentials with appropriate scoping
- **Workspace-specific access**—Create tokens scoped to specific workspaces
- **MSP Support**—Exchange tokens between parent and tenant workspaces (for MSPs)
- **Programmatic control**—Full API access for credential lifecycle management


### Access token scope

Each workspace requires an access token scoped specifically to that workspace. Typically, you must create API client credentials in each workspace to obtain a workspace-scoped access token.

- Learn more about [basic token generation](/docs/greenlake/services/credentials/public#developer-guide)


### MSP token exchange

For Managed Service Provider (MSP) workspaces hosted in HPE GreenLake Cloud, token exchange is supported. MSPs can generate a single set of credentials in their parent workspace, use them to acquire a signed access token, and then exchange that token for tenant-scoped tokens as needed.

This process follows the [OAuth 2.0 Token Exchange specification (IETF RFC 8693)](https://datatracker.ietf.org/doc/html/rfc8693).

- Learn more about [MSP token exchange](/docs/greenlake/services/credentials/public/msp-token-exchange)


### API availability across platforms

The following table shows the availability of API endpoints across HPE GreenLake platforms:

| Endpoint | HPE GreenLake Cloud | HPE GreenLake Dedicated Platform |
|  --- | --- | --- |
| `GET /workspaces/v1/credentials` | ✓ | ✓ |
| `POST /workspaces/v1/credentials` | ✓ | ✓ |
| `DELETE /workspaces/v1/credentials/{id}` | ✓ | ✓ |
| `POST /workspaces/v1/credentials/{id}/reset` | ✓ | ✓ |
| Token Exchange | ✓ | ✗ |


### What's new

August 2024

- HPE GreenLake for Credential Management was renamed to HPE GreenLake API Client Credentials
- APIs were moved from the Identity & Access Management category to a dedicated section
- No changes to API functionality


For complete details on all changes, see the [changelog](/docs/greenlake/services/credentials/public/openapi/changelog/).

### Related documentation

- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-CCD4CFC8-D67A-4AFF-953D-637A68588009.html)
- [MSP Token Exchange Guide](/docs/greenlake/services/credentials/public/msp-token-exchange/)


## Developer guide

The examples in this guide help you use the HPE GreenLake for API Client Credentials.

- For information on basic token generation, see [Token generation guide](#token-generation-guide).
- For detailed implementation steps for MSP environments, see the [MSP Token Exchange Guide](/docs/greenlake/services/credentials/public/msp-token-exchange/).


### Prerequisites

#### Endpoints

Endpoints are the host URLs to which you will submit your API requests. To access HPE GreenLake for API Client Credentials APIs, use the unified API:

- `https://global.api.greenlake.hpe.com`


#### URIs

Unique Resource Identifiers (URIs) are used to identify a server or resource used within the users and workspaces. A URI is a full API path ending with an identification number. For example:

- `/identity/v1/users/{userId}`


#### Access token scopes

Each workspace requires an access token scoped specifically to that workspace. An access token allows your application to make authenticated API requests to HPE GreenLake services within the scope of that workspace.

##### Single workspace token process

For single workspace token generation, you need to:

1. Create API client credentials in each workspace where you need to make API calls.
2. Use these credentials to obtain a workspace-scoped access token.
3. Include this token in your API requests to that specific workspace.


##### MSP token exchange process

For Managed Service Provider (MSP) workspaces hosted in HPE GreenLake Cloud, token exchange functionality simplifies credential management:

1. Generate a single set of credentials in your parent (MSP) workspace.
2. Use these credentials to acquire a signed access token for the parent workspace.
3. Exchange that token for tenant-scoped tokens as needed.


This token exchange process follows the [OAuth 2.0 Token Exchange specification (IETF RFC 8693)](https://datatracker.ietf.org/doc/html/rfc8693), which provides a secure method for obtaining delegation tokens.

MSP environments
For detailed implementation steps for MSP environments, see the [MSP Token Exchange Guide](/docs/greenlake/services/credentials/public/msp-token-exchange).

#### Access and permissions

To use HPE GreenLake API Client Credentials, you must have the appropriate role and permissions in your HPE GreenLake cloud workspace.

The following table outlines the specific permissions required for each API endpoint:

| API Endpoint | Resource | Permission Required |
|  --- | --- | --- |
| `GET /workspaces/v1/credentials` | Workspace | View |
| `POST /workspaces/v1/credentials` | Workspace | Edit |
| `DELETE /workspaces/v1/credentials/{id}` | Workspace | Delete |
| `POST /workspaces/v1/credentials/{id}/reset` | Workspace | Edit |


For more information about roles and permissions, see the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html):

- View preconfigured roles and their permissions
- Learn how to create custom roles
- Discover how to assign roles to users


#### Generating tokens

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Token generation guide

With the API Client Credentials, you can:

- Create a credential
- List the credentials you have created
- Reset the secret of a credential
- Delete a credential


You can perform these operations for the HPE GreenLake cloud service and provisioned services in standard enterprise, managed service provider (MSP), and MSP tenant workspaces.

The following API descriptions clarify the optional parameters for managing MSP tenant workspaces and provisioned service managers.

#### Create a credential

To create a new credential in a workspace, submit a `POST` request:


```sh
POST https://global.api.greenlake.hpe.com/workspaces/v1/credentials
```

The elements of the APIs payload are the `credentialName` and optionally `associatedTenant` and `associatedServiceManagerProvision`.

- **Credential name**—Human readable alias for this credential.
- **Associated tenant** (MSP only)—A reference to the tenant in which this credential will be created. If you supply an `associatedTenant`, it will be returned in the response payload.


You need to supply the UUID of the workspace. To find the UUID:

- Use the [Get basic workspace information](/docs/greenlake/services/workspace/public#get-basic-workspace-information) API to find your workspace UUID.
  - Alternatively, [use the HPE GreenLake UI](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-653D562B-53B9-4B23-91BD-6646C8AB8641.html).
- (MSP only) Use the [Obtain a list of tenants](/docs/greenlake/services/workspace/public#obtain-a-list-of-tenants) API to find workspace UUIDs for the MSP tenant workspace.



```json Example associated tenant
"associatedTenant": {
    "resourceUri": "/workspaces/v1/workspaces/<UUID of Workspace>"
}
```

(Optional) Provide an associated service manager provision. This refers to the instance of the provisioned service in your workspace to which you want to link the credential. If you supply an `associatedServiceManagerProvision`, the response payload will return it.

You need to supply the UUID of the provisioned service instance.

- To find this UUID, use the [GET a list of provisioned service managers](/docs/greenlake/services/service-catalog/public#get-a-list-of-provisioned-service-managers) API.



```json Example associated service manager provision
"associatedServiceManagerProvision": {
    "resourceUri": "/service-catalog/v1beta1/service-manager-provisions/<UUID of provisioned service instance>"
}
```

##### Sample request with both associatedTenant and associatedServiceManagerProvision


```json
{
    "credentialName": "<A human readable alias for your new credential>",
    "associatedServiceManagerProvision": {
        "resourceUri": "/service-catalog/v1beta1/service-manager-provisions/767c0c92-5ecc-4952-85d6-04a2acaaf050"
    }
    "associatedTenant": {
        "resourceUri": "/workspaces/v1/workspaces/eba3541b-db86-465f-9cae-31f33ccb1fa0"
    }
}
```

##### Sample response


```json
{
    "id": "fa4e341b-db86-495f-9cee-31f48bba1ea0",
    "credentialName": "My credential",
    "clientId": "fa4e341b-db86-495f-9cee-31f48bba1ea0",
    "clientSecret": "9163c936b93911ee822c16e5bfc542a7",
    "type": "credentials",
    "generation": 1,
    "createdAt": "2024-01-22 15:18:59.936526",
    "updatedAt": "2024-01-22 15:18:59.936526",
    "associatedTenant": {
        "resourceUri": "/workspaces/v1/workspaces/aa4e3a1a-cc83-335b-9cae-b93911ee822c",
        "tenantName": "Tenant ABC"
    },
    "associatedServiceManagerProvision": {
        "resourceUri": "/service-catalog/v1beta1/service-manager-provisions/767c0c92-5ecc-4952-85d6-04a2acaaf050"
    }
}
```

#### Listing your credentials

To list the credentials, submit a `GET` request:


```sh
GET https://global.api.greenlake.hpe.com/workspaces/v1/credentials
```

- **Associated service manager provision**—If a credential was created with an `associatedServiceManagerProvision` it will be present in the response for that credential.
- **Associated tenant** (MSP only) —If a credential was created with an `associatedTenant` it will be present in the response for that credential.
- **Filtering** (MSP only)—For MSP workspaces, this `GET` endpoint supports filtering using the OData standard. To retrieve credentials in an MSP tenant, append `?filter='tenantId eq <The tenantId of interest>'` to the GET request.


Sample response with `associatedTenant` and `associatedServiceManagerProvision`:


```json
{
    "items": [
        {
            "credentialName": "Credential Demo",
            "associatedServiceManagerProvision": {
                "resourceUri": "/service-catalog/v1beta1/service-manager-provisions/767c0c92-5ecc-4952-85d6-04a2acaaf050"
            },
            "associatedTenant": {
                "resourceUri": "/workspaces/v1/workspaces/aa4e3a1a-cc83-335b-9cae-b93911ee822c",
                "tenantName": "Tenant ABC"
            },
            "id": "b660bcc4-1914-45b1-81a8-fcff6cb82a9e",
            "clientId": "b660bcc4-1914-45b1-81a8-fcff6cb82a9e",
            "type": "credentials",
            "generation": 1,
            "createdAt": "2024-01-22 10:00:00.000000",
            "updatedAt": "2024-01-22 10:00:00.000000"
        }
    ],
    "count": 1
}
```

#### Reset the secret of a credential

Use the reset endpoint to regenerate the `clientSecret` of a credential. POST to the endpoint, supplying the `id` of the credential you wish to reset.


```sh
POST https://global.api.greenlake.hpe.com/workspaces/v1/credentials/{id}/reset
```

- **Associated service manager provision**—If a credential was created with an `associatedServiceManagerProvision` it will be present in the response for that credential.
- **Associated tenant**(MSP only) —If a credential was created with an `associatedTenant` it will be present in the response for that credential.


Sample response with `associatedTenant` and `associatedServiceManagerProvision`:


```json
{
    "credentialName": "Credential Demo",
    "id": "fa4e341b-db86-495f-9cee-31f48bba1ea0",
    "clientId": "fa4e341b-db86-495f-9cee-31f48bba1ea0",
    "clientSecret": "8274d83827b93912dd811c16f5bfa542b6",
    "type": "credentials",
    "generation": 1,
    "createdAt": "2024-01-22 15:19:00.000000",
    "updatedAt": "2024-01-22 15:19:00.000000",
    "associatedServiceManagerProvision": {
        "resourceUri": "/service-catalog/v1beta1/service-manager-provisions/767c0c92-5ecc-4952-85d6-04a2acaaf050"
    },
    "associatedTenant": {
        "resourceUri": "/workspaces/v1/workspaces/aa4e3a1a-cc83-335b-9cae-b93911ee822c",
        "tenantName": "Tenant ABC"
    },
}
```

#### Delete a credential

Use the delete endpoint to delete a credential. Submit a `DELETE` request to the endpoint supplying the `id` of the credential you wish to delete.


```sh
DELETE https://global.api.greenlake.hpe.com/workspaces/v1/credentials/{id}
```

A successful deletion returns an HTTP status 204.

### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the `GET` or `PUT` action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query's resources are limited to results for the specified username. Within the filter, the separator is a space.


```sh
GET <URI>?filter=username eq 'user@example.com'
```

#### Filtering on a single property


```sh
filter = <propertyName> <comparison operation> <literal>
```

`GET /workspaces/v1/credentials?filter=tenantId eq '7600415a-8876-5722-9f3c-b0fd11112283'`

Examples of the possible filter values:

| **Filter** | **Example** | **Description** |
|  --- | --- | --- |
| tenantId | `tenantId eq '7600415a-8876-5722-9f3c-b0fd11112283'` | Returns credentials for a user within a particular tenant, only enabled for MSP managed tenants. |


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).