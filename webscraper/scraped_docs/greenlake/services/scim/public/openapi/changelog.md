---
title: "HPE GreenLake SCIM User and Group Management API - Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/scim/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:24.292399+00:00Z"
---

# HPE GreenLake SCIM User and Group Management API - Changelog

All notable changes to the HPE GreenLake SCIM User and Group Management API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 2025-08-18

### Added

The initial public release of the HPE GreenLake SCIM User and Group Management API. The following `v2beta1` endpoints were made available:

- **User management operations**
  - `POST /identity/v2beta1/scim/v2/Users`—Create new users
  - `GET /identity/v2beta1/scim/v2/Users`—List users with filtering support
  - `GET /identity/v2beta1/scim/v2/Users/{userId}`—Retrieve individual user details
  - `PATCH /identity/v2beta1/scim/v2/Users/{userId}`—Update user attributes
  - `DELETE /identity/v2beta1/scim/v2/Users/{userId}`—Delete user accounts
- **Group management operations**
  - `POST /identity/v2beta1/scim/v2/Groups`—Create new user groups
  - `GET /identity/v2beta1/scim/v2/Groups`—List groups with filtering support
  - `GET /identity/v2beta1/scim/v2/Groups/{groupId}`—Retrieve individual group details
  - `PATCH /identity/v2beta1/scim/v2/Groups/{groupId}`—Update group attributes and membership
  - `DELETE /identity/v2beta1/scim/v2/Groups/{groupId}`—Delete user groups
- **Membership management extensions**
  - `GET /identity/v2beta1/scim/v2/extensions/Groups/{groupId}/users`—List users in a specific group
  - `GET /identity/v2beta1/scim/v2/extensions/Users/{userId}/groups`—List groups for a specific user