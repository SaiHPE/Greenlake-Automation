---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/changelog.md"
scraped_at: "2026-06-07T06:13:21.658275+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

The format is group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2026-02-10

### Changed

* Better describe and fix typos on `/authorization/v1beta1/scope-groups` APIs
* Better describe and fix typos on `/authorization/v1beta1/role-assignments` APIs


### Removed

* API `/authorization/v1beta1/roles` was removed


## 2025-11-12

### Added

The initial release of the Workspace Groups Management API. The following endpoints were released:

* `POST /workspaces/v1beta1/groups`—Create new workspace groups
* `GET /workspaces/v1beta1/groups`—Retrieve existing groups in a workspace
* `GET /workspaces/v1beta1/groups/{groupId}`—Retrieve specific groups details
* `PUT /workspaces/v1beta1/groups/{groupId}`—Update workspace group properties
* `DELETE /workspaces/v1beta1/groups/{groupId}`—Delete a specific workspace group
* `POST /workspaces/v1beta1/groups/{groupId}/group-workspaces`—Add workspaces to groups
* `GET /workspaces/v1beta1/groups/{groupId}/group-workspaces`—Retrieve workspaces from groups
* `DELETE /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}`—Remove workspace from workspace groups
* `GET /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}`—Retrieve workspace details from a group


## 2025-11-07

### Added

* Initial release of the HPE GreenLake Authorization API v1beta1
* Role assignment management endpoints:
  * `POST /authorization/v1beta1/role-assignments`—Create a role assignment
  * `GET /authorization/v1beta1/role-assignments/{id}`—Get a specific role assignment
  * `PUT /authorization/v1beta1/role-assignments/{id}`—Update a role assignment
  * `DELETE /authorization/v1beta1/role-assignments/{id}`—Delete a role assignment
  * `GET /authorization/v1beta1/role-assignments`—List role assignments with OData filtering support
* Scope group management endpoints:
  * `POST /authorization/v1beta1/scope-groups`—Create a scope group
  * `GET /authorization/v1beta1/scope-groups`—Retrieve all scope groups with OData filtering, sorting, and pagination
  * `GET /authorization/v1beta1/scope-groups/{id}`—Retrieve a specific scope group by ID
  * `PUT /authorization/v1beta1/scope-groups/{id}`—Update a scope group by ID
  * `DELETE /authorization/v1beta1/scope-groups/{id}`—Delete a scope group by ID
  * `GET /authorization/v1beta1/scope-groups/{id}/scopes` —Retrieve the scope list for a scope group
  * `POST /authorization/v1beta1/scope-groups/{id}/scopes/batch`—Add items to a scope group scope list (synchronous, non-atomic)
  * `DELETE /authorization/v1beta1/scope-groups/{id}/scopes/bulk` —Delete items from a scope group scope list (synchronous, atomic)