---
title: "HPE GreenLake Authorization Management API Guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/authz-v2/guide.md"
scraped_at: "2026-06-07T05:46:20.776940+00:00Z"
---

# HPE GreenLake Authorization Management API Guide

## Overview

The HPE GreenLake Authorization Management API enables you to programmatically manage access control within your HPE GreenLake environment. This guide provides essential information about the API structure, authorization concepts, and implementation guidelines to help you effectively manage roles and permissions.

> **Note**: This documentation applies only to workspaces with the IAM v2 experience enabled.


## API Basics

### Endpoint

All Authorization APIs are accessible through a single base endpoint:


```http
https://global.api.greenlake.hpe.com/
```

### Core API Paths

The Authorization API includes the following primary resource paths:

- `/authorization/v2alpha2/resource-providers/{providerId}/resource-types`
- `/authorization/v2alpha2/resource-providers/{providerId}/permissions`
- `/authorization/v2alpha2/roles/`
- `/authorization/v2alpha2/role-assignments`
- `/authorization/v2alpha2/scope-groups`


## Authorization Framework

HPE GreenLake implements Role-Based Access Control (RBAC) as its authorization framework, consisting of three fundamental components:

### RBAC Model Core Components

- **Permissions**: Specific rights that enable actions on resources
- **Roles**: Structured collections of permissions that define allowed actions
- **Role Assignments**: Connections linking users, groups, or API clients (subjects) to roles within defined contexts (scopes)


### Role Categories

HPE GreenLake provides two types of roles:

1. **Predefined Roles**: Managed by HPE, offering standardized permissions for common functions:
  - **Administrator roles**: Comprehensive management capabilities (view, edit, delete)
  - **Operator roles**: Day-to-day operational activities (view, edit)
  - **Observer roles**: Read-only access (view only)
2. **Custom Roles**: User-configurable permission sets tailored to specific organizational requirements


### Permission Attributes

Each permission contains the following attributes:

| Attribute | Type | Description |
|  --- | --- | --- |
| **name** | string (≤ 128 chars) | Unique identifier following the convention `<resource provider>.<resource type>.<action>`. This value is immutable once created. |
| **description** | string | Human-readable explanation of the permission's function and scope |
| **releaseStage** | string | Lifecycle status of the permission. See release stage values below. |
| **customRoleUse** | string | Controls whether the permission can be used in custom roles. Values: `ALLOW` or `DENY` |
| **applicableResourceTypes** | array of strings (required, 1-100 items) | List of resource types this permission applies to |
| **fixedScope** | boolean | When `true`, the permission cannot be associated with resource types and their instances |


#### Release Stage Values

Each permission has a `releaseStage` property that indicates its lifecycle status. This property is essential for managing permission deprecation and migration processes.

| Stage | Description | Usage |
|  --- | --- | --- |
| `ALPHA` | Early development stage, subject to breaking changes | Not recommended for production use |
| `BETA` | Feature-complete but may have minor changes | Limited production use with caution |
| `STABLE` | Production-ready, stable API contract | Recommended for all production implementations |
| `DEPRECATED` | Marked for removal, replacement potentially available | Migration required, will be removed in future release |


### Resource Scoping

Role assignments use HPE GreenLake Resource Notation (GRN) for precise scope definition using a standardized, URI-compatible syntax (`grn:glp/workspaces/...`). GRN creates unique resource identifiers through a structured hierarchy (platform, workspace, region, provider, resource).

> For complete details, see the [GreenLake Resource Notation - GRN Specification](/docs/greenlake/services/iam/greenlake-resource-notation)


## Working with the API

### Authentication

Before using the Authorization API, you must:

1. Configure API credentials
2. Generate an OAuth-based access token
3. Use the token as an authorization bearer token in your API requests


For detailed instructions, refer to the [API Credentials Guide](/docs/greenlake/services/credentials/public).

### Required Permissions

To use the HPE GreenLake Authorization API, you need appropriate permissions based on your role:

- **Administrator**: Complete access with view, edit, and delete privileges
- **Operator**: Operational access with view and edit privileges
- **Observer**: Limited access with view-only privileges


For more information about roles and permissions, see the [HPE GreenLake Platform User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html).

## Key Concepts

### IAM Principals

In HPE GreenLake, a principal is an entity that can be authenticated and authorized to access resources. Principals may represent users, devices, API clients, or services and are fundamental to determining access rights.

> Learn more about [HPE GreenLake Identity Principals](/docs/greenlake/services/iam/iam-principals-subjects)


### Best Practices

To optimize security and efficiency when implementing RBAC:

1. **Apply Least Privilege Principles**: Grant only the minimum permissions necessary for users to perform their required functions
2. **Implement Role Separation**: Establish distinct roles aligned with specific job functions
3. **Maintain Consistent Naming Conventions**: Use clear, standardized naming across resources, permissions, and roles
4. **Define Appropriate Scopes**: Utilize precise resource scoping to properly contain access controls