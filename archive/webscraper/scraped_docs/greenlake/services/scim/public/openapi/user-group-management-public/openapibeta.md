---
title: "HPE GreenLake SCIM User and Group Management APIs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta.md"
scraped_at: "2026-06-07T06:13:38.056748+00:00Z"
---

# HPE GreenLake SCIM User and Group Management APIs

User and Group Management APIs compliant with [SCIM 2.0](https://tools.ietf.org/html/rfc7644).

Version: v2.0
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Access token compliant with [RFC8725](https://datatracker.ietf.org/doc/html/rfc8725). Issued by HPE GreenLake.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake SCIM User and Group Management APIs](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapiBeta.yaml)

## SCIM v2beta1

[SCIM 2.0](https://tools.ietf.org/html/rfc7644)-compliant management operations for users and groups.

### List users assigned to a user group

 - [GET /identity/v2beta1/scim/v2/extensions/Groups/{groupId}/users](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/groupmembersscim.md): Get users assigned to a user group.

### List user groups assigned to a user

 - [GET /identity/v2beta1/scim/v2/extensions/Users/{userId}/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/usergroupmembersscim.md): Get user groups assigned to a user.

### Create a user

 - [POST /identity/v2beta1/scim/v2/Users](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/createuserscim.md): Creates a user. Compliant with SCIM 2.0.

### List users

 - [GET /identity/v2beta1/scim/v2/Users](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/listusersscim.md): List users. Compliant with SCIM 2.0.

### Get a user

 - [GET /identity/v2beta1/scim/v2/Users/{userId}](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/getuserscim.md): Retrieve a user. Compliant with SCIM 2.0.

### Delete a user

 - [DELETE /identity/v2beta1/scim/v2/Users/{userId}](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/deleteuserscim.md): Delete a user. Compliant with SCIM 2.0.

### Patch user attributes

 - [PATCH /identity/v2beta1/scim/v2/Users/{userId}](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/patchuserscim.md): Updates one or more user attributes. Compliant with SCIM 2.0, except the attributes field is not supported.

### List user groups

 - [GET /identity/v2beta1/scim/v2/Groups](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/listgroupsscim.md): Get a list of user groups. Compliant with SCIM 2.0.

### Create a user group

 - [POST /identity/v2beta1/scim/v2/Groups](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/creategroupscim.md): Create a user group. Compliant with SCIM 2.0.

### Get a user group

 - [GET /identity/v2beta1/scim/v2/Groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/getgroupscim.md): Get a user group. Compliant with SCIM 2.0.

### Update user group

 - [PATCH /identity/v2beta1/scim/v2/Groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/patchgroupscim.md): Add or remove users from a user group, or update the group name or description. Compliant with SCIM 2.0.

### Delete a user group

 - [DELETE /identity/v2beta1/scim/v2/Groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/user-group-management-public/openapibeta/scim-v2beta1/deletegroupscim.md): Delete a user group. Compliant with SCIM 2.0.

