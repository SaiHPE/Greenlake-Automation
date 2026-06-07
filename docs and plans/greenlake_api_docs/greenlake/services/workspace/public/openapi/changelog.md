---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:26.305117+00:00Z"
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


## June 2024

Added the Workspace Management APIs after being moved from Identity & Access Management.

### Added

* `GET /workspaces/v1/workspaces/{workspaceId}`
* `GGET /workspaces/v1/msp-tenants`
* `POST /workspaces/v1/msp-tenants`
* `PUT /workspaces/v1/msp-tenants/{tenantId}`
* `DELETE /workspaces/v1/msp-tenants/{tenantId}`