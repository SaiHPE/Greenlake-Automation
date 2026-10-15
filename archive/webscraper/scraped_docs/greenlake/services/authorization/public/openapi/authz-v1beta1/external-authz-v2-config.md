---
title: "HPE GreenLake for Authorization API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config.md"
scraped_at: "2026-06-07T06:13:34.594422+00:00Z"
---

# HPE GreenLake for Authorization API

The HPE GreenLake for Authorization API provides a unified way to manage the authorization function for HPE GreenLake cloud.

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

[HPE GreenLake for Authorization API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config.yaml)

## Role Assignments

Role assignments are composed of three pieces (principal, role, and scope). Role assigments associate a user, group, or service (principal) with a specific role (along with its permissions) at a particular scope (a resource or group of resources) to grant them access and specify their responsibilities within HPE GreenLake.
<br><br>**Note:** There is a maximum limit of 50 role assignments per user per workspace. <br><br>**Note:** Users can manage roles and retrieve a role identifier (ID / GRN) using the Web Interface. Once the role ID / GRN is retrieved then a role assignment can be created using the API described below.

### Create a role assignment

 - [POST /authorization/v1beta1/role-assignments](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/role-assignments/createroleassignmentv1beta1.md): Create a role assignment.
By creating a role assignment, you grant access to resources. Role assignments allow for controlled management of permissions and responsibilities.
Note: For assistance finding the principal, scope, and role identifiers, see the developer guide.

### Retrieve all role assignments

 - [GET /authorization/v1beta1/role-assignments](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/role-assignments/getroleassignmentsv1beta1.md): Retrieves role assignments by applying OData 4.0 filters. Use the filter parameter to provide a filter string. Supports in and and operators on role, scope and principal attributes. Example Request: /authorization/v1beta1/role-assignments?filter=role in ('grn:glp/providers/authorization/roles/storageservices.LimitedAdmin') and principal in ('user:123981y2zxhiz1890')
Note:
- No duplicate attributes in OData filter: Each attribute (role, scope, principal) can only appear once in the OData filter expression. Multiple occurrences will result in a 400 Bad Request error.
- Supported operators: Only the in and and operators are supported.

### Retrieve a role assignment instance by ID

 - [GET /authorization/v1beta1/role-assignments/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/role-assignments/getroleassignmentv1beta1.md)

### Update a role assignment instance by ID

 - [PUT /authorization/v1beta1/role-assignments/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/role-assignments/updateroleassignmentv1beta1.md): Allows updating scopes of an existing role assignment. Request body must contain id, principal and role attributes even though they are immutable.  The id can be found in the response body of POST /authorization/v1beta1/role-assignments.  Note: For assistance finding the principal, scope, and role identifiers, see the developer guide.

### Delete a role assignment instance by ID

 - [DELETE /authorization/v1beta1/role-assignments/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/role-assignments/deleteroleassignmentv1beta1.md)

## Scope Groups

A scope group is composed of scopes and allows a single role assignment against multiple scopes.
<br><br> Known limitations <ul> <li>There is a max limit of 500 scopes per scope group.</li> <li>There is a max limit of 500 scope groups per workspace.</li> </ul>

### Create a scope group

 - [POST /authorization/v1beta1/scope-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/createscopegroupv1beta1.md): A scope group is a collection of scopes that can be assigned to a role assignment. This allows a single role assignment to cover multiple scopes. Note:  
A scope group cannot contain another scope group (no nesting).
Once created, a scope group will belong to a organization/workspace based on the caller context.
The returned grn attribute will include this context and can be used as a global unique identifier.

### Retrieve all scope groups

 - [GET /authorization/v1beta1/scope-groups](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/getscopegroupsv1beta1.md): Retrieves scope groups by applying OData 4.0 filters. Use the filter parameter to provide a filter string. Supports in operator on serviceMetadata/id, name or grn attributes. Example Request: /authorization/v1beta1/scope-groups?filter=grn in ('grn:glp/workspaces/05f0523c-fd03-47fc-981b-9c4333a37b70/regions/default/providers/authorization/scope-groups/123')
Note:
- No duplicate attributes in OData filter: Each attribute (serviceMetadata/id, name, grn) can only appear once in the OData filter expression. Multiple occurrences will result in a 400 Bad Request error.
- Only one attribute in OData filter: Only one attribute (serviceMetadata/id, name or grn) can be used at a time, otherwise it will result in a 400 Bad Request error.
- Supported operators: Only in operator is supported.

### Retrieve a scope group instance by ID

 - [GET /authorization/v1beta1/scope-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/getscopegroupv1beta1.md)

### Update a scope group instance by ID

 - [PUT /authorization/v1beta1/scope-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/updatescopegroupv1beta1.md): Request body must contain id attribute even though it is immutable.

### Delete a scope group instance by ID

 - [DELETE /authorization/v1beta1/scope-groups/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/deletescopegroupv1beta1.md)

### Retrieve the scope group scopes list

 - [GET /authorization/v1beta1/scope-groups/{id}/scopes](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/getscopegroupscopesv1beta1.md): Retrieves a list of scopes for a specific scope group. Results are sorted by description and GRN alphabetically by default.

### Add scopes to a scope group

 - [POST /authorization/v1beta1/scope-groups/{id}/scopes/batch](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/addscopegroupscopesv1beta1.md): Add new scopes to an existing scope group. This operation is synchronous and non-atomic.

### Delete scopes from a scope group

 - [DELETE /authorization/v1beta1/scope-groups/{id}/scopes/bulk](https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/openapi/authz-v1beta1/external-authz-v2-config/scope-groups/deletescopegroupscopesv1beta1.md): Delete scopes from an existing scope group. The scope group ID can be found in the response body of GET /authorization/v1beta1/scope-groups while the scope ID to be deleted can be found in the response body of GET /authorization/v1beta1/scope-groups/{id}/scopes. This operation is synchronous and non-atomic.

