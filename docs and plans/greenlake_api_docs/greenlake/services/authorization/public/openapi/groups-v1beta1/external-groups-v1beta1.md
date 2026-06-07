---
title: "Workspace Groups Management API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1.md"
scraped_at: "2026-06-07T06:13:34.966025+00:00Z"
---

# Workspace Groups Management API

CRUD operations for Workspace Groups Management

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

[Workspace Groups Management API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1.yaml)

## Groups

### Create a workspace group

 - [POST /workspaces/v1beta1/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/createnewgroupv2.md): Creates a group for various group types

### List of Paginated workspace groups

 - [GET /workspaces/v1beta1/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/getgroupsv2.md): Get the paginated list of Groups associated to the workspace

### Add a workspace to the group

 - [POST /workspaces/v1beta1/groups/{groupId}/group-workspaces](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/addworkspacetogroup.md): Add workspace to a group

### List of paginated workspaces associated with the group ID

 - [GET /workspaces/v1beta1/groups/{groupId}/group-workspaces](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/listgroupworkspaces.md): Get the paginated list of workspaces associated with the group ID

### Get the workspace details

 - [GET /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/getgroupworkspace.md): Get the workspace details by group ID

### Remove a workspace from the workspace group

 - [DELETE /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/deleteworkspacefromgroup.md): Remove workspace from a group

### Get the workspace group details

 - [GET /workspaces/v1beta1/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/fetchgroupv2.md): Get the workspace group details by group ID

### Update workspace group details

 - [PUT /workspaces/v1beta1/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/putgroupv2.md): Updates group details name and description

### Delete the workspace group

 - [DELETE /workspaces/v1beta1/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/groups-v1beta1/external-groups-v1beta1/groups/removegroupv2.md): Delete the existing workspace group from the account

