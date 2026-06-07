---
title: "HPE GreenLake for User Management API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity.md"
scraped_at: "2026-06-07T06:13:41.767780+00:00Z"
---

# HPE GreenLake for User Management API

With the HPE GreenLake for Identity Management APIs you can view, update preferences, and remove users from your workspace.

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

[HPE GreenLake for User Management API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity.yaml)

## User Management

User management operations specific to HPE GreenLake.

### Get users

 - [GET /identity/v1/users](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity/nb-api-user/get_users_identity_v1_users_get.md): Retrieve list of users with filtering, and pagination options. All users are returned when no filters are provided. 
Note: User view all permission is required to invoke this API. 
Rate limit: 300 requests per minute per workspace, resulting in a 429 error if exceeded.

### Invite a user

 - [POST /identity/v1/users](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity/nb-api-user/invite_user_to_account_identity_v1_users_post.md): Invite a user to a workspace.

### Get a user

 - [GET /identity/v1/users/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity/nb-api-user/get_user_detailed_identity_v1_users__id__get.md): Retrieve a single user based on a given user ID.

### Update a user

 - [PUT /identity/v1/users/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity/nb-api-user/update_user_preferences_identity_v1_users__id__put.md): Update an existing user's preferences.

### Disassociate a user

 - [DELETE /identity/v1/users/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb_openapi_identity/nb-api-user/disassociate_platform_user_identity_v1_users__id__delete.md): Delete a user from a workspace.

