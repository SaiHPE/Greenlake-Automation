---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/openapi/changelog.md"
scraped_at: "2026-06-07T06:13:31.637342+00:00Z"
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

Credential Management was renamed API Client Credentials and moved to **Services** > [API Client Credentials](/docs/greenlake/services/credentials/public). No functionality of any API was changed.

## April 2024

Added four HPE GreenLake for Credential Management APIs. With these APIs, you can get, add, reset, and delete credentials in standard enterprise, managed service provider (MSP), or an MSP tenant workspace.

### Added

* `GET /workspaces/v1/credentials`
* `POST /workspaces/v1/credentials`
* `DELETE /workspaces/v1/credentials/{id}`
* `POST /workspaces/v1/credentials/{id}/reset`