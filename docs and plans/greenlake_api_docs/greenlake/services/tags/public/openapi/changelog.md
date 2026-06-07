---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/tags/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:25.344438+00:00Z"
---

# Changelog

All notable changes to the public APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

Group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2025-January

### Added

As part of the transition to the stable `v1` version, the following endpoints were added:

* `GET /tags/v1/tags`
* `GET /tags/v1/tag-resources`


### Deprecated

As part of the transition to the stable `v1` version, the following `v1beta1` endpoints were deprecated and will no longer be available from 2025-05-05:

* `GET /tags/v1beta1/tags`
* `GET /tags/v1beta1/tag-resources`


## 2024-July-10

### Added

The initial public APIs were added:

* `GET /tags/v1beta1/tags`
* `GET /tags/v1beta1/tag-resources`