---
title: "HPE GreenLake for Workspace Management glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/glossary.md"
scraped_at: "2026-06-07T05:46:16.691096+00:00Z"
---

# HPE GreenLake for Workspace Management glossary

## Acronyms

### MSP

A managed service provider (MSP) workspace is an operational mode between a service provider and clients. This workspace is best suited for service providers to manage their client’s HPE GreenLake workspaces, devices, and licenses across all HPE cloud services. An MSP workspace is a multi-tenant operational mode with options to manage multiple independent HPE GreenLake workspaces from a single interface.

## Terms

### Workspace Types

#### Standard Enterprise Workspace

This is a single-tenant environment for a single customer and it is the default workspace type.

A standard enterprise workspace can use enhanced Identity and Access Management (IAM). When you create a standard enterprise workspace, you can optionally choose to create a workspace that uses the new IAM experience (enhanced IAM) with the option to enable Organization Governance.

#### MSP workspace

A managed service provider (MSP) workspace is an operational mode between a service provider and their clients. This workspace type is best suited for service providers to manage their client’s HPE GreenLake workspaces, devices, and licenses across all HPE cloud services. An MSP workspace is a multi-tenant operational mode with options to manage multiple independent tenant workspaces from a single interface.

#### MSP Tenant

In HPE GreenLake MSPs, tenancy is hierarchical. This means a managed service provider (MSP) workspace can have child tenants, each with resources dedicated to it. An MSP tenant is always managed by an MSP workspace.

MSPs can create two types of tenant workspaces:

- MSP-owned mode: The MSP owns the devices and subscriptions and also manages the workspace on behalf of their customers.
- Customer-owned mode: The customer owns their own assets, but the MSP manages their workspace.


### Organization Governance

The Organization Governance feature provides a centralized, organization-wide, identity management system for administrators. When you configure the Organization Governance feature, an organization is created which provides the following identity and access management capabilities:

- User life cycle management. A single, organization-wide user directory provides a view of all users in the organization.
- Ability to create and manage user groups which are applicable across all organization workspaces.
- Create additional workspaces in the organization.
- Exclusively claim email domains for the organization.
- Configure single sign-on (SSO) for all workspaces in the organization.