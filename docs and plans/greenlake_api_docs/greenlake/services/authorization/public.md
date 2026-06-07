---
title: "HPE GreenLake for Authorization"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public.md"
scraped_at: "2026-06-07T05:45:57.621056+00:00Z"
---

# HPE GreenLake for Authorization

This page provides an introduction and quick start guide for the Authorization API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake for Authorization service enables you to programmatically manage access control within your HPE GreenLake environment. This service serves as the central authority for determining who can access what resources across the HPE GreenLake cloud, ensuring that only authorized users can perform specific actions on protected resources.

Enhanced IAM
This service applies only to workspaces with enhanced Identity and Access Management (IAM) enabled. To learn about configuring enhanced IAM workspaces, see [Creating your company workspace](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-C335D790-5166-406F-B0B8-C93AB46A2C76.html).

### Features

- Manage roles
- Manage user role assignment
- Manage scope groups
- Manage workspace groups


### Scope groups and role assignments

When you assign a role to a user, you can constrain the role assignment to provide access to only a subset of the resources available in a workspace.

A role assignment consists of a subject, such as a user or user group, the role the subject is assigned, and a scope. The scope determines the resources to which the role privileges apply. A scope defines a subset of the resources available in a workspace. Some roles can only be scoped to the entire workspace, that is, the role privileges apply to all the resources in the workspace. Other roles can be scoped to either the entire workspace or to a subset of the resources in the workspace.

A scope group consists of one or more scopes. When you assign a role to a subject, you can set the scope of the role assignment to one or more scope groups which constrains the permissions granted to the subject to the scopes in the scope groups.

### Workspace groups management

The Workspace Groups Management API enables you to create, manage, and organize workspace groups within HPE GreenLake. This service provides comprehensive CRUD (create, read, update, and delete) operations for workspace groups.

### What's new

Date: 2025-11-12

The initial public release of the Workspace Groups Management API.

[View the changelog for more information](/docs/greenlake/services/authorization/public/changelog)

### Related documentation

- [HPE GreenLake Cloud User Guide: Manage workspaces that use enhanced IAM](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-8315DD2B-CD45-4305-9323-3F573EDAF3B9.html)
- [HPE GreenLake Cloud User Guide: Workspace groups](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&docLocale=en_US&page=GUID-3200733C-AF56-4F7E-81F4-7CD9CC5E9A91.html)
- [HPE GreenLake Cloud User Guide: Workspace identity & access](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html)
- [Workspace Glossary](/docs/greenlake/services/workspace/public/glossary) provides detailed information about workspace management terminology.


## Developer guide

The HPE GreenLake Authorization API enables you to programmatically manage access control within your HPE GreenLake environment. This guide provides essential information about the API structure, authorization concepts, and implementation guidelines to help you effectively manage roles and permissions.

Enhanced IAM
This service applies only to workspaces with enhanced Identity and Access Management enabled. To learn about configuring enhanced IAM workspaces, see [Creating your company workspace](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-C335D790-5166-406F-B0B8-C93AB46A2C76.html).

### Prerequisites

#### Endpoint

All Authorization API endpoints are accessible through a single global endpoint:

- `https://global.api.greenlake.hpe.com/`


#### Core API paths

- `/authorization/v1beta1/role-assignments`
- `/authorization/v1beta1/scope-groups`


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token.

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


#### Required permissions

To use the HPE GreenLake Authorization API, you need appropriate permissions based on your role:

- `ccs.authorization.view` for all `GET` or `LIST` requests
- `ccs.authorization.edit` for all `POST`, `PUT`, or `PATCH` requests
- `ccs.authorization.delete` for the `DELETE` request


For more information about roles and permissions, see the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html).

#### Rate limiting

All Authorization API endpoints have a 1000 requests per minute rate limit.

#### API quota

For more information on role assignment quotas, see the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-1F122521-0713-4822-A979-72828C99D1FA.html)

### Making it all work

This section explains how to create a scope group and a role assignment.

Through the examples, you will learn how to find `principal`, `role`, and `scope` , and how to use the `id` returned in the responses to make calls to other endpoints.

#### Creating a scope group

Use the `POST /authorization/v1beta1/scope-groups` endpoint to create a scope group. In the API body, provide a `name` (required) and an optional `description`.

The `name` must be unique to the organization or workspace. Further, it cannot contain `&`, `<`, `>`, `|`, `:`, `,` and cannot have leading or trailing spaces.

