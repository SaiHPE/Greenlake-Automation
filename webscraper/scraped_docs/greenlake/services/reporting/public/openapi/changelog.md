---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:23.690712+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

The format is group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2026-04-30

### Removed

The following `v1alpha1` Reporting paths are no longer served after the deprecation period that began on 2025-03-12. Use the `v1` endpoints instead.

* `POST /reporting/v1alpha1/report-exports` → `POST /reporting/v1/report-exports`
* `GET /reporting/v1alpha1/report-exports-metadata` → `GET /reporting/v1/report-exports-metadata`
* `GET /reporting/v1alpha1/statuses` → `GET /reporting/v1/statuses`
* `GET /reporting/v1alpha1/async-operations/{id}` → `GET /reporting/v1/async-operations/{id}`
* `GET /reporting/v1alpha1/statuses/{id}` → `GET /reporting/v1/statuses/{id}`
* `GET /reporting/v1alpha1/fixed-filters` → use `GET /reporting/v1/report-exports-metadata` for supported filters and columns


## 2025-03-12

### Added

The following APIs were released as v1 stable versions:

* `POST /reporting/v1/report-exports`
* `GET /reporting/v1/report-exports-metadata`
* `GET /reporting/v1/statuses`
* `GET /reporting/v1/async-operations`
* `GET /reporting/v1/statuses/{id}`


### Deprecated

The following alpha APIs have been deprecated:

* `POST /reporting/v1alpha1/report-exports`
* `GET /reporting/v1alpha1/report-exports-metadata`
* `GET /reporting/v1alpha1/statuses`
* `GET /reporting/v1alpha1/async-operations`
* `GET /reporting/v1alpha1/statuses/{id}`


## 2024-07-08

Added the initial APIs for HPE GreenLake for Reporting API.

### Added

The following APIs were added and released.

* `POST report exports`
* `GET report exports metadata`
* `GET report statuses`
* `GET asynchronous operation details`
* `GET report status by ID`


## 2024-03-12

### Added

The following APIs were released:

* `POST /reporting/v1/report-exports`
* `GET /reporting/v1/statuses`
* `GET /reporting/v1/async-operations`
* `GET /reporting/v1/report-exports-metadata`
* `GET /reporting/v1/statuses/{id}`


### Deprecated

The following APIs have been deprecated:

* `POST /reporting/v1alpha1/report-exports`
* `GET /reporting/v1alpha1/statuses`
* `GET /reporting/v1alpha1/async-operations`
* `GET /reporting/v1alpha1/report-exports-metadata`
* `GET /reporting/v1alpha1/statuses/{id}`