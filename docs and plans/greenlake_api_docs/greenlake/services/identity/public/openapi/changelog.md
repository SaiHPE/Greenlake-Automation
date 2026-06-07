---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:22.279565+00:00Z"
---

# Changelog

All notable changes to the internal APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format is group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## August 2024

Identity Management was renamed User Management and moved to **Services** > [User Management](/docs/greenlake/services/identity/public). No functionality of any API was changed.

## June 2024

Workspace Management APIs have moved directly under **Services** > [Workspaces](/docs/greenlake/services/workspace/public). No functionality of any API has been changed.

The name for Workspaces was changed to Identity and Credential Management.

### Removed

* `GET /workspaces/v1/workspaces/{workspaceId}`
* `GET /workspaces/v1/msp-tenants`
* `POST /workspaces/v1/msp-tenants`
* `PUT /workspaces/v1/msp-tenants/{tenantId}`
* `DELETE /workspaces/v1/msp-tenants/{tenantId}`


## April 2024

Added four HPE GreenLake for Credential Management APIs. With these APIs, you can get, add, reset, and delete credentials in standard enterprise, managed service provider (MSP), or an MSP tenant workspace.

### Added

* `GET /workspaces/v1/credentials`
* `POST /workspaces/v1/credentials`
* `DELETE /workspaces/v1/credentials/{id}`
* `POST /workspaces/v1/credentials/{id}/reset`