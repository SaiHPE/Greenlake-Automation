---
title: "HPE GreenLake SCIM User and Group Management"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/scim.md"
scraped_at: "2026-06-07T06:13:20.967024+00:00Z"
---

# HPE GreenLake SCIM User and Group Management

This page provides an introduction and quick start guide for the SCIM User and Group Management API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake SCIM User and Group Management API provides standardized user and group management operations compliant with SCIM (System for Cross-domain Identity Management) 2.0 specifications. This API enables you to automate identity lifecycle management, synchronize user data across systems, and maintain group memberships throughout your HPE GreenLake cloud environment.

System for Cross-domain Identity Management (SCIM) is an open standard that enables the secure automation of user and group data between a company's cloud applications and a service provider. You can create an external SCIM integration to synchronize users and groups between your identity provider and an organization in HPE GreenLake cloud.

SCIM integrations are supported only by Organization Governance organizations.

When you configure a SCIM integration for your organization, users and user groups are created and managed in the organization by your IdP. On the platform, workspace administrators manage role assignments for integration users and user groups but cannot do any of the following:

- Create, update, and delete users for the domain associated with the integration
- Add or remove user groups or change the membership of user groups created through the integration


Once users or user groups are added to the organization through an integration, the workspace administrator assigns roles to these users and user groups in specific workspaces.

Organization administrators can add or remove integration-managed users from user groups that were created outside of the integration.

### Features

- Create, read, update, and delete user accounts with SCIM 2.0 compliance
- Manage user groups and group memberships
- List users assigned to specific groups and groups assigned to users
- HPE GreenLake-specific extensions for enhanced user and group metadata
- Support for POSIX user extensions


### Use cases

- **Identity provisioning automation**—Create and configure user accounts when new employees join, ensuring consistent access across all HPE GreenLake services
- **Group-based access management**—Organize users into groups based on roles, departments, projects, and so on to streamline permission management and maintain security boundaries
- **Directory synchronization**—Synchronize user and group information between external identity providers and HPE GreenLake


### What's new

Date: 2025-08-18

Initial public release of the HPE GreenLake SCIM User and Group Management API.

[View the Changelog for more information](/docs/greenlake/services/scim/public/openapi/changelog)

### Related documentation

