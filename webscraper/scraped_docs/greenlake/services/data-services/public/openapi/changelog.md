---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:19.807272+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format is group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2025-02-17

### Changed

The following public APIs were changed to return multiple associated resources and deprecate redundant fields:

* `GET /data-services/v1beta1/dual-auth-operations`
* `GET /data-services/v1beta1/dual-auth-operations/{id}`
* `PATCH /data-services/v1beta1/dual-auth-operations/{id}`


## 2024-12-13

### Added

The following public APIs were added:

* `PATCH /data-services/v1beta1/issues/{id}`


## 2024-09-12

### Changed

The API servers host names were changed to adopt the standard regional
endpoint host names in the form: `<region>.api.greenlake.hpe.com`.

## 2024-09-11

### Added

The following public APIs were added:

* `GET /data-services/v1beta1/settings`
* `GET /data-services/v1beta1/settings/{id}`
* `PATCH /data-services/v1beta1/settings/{id}`