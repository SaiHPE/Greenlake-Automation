---
title: "HPE GreenLake for Workspace Management API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace.md"
scraped_at: "2026-06-07T06:13:41.810801+00:00Z"
---

# HPE GreenLake for Workspace Management API

With the HPE GreenLake for Workspace Management APIs you can view workspace information and create, update, or delete managed service provider tenants.

Version: 1.0.0
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### BearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake for Workspace Management API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace.yaml)

## Workspace Management

Workspace management operations for HPE GreenLake. 

### Get workspace information

 - [GET /workspaces/v1/workspaces/{workspaceId}](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/get_workspace_workspaces_v1_workspaces__workspaceid__get.md): Retrieve basic workspace information for a provided workspace identifier.

### Get detailed workspace information

 - [GET /workspaces/v1/workspaces/{workspaceId}/contact](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/get_workspace_detailed_info_workspaces_v1_workspaces__workspaceid__contact_get.md): Retrieve detailed workspace information.

### Get list of MSP Tenants

 - [GET /workspaces/v1/msp-tenants](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/get_tenants_workspaces_v1_msp_tenants_get.md): Retrieve a list of managed service provider (MSP) tenants.

### Create MSP customer workspace

 - [POST /workspaces/v1/msp-tenants](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/create_tenant_workspaces_v1_msp_tenants_post.md): Create an MSP customer workspace.

### Update managed service tenant

 - [PUT /workspaces/v1/msp-tenants/{tenantId}](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/update_tenant_api_workspaces_v1_msp_tenants__tenantid__put.md): Update an existing tenant in the currently logged in managed service provider (MSP) workspace.

### Delete a managed service tenant

 - [DELETE /workspaces/v1/msp-tenants/{tenantId}](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_workspace/nb-api-workspaces/remove_tenant_workspaces_v1_msp_tenants__tenantid__delete.md): Delete a tenant in the currently logged in managed service provider's (MSP) workspace.