An example of a successful response:


```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "type": "authorization/scope-group",
  "name": "sg1",
  "description": "This group gives access to resource \"host/123\"",
  "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/authorization/scope-groups/05f0523c-fd03-47fc-981b-9c4333a37b78",
  "generation": 1,
  "createdAt": "2023-04-06T22:45:59.759943+00:00",
  "updatedAt": "2023-04-06T22:45:59.759943+00:00"
}
```

The `id` returned in the response (for example, `"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"`) can be used as the path parameter to make calls to other scope group endpoints.

#### Adding items to a scope group

Use the `POST /authorization/v1beta1/scope-groups/{scope-group-id}/scopes/batch` endpoint to add items (or resources) to a scope group. In the API body, provide:

- `grn`: The full HPE GreenLake Resource Notation for each resource
- `description`: (Optional) A description for each scope


Example request:


```bash
curl -i -X POST \
  https://global.api.greenlake.hpe.com/authorization/v1beta1/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08/scopes/batch \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {
        "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/compute/servers/abc123",
        "description": "Production server"
      },
      {
        "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/storage/volumes/xyz789",
        "description": "Storage volume for application data"
      }
    ]
  }'
```

Example response:


```json
{
  "successCount": 1,
  "errorCount": 1,
  "successes": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/us-east/providers/bmaas/host/123"
    }
  ],
  "errors": [
    {
      "httpStatusCode": 500,
      "errorCode": "HPE_GL_ERROR_INTERNAL_SERVER_ERROR",
      "message": "The server encountered an unexpected condition which prevented it from fulfilling the request.",
      "debugId": "12312-123123-123123-1231212",
      "errorDetails": [
        {
          "type": "hpe.greenlake.retry_info",
          "retryAfterSeconds": 30
        }
      ]
    }
  ]
}
```

#### Retrieving a scope group by ID

Use the `GET /authorization/v1beta1/scope-groups/{scope-group-id}` endpoint to retrieve details of a specific scope group.

Example request:


```bash
curl -i -X GET \
  https://global.api.greenlake.hpe.com/authorization/v1beta1/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Example response:


```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "type": "authorization/scope-group",
  "name": "sg1",
  "description": "This group gives access to resource \"host/123\"",
  "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/authorization/scope-groups/05f0523c-fd03-47fc-981b-9c4333a37b78",
  "serviceMetadata": {
    "id": "44f0443c-fd03-47fc-981b-9c4333a37b44",
    "type": "/service-catalog/service-offer"
  },
  "generation": 1,
  "createdAt": "2023-04-06T22:45:59.759943+00:00",
  "updatedAt": "2023-04-06T22:45:59.759943+00:00"
}
```

#### Updating a scope group by ID

Use the `PUT /authorization/v1beta1/scope-groups/{scope-group-id}` endpoint to update a scope group's name or description.

Example request:


```bash
curl -i -X PUT \
  https://global.api.greenlake.hpe.com/authorization/v1beta1/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    "name": "sg1"
  }'
```

Example response:


```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "type": "authorization/scope-group",
  "name": "sg1",
  "description": "This group gives access to resource \"host/123\"",
  "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/default/providers/authorization/scope-groups/05f0523c-fd03-47fc-981b-9c4333a37b78",
  "serviceMetadata": {
    "id": "44f0443c-fd03-47fc-981b-9c4333a37b44",
    "type": "/service-catalog/service-offer"
  },
  "generation": 1,
  "createdAt": "2023-04-06T22:45:59.759943+00:00",
  "updatedAt": "2023-04-06T22:45:59.759943+00:00"
}
```

#### Listing scopes in a scope group

Use the `GET /authorization/v1beta1/scope-groups/{scope-group-id}/scopes` endpoint to retrieve all scopes (resources) within a specific scope group.

Example request:


```bash
curl -i -X GET \
  https://global.api.greenlake.hpe.com/authorization/v1beta1/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08/scopes \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Example response:


```json
{
  "items": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "type": "authorization/scope-group/scope",
      "grn": "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60/regions/us-east/providers/bmaas/host/123",
      "description": "host 123",
      "region": "us-east-2",
      "allScopes": false,
      "resourceTypeDisplayName": "Hosts"
    }
  ],
  "count": 1,
  "total": 1,
  "offset": 0
}
```