- [SCIM Definitions, Overview, Concepts and Requirements](https://tools.ietf.org/html/rfc7642)
- [SCIM Core Schema](https://tools.ietf.org/html/rfc7643)
- [SCIM Protocol](https://tools.ietf.org/html/rfc7644)
- [HPE GreenLake Cloud User Guide: Organization Governance](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-3EC0BF03-721B-49A3-B4A0-4F955808AEB3.html)
- [JSON Web Token Best Current Practices](https://datatracker.ietf.org/doc/html/rfc8725)


## Developer guide

This section covers authentication, permissions, and practical examples for implementing user and group management using the SCIM API.

### Prerequisites

#### Endpoints

Endpoints are the host URLs to which you will submit your API requests. To access HPE GreenLake SCIM User and Group Management APIs, use the unified API:

- `https://global.api.greenlake.hpe.com`


#### URIs

- `/identity/v2beta1/scim/v2/Users`
- `/identity/v2beta1/scim/v2/Users/{userId}`
- `/identity/v2beta1/scim/v2/Groups`
- `/identity/v2beta1/scim/v2/Groups/{groupId}`
- `/identity/v2beta1/scim/v2/extensions/Groups/{groupId}/users`
- `/identity/v2beta1/scim/v2/extensions/Users/{userId}/groups`


#### Getting an access token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#generating-an-access-token)
  - [View code samples for generating an access token.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


#### Access and permissions

| Endpoint | Permission | Resource |
|  --- | --- | --- |
| `GET /identity/v2beta1/scim/v2/Users` | identity.users.read | User |
| `POST /identity/v2beta1/scim/v2/Users` | identity.users.create | User |
| `GET /identity/v2beta1/scim/v2/Users/{userId}` | identity.users.read | User |
| `PATCH /identity/v2beta1/scim/v2/Users/{userId}` | identity.users.update | User |
| `DELETE /identity/v2beta1/scim/v2/Users/{userId}` | identity.users.delete | User |
| `GET /identity/v2beta1/scim/v2/Groups` | identity.user-groups.read | Group |
| `POST /identity/v2beta1/scim/v2/Groups` | identity.user-groups.create | Group |
| `GET /identity/v2beta1/scim/v2/Groups/{groupId}` | identity.user-groups.read | Group |
| `PATCH /identity/v2beta1/scim/v2/Groups/{groupId}` | identity.user-groups.update | Group |
| `DELETE /identity/v2beta1/scim/v2/Groups/{groupId}` | identity.user-groups.delete | Group |


:::info
Learn more about configuring roles and permissions in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html).
:::

#### Rate limits

**Group management:**

| Operation | Endpoint | Request limit |
|  --- | --- | --- |
| GET | `/identity/v2beta1/scim/v2/Groups` | 6000 per minute |
| GET | `/identity/v2beta1/scim/v2/Groups/{groupId}` | 6000 per minute |
| CREATE | `POST /identity/v2beta1/scim/v2/Groups` | 1000 per minute |
| PATCH | `PATCH /identity/v2beta1/scim/v2/Groups/{groupId}` | 1000 per minute |
| DELETE | `DELETE /identity/v2beta1/scim/v2/Groups/{groupId}` | 1000 per minute |


**User management:**

| Operation | Endpoint | Request limit |
|  --- | --- | --- |
| GET | `/identity/v2beta1/scim/v2/Users` | 6000 per minute |
| GET | `/identity/v2beta1/scim/v2/Users/{userId}` | 6000 per minute |
| CREATE | `POST /identity/v2beta1/scim/v2/Users` | 1000 per minute |
| DELETE | `DELETE /identity/v2beta1/scim/v2/Users/{userId}` | 1000 per minute |


**Group extensions:**

| Operation | Endpoint | Request limit |
|  --- | --- | --- |
| GET | `/identity/v2beta1/scim/v2/extensions/Groups/{groupId}/users` | 6000 per minute |


**User extensions:**

| Operation | Endpoint | Request limit |
|  --- | --- | --- |
| GET | `/identity/v2beta1/scim/v2/extensions/Users/{userId}/groups` | 6000 per minute |


### Making it all work

This section provides examples of creating users and explains SCIM attributes, HPE GreenLake extensions, and POSIX user attributes.

#### Creating a new user with SCIM attributes

Use the `POST /identity/v2beta1/scim/v2/Users` endpoint to create a new user account with required SCIM attributes and HPE GreenLake extensions.

To learn more about the SCIM attributes and extensions, see [Understanding SCIM](#understanding-scim).

Example request body:


```json
{
  "schemas": "urn:ietf:params:scim:schemas:core:2.0:User",
  "userName": "abc@xyz.com",
  "displayName": "Barbara Jensen",
  "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:User": {
    "countryCode": "US"
  },
  "name": {
    "familyName": "Jensen",
    "givenName": "Barbara"
  },
  "emails": [
    {
      "primary": true,
      "value": "abc@xyz.com"
   }
  ]
}
```

Sample API response:


```json
{
  "schemas": "urn:ietf:params:scim:schemas:core:2.0:User",
  "id": "00gs3w909WxZ4CIjl356",
  "active": false,
  "userName": "abc@xyz.com",
  "displayName": "Joe Smith",
  "meta": {
    "created": "string",
    "lastModified": "string",
    "lastLogin": "string",
    "location": "string",
    "resourceType": "User",
    "version": "string"
  },
  "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:User": {
    "status": "STAGED",
    "countryCode": "US",
    "primaryEmailVerified": true,
    "hpe_principal": "user:448ebfdb-7bc9-402f-9eb0-f9a86c06ca5a",
    "source": "Local",
    "sourceInstance": "organization UUID"
  },
  "name": {
    "familyName": "Jensen",
    "givenName": "Barbara"
  },
  "emails": [
    {
      "primary": true,
      "value": "abc@xyz.com"
    }
  ]
}
```

##### Understanding SCIM

SCIM (System for Cross-domain Identity Management) schemas define the attributes and structure of resources like users and groups in identity management systems. These schemas provide a standardized way to represent identity data, enabling interoperability between different systems and services.

A SCIM schema consists of:

- A unique identifier (URI)
- A set of attribute definitions
- Metadata about the resource type


SCIM schemas allow organizations to:

- Consistently represent user identity data across systems.
- Automate user provisioning and deprovisioning.
- Enable secure identity synchronization between applications.
- Support cloud-based identity management solutions.


For more information, see the [SCIM 2.0 documentation](https://tools.ietf.org/html/rfc7644).

HPE GreenLake implements extensions to the SCIM schemas.

| HPE user extension attributes | HPE group extension attributes |
|  --- | --- |
| `status` - User status (for example,  "STAGED") | `hpe_principal` - Group principal identifier |
| `countryCode` - User's country code (for example, "US") | `groupDescription` - Description of the group |
| `primaryEmailVerified` - Email verification status | `source` - Source system (for example, "Local") |
| `hpe_principal` - User principal identifier | `sourceInstance` - The organization's UUID |
| `source` - Source system (for example, "Local") |  |
| `sourceInstance` - Organization UUID |  |


Example HPE SCIM schemas:


```json
{
    "Resources": [
        {
            "schemas": "urn:ietf:params:scim:schemas:core:2.0:User",
            "id": "00gs3w909WxZ4CIjl356",
            "active": false,
            "userName": "abc@xyz.com",
            "displayName": "Joe Smith",
            "meta": {
                "created": "string",
                "lastModified": "string",
                "lastLogin": "string",
                "location": "string",
                "resourceType": "User",
                "version": "string"
            },
            "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:User": {
                "status": "STAGED",
                "countryCode": "US",
                "primaryEmailVerified": true,
                "hpe_principal": "user:448ebfdb-7bc9-402f-9eb0-f9a86c06ca5a",
                "source": "Local",
                "sourceInstance": "organization UUID"
            },
            "name": {
                "familyName": "Smith",
                "givenName": "Joe"
            },
            "emails": [
                {
                    "primary": true,
                    "value": "abc@xyz.com"
                }
            ]
        }
    ]
}
```


```json
{
  "Resources": [
    {
      "schemas": "urn:ietf:params:scim:schemas:core:2.0:Group",
      "id": "00gs3w909WxZ4CIjl356",
      "displayName": "Sales Group",
      "meta": {
        "created": "string",
        "lastModified": "string",
        "location": "string",
        "resourceType": "Group"
      },
      "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group": {
        "hpe_principal": "user-group:448ebfdb-7bc9-402f-9eb0-f9a86c06ca5a",
        "groupDescription": "Office users",
        "source": "Local",
        "sourceInstance": "organization UUID"
      }
    }
  ]
}
```

#### Creating a user with SCIM and POSIX attributes

Use the `POST /identity/v2beta1/scim/v2/Users` endpoint to create a new user account with required SCIM attributes and POSIX-user attributes relevant to POSIX-compliant systems. To learn more, see [Understanding POSIX](#understanding-posix).

Sample request body:


```json
{
  "schemas": "urn:ietf:params:scim:schemas:core:2.0:User",
  "userName": "abc@xyz.com",
  "displayName": "Barbara Jensen",
  "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:User": {
    "countryCode": "US"
  },
  "name": {
    "familyName": "Jensen",
    "givenName": "Barbara"
  },
  "emails": [
    {
      "primary": true,
      "value": "abc@xyz.com"
    }
  ]
}
```

Sample API response:


```json
{
  "schemas": "urn:ietf:params:scim:schemas:core:2.0:User",
  "id": "00gs3w909WxZ4CIjl356",
  "active": false,
  "userName": "abc@xyz.com",
  "displayName": "Barbara Jensen",
  "meta": {
    "created": "string",
    "lastModified": "string",
    "lastLogin": "string",
    "location": "string",
    "resourceType": "User",
    "version": "string"
  },
  "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:User": {
    "status": "STAGED",
    "countryCode": "US",
    "primaryEmailVerified": true,
    "hpe_principal": "user:448ebfdb-7bc9-402f-9eb0-f9a86c06ca5a",
    "source": "Local",
    "sourceInstance": "organization UUID"
  },
  "name": {
    "familyName": "Jensen",
    "givenName": "Barbara"
  },
  "emails": [
    {
      "primary": true,
      "value": "abc@xyz.com"
    }
  ],
  "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:posix:User": {
    "uid": 1001,
    "userName": "jdoe",
    "gid": 2001,
    "homeDirectory": "/home/jdoe",
    "shell": "/bin/bash"
  }
}
```

##### Understanding POSIX

POSIX (Portable Operating System Interface) is a family of standards specified by the IEEE to maintain compatibility between different operating systems. It defines the API, command line shells, and utility interfaces for software compatibility with variants of Unix and other operating systems.

The POSIX user extension provides essential attributes needed for user accounts on POSIX-compliant systems. This extension is used when:

- Provisioning users to Linux/Unix servers or containers.
- Integrating with file systems that require numeric user or group IDs.
- Managing SSH access or shell accounts.
- Synchronizing with LDAP directories that include POSIX attributes.


The POSIX extension contains:

- `uid`—A numeric identifier for the user account (User ID).
- `userName`—The login name for the user.
- `gid`—The primary group identifier (Group ID) for the user.
- `homeDirectory`—The user's home directory path, for example, `/home/username`.
- `shell`—The user's default command shell, for example, `/bin/bash`.


An example of a POSIX user schema:


```json
{
  "urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:posix:User": {
    "uid": 1001,
    "userName": "jdoe",
    "gid": 2001,
    "homeDirectory": "/home/jdoe",
    "shell": "/bin/bash"
  }
}
```

#### Understanding strongly claimed domains

To enable the SCIM integration features, it is necessary to configure a strongly claimed domain in the organization.

- GreenLake provides a TXT record that the user puts into their DNS records that GreenLake can validate automatically.
- Once validated, the organization has claimed the domain.


For more details, see [Claiming a domain](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-29C5FE95-3E25-4675-A392-8D2596AE033F.html).