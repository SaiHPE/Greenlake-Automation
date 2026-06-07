---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/changelog.md"
scraped_at: "2026-06-07T06:13:31.258671+00:00Z"
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


## 2026-January

A new version of the Audit Logs API was released. The endpoint `GET /audit-log/v2beta1/logs/{id}` is new to the v2beta1 version of the API.

### Added

* `GET /audit-log/v2beta1/logs`
* `GET /audit-log/v2beta1/logs/{id}`
* `GET /audit-log/v2beta1/logs/{id}/details`


## 2025-May

### Removed

The following APIs have been removed:

* `GET audit-log/v1beta1/logs`
* `GET audit-log/v1beta1/logs/{audit-id}/detail`


## 2024-September

### Added

The following APIs were released:

* `GET audit-log/v1/logs`
* `GET audit-log/v1/logs/{audit-id}/detail`


### Deprecated

The following APIs have been deprecated:

* `GET audit-log/v1beta1/logs`
* `GET audit-log/v1beta1/logs/{audit-id}/detail`


## 2024-March

The initial `v1beta1` release of HPE GreenLake for Audit Log APIs.

### Added

* `GET audit-log/v1beta1/logs`
* `GET audit-log/v1beta1/logs/{audit-id}/detail`