#### Deleting scopes from a scope group

Use the `DELETE /authorization/v1beta1/scope-groups/{scope-group-id}/scopes/bulk` endpoint to remove multiple scopes (resources) from a scope group.

Example request:


```bash
curl -i -X DELETE \
  https://global.api.greenlake.hpe.com/authorization/v1beta1/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08/scopes/bulk \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {
        "id": "e7b8f8e1-9ad5-432d-a858-499d9f279647"
      },
      {
        "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"
      },
    ]
  }'
```

Example response:


```json
{
  "successCount": 1,
  "errorCount": 1,
  "successes": [
    {
      "id": "e7b8f8e1-9ad5-432d-a858-499d9f279647"
    }
  ],
  "errors": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "httpStatusCode": 500,
      "errorCode": "HPE_GL_ERROR_INTERNAL_SERVER_ERROR",
      "message": "The server encountered an unexpected condition which prevented it from fulfilling the request",
      "debugId": "12312-123123-123123-1231212",
      "errorDetails": [
        {
          "type": "hpe.greenlake.retry_info",
          "retryAfterSeconds": 30
        }
      ]
    }
  ]
}
```

#### Deleting a scope group by ID

Use the `DELETE /authorization/v1beta1/scope-groups/{scope-group-id}` endpoint to delete a scope group. Note that you cannot delete a scope group that is currently in use by any role assignments.

Example request:


```bash
curl -i -X DELETE \
  https://global.api.greenlake.hpe.com/authorization/v1beta1/scope-groups/497f6eca-6276-4993-bfeb-53cbbbba6f08 \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Example response:

204 No Content

#### Creating a role assignment

Use the `POST /authorization/v1beta1/role-assignments` endpoint to create a role assignment.

In the request body you need to provide the `principal`, `role`, and `scope`. This information can be found through the HPE GreenLake UI.

1. Log in to your HPE GreenLake workspace.
2. Click **Manage Workspace**.
3. Click **Workspace identity & access**.
4. From the **Workspace identity & access** page you can find `principal`, `role`, and `scope`.
  - To find `principal`, click **Workspace users** > Select a user > From the **Details** page, copy the **Principal ID**.
  - To find `role`, click **Roles & permissions** > Click on the relevant role > Click **Details** > Copy the **GreenLake resource notation**.
  - To find `scope`, click **Scope groups** > Click on a scope group > Click **Details** > Copy the **GreenLake Resource Notation**.  Alternatively, you can find scope group details using the `GET /authorization/v1beta1/scope-groups` endpoint.


You can now use this information to create your API request.

Example request:


```bash
curl -i -X POST \
  https://hpe-greenlake-developer-portal--iam-authz-test.preview.redocly.app/_mock/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/authorization/v1beta1/role-assignments \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>' \
  -H 'Content-Type: application/json' \
  -d '{
    "principal": "user:123981y2zxhiz1890",
    "role": "grn:glp/providers/authorization/roles/storageservices.LimitedAdmin",
    "scope": [
      "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/msp/tenant-groups/d88d38c9-8cf7-4ab8-a808-126b47bb787d",
      "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/21e582d3-fb24-4162-9fca-350defe24d3c"
    ]
  }'
```

Example response:


```json
{
  "id": "05f2523c-fe03-47fc-981b-9c4333a37b01",
  "type": "authorization/role-assignment",
  "principal": "user:123981y2zxhiz1890",
  "role": "grn:glp/providers/authorization/roles/storageservices.LimitedAdmin",
  "scope": [
    "grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b60"
  ],
  "principalMetadata": {
    "id": "123981y2zxhiz1890",
    "type": "identity/user"
  },
  "roleMetadata": {
    "id": "e54415a9-4f46-43c0-893e-67ec778c6c45",
    "type": "authorization/role"
  },
  "generation": 1,
  "createdAt": "2023-04-06T22:45:59.759943+00:00",
  "updatedAt": "2023-04-06T22:45:59.759943+00:00"
}
```

The `id` returned in the response (for example, `"id": "05f2523c-fe03-47fc-981b-9c4333a37b01",`) can be used as the path parameter to make calls to the following endpoints:

- `GET /authorization/v1beta1/role-assignments/{id}`
- `PUT /authorization/v1beta1/role-assignments/{id}`
- `DELETE /authorization/v1beta1/role-assignments/{id}`