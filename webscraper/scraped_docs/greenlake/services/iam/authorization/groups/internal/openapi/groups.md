---
title: "Workspace Groups Management API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups.md"
scraped_at: "2026-06-07T05:46:48.398416+00:00Z"
---

# Workspace Groups Management API

Workspace Groups Management API

Version: 1.0.0-beta
License: HPE End User License Agreement

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### bearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Workspace Groups Management API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/index.yaml)

## Groups

CRUD operations for Workspace Groups Management

### Create a Workspace Group

 - [POST /workspaces/v1beta1/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/createnewgroupv2.md): Creates a group for various group types

### List of Paginated Workspace Groups

 - [GET /workspaces/v1beta1/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/getgroupsv2.md): Get the paginated list of Groups associated to the workspace

### Add a Workspace to the Group

 - [POST /workspaces/v1beta1/groups/{groupId}/group-workspaces](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/addworkspacetogroup.md): Add workspace to a group

### List of paginated workspaces associated with the group ID

 - [GET /workspaces/v1beta1/groups/{groupId}/group-workspaces](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/listgroupworkspaces.md): Get the paginated list of workspaces associated with the group ID

### Get the Workspace details

 - [GET /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/getgroupworkspace.md): Get the Workspace details by group ID

### Remove a Workspace from the workspace Group

 - [DELETE /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/deleteworkspacefromgroup.md): Remove workspace from a group

### Get the Workspace Group details

 - [GET /workspaces/v1beta1/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/fetchgroupv2.md): Get the Workspace Group details by group ID

### Update Workspace Group details

 - [PUT /workspaces/v1beta1/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/putgroupv2.md): Updates group details name and description

### Delete the Workspace Group

 - [DELETE /workspaces/v1beta1/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/groups/internal/openapi/groups/groups/removegroupv2.md): Delete the existing Workspace Group from the account

