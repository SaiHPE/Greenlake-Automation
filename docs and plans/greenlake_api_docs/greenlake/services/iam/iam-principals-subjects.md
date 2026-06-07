---
title: "Identity Principals | HPE GreenLake"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/iam-principals-subjects.md"
scraped_at: "2026-06-07T05:45:54.751138+00:00Z"
---

# HPE GreenLake Identity Principals

## Executive Summary

In HPE GreenLake, a principal is an entity that can be authenticated and authorized to access resources. Principals can represent users, devices, API clients, services, or AI agents. They are fundamental to access control, determining who can access specific resources and under what conditions. This document outlines the different representations of principals within HPE GreenLake, particularly the transition from v1 to v2 syntax.

**Note**: The `api-client` principal type represents a broad class of non-human identities used for automation and programmatic access. Future releases may introduce additional specialized non-human identity types.

## Principal Syntax Representations

HPE GreenLake utilizes two versions (v1 and v2) for representing subjects and security principals in APIs and access tokens. The v2 representation is the current standard, offering broader support for different principal types.

### V2 Representation (Current Standard)

Version 2 supports multiple principal types, each identified by a prefix and an opaque global ID. This format is used in IAM v2 APIs and access tokens.


```text
# User Principal
# Represents an individual user
user:<opaque-global-id>

# API Client Principal
# Represents non-human identities including:
# - Automation and scripting
# - Platform-managed services
api-client:<opaque-id>

# User Group Principal
# Represents a collection of users
user-group:<opaque-id-within-org>
```

**Understanding API Client Principal Type**: The `api-client` principal type encompasses various non-human identity patterns used throughout HPE GreenLake Platform. These identities enable automated workflows, service integration, and programmatic access without binding operations to individual human user accounts.

### V1 Representation (Legacy - to be deprecated)

Version 1 only supported user principals identified solely by their email address formatted string. This representation is considered legacy and will be progressively deprecated in favor of the more comprehensive v2 format.


```text
# Example V1 User Principal
john.doe@hpe.com
```

## Principals as Subjects in Authorization

When managing and evaluating access policies, such as Role-Based Access Control (RBAC), a principal is referred to as a **subject**. The subject identifier (using the v2 syntax) is used within RBAC policies to assign roles and is embedded within access tokens to represent the authenticated entity requesting access.

A subject is a representation of a principal when performing policy management and evaluation, such as Role Based Access Control.  The subject is specific both in the RBAC Policy for role assignment and in the access tokens.

![Authentication & Authorization Illusrration](/assets/authn-authz-illustration.43400f543fda17f8b29f1a0b15a5b35cb1f23b24fdd220ab9b20a4e31ec22e79.3bd884bd.png)

### Authorization APIs

For details on how subjects are used in authorization requests and policies, refer to the AuthZ API documentation:

### Access Tokens

For information on how principal/subject information is represented within different types of access tokens, see the Access Token guide:

* [Access Token Types and Formats](/docs/greenlake/guides/internal/token_guides/token_types_and_formats/).