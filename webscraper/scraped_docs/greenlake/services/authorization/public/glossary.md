---
title: "HPE GreenLake for Authorization glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/authorization/public/glossary.md"
scraped_at: "2026-06-07T06:13:21.666275+00:00Z"
---

# HPE GreenLake for Authorization glossary

## Acronyms

### GRN

The HPE GreenLake Resource Notation (GRN) is the standardized, URI-compatible syntax (`grn:glp/workspaces/...`) used to define and specify this scope within the HPE GreenLake. The GRN provides a unique, hierarchical identifier (encompassing platform instances, workspaces, regions, providers, and specific resources) that allows for precise targeting of resources.

For example:

* A GRN for a specific virtual machine defines a narrow scope limited to that virtual machine.
* A GRN prefix for a workspace defines a broader scope encompassing all resources within that workspace.
* A GRN for a service provider within a region defines a scope covering resources managed by that provider in that location.


Use cases:

* Unambiguous resource identification.
* Defining policies where the resource's tenancy is critical.


Examples:


```
# Workspace Scoped Resource:

grn:{platform-instance}/workspaces/{id}/regions/{name|default}/providers/{namespace}/{resource-type}/{id}

# Entire Workspace Scope:

grn:{platform-instance}/workspaces/{id}

# Platform Scoped Resource (not workspace specific):

grn:{platform-instance}/providers/{namespace}/{resource-type}/{id}
```

## Terms

### Authorization

Authorization is the process of granting or denying access to resources based on the authenticated user's identity and permissions. It involves checking whether a user has the appropriate permissions to access a specific resource or perform a particular action. Authorization helps enforce security by restricting access to sensitive information and resources to authorized users only.

Some protocols like Oauth2 cross the boundary between authentication and authorization.

### Group membership

The association between MSP Tenants and workspace groups, defining which MSP tenants belong to which workspace groups.

### Principal

A principal is an entity that can be authenticated and authorized to access resources. A principal can be a user, a device, an API client, or a system. Principals are essential components of access control, as they are used to determine who can access what resources and under what conditions.

### Role categories

HPE GreenLake provides two types of roles:

1. **Predefined Roles**—Managed by HPE, offering standardized permissions for common functions:
  * **Administrator roles**—Comprehensive management capabilities (view, edit, delete)
  * **Operator roles**—Day-to-day operational activities (view, edit)
  * **Observer roles**—Read-only access (view only)
2. **Custom Roles**—User-configurable permission sets tailored to specific organizational requirements


### Subject

A subject is a representation of a principal, which is used to enforce access control policies. Subjects can be used to define permissions, roles, and other attributes that determine what a principal can access. They are essential components of identity management, as they are used to manage and control access to resources based on the identity and privileges of the principal.

### Workspace group

A collection of MSP Tenants that can be managed together with an MSP for authorization and access control purposes.