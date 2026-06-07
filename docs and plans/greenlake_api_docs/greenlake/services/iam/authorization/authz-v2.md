---
title: "Role-Based Access Control (RBAC) in HPE GreenLake"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/authorization/authz-v2.md"
scraped_at: "2026-06-07T06:13:32.000460+00:00Z"
---

# Role-Based Access Control (RBAC) in HPE GreenLake

## Overview

The HPE GreenLake Authorization (AuthZ) service provides a comprehensive framework for managing and controlling access to your HPE GreenLake resources. This service serves as the central authority for determining who can access what resources across the HPE GreenLake Platform, ensuring that only authorized users can perform specific actions on protected resources.

## Key Components

HPE GreenLake's RBAC implementation consists of four essential elements:

- **Permissions**: Granular access rights to perform specific operations
- **Roles**: Collections of permissions that represent job functions or responsibilities
- **Scopes**: Boundaries that define where permissions apply within your environment
- **Assignments**: Connections that link users or groups to roles within specific scopes


## How It Works

The Authorization service continuously evaluates access requests against defined policies to determine if users have appropriate privileges to access service-owned resources. This evaluation occurs based on:

1. The user's identity and workspace context
2. Roles assigned to the user
3. The specific scope of the resource being accessed
4. The permission required for the requested operation


## Benefits

- **Enhanced Security**: Implement least-privilege access principles across your environment
- **Simplified Administration**: Manage access through roles rather than individual permissions
- **Operational Efficiency**: Align access controls with organizational structures and responsibilities
- **Compliance Support**: Maintain clear access boundaries and audit trails for governance requirements


## Getting Started

To begin working with HPE GreenLake RBAC, see the [Authorization Management API Guide](/docs/greenlake/services/iam/authorization/authz-v2/guide) for detailed implementation instructions.