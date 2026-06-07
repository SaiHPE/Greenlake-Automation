---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:24.656826+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

Group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2025-July

### Added

The following endpoint was added:

* `DELETE /subscriptions/v2beta1/subscriptions/bulk`


### Changed

* Updated the `GET /subscriptions/v1/subscriptions` and `GET /subscriptions/v1/subscriptions/{id}` API endpoints to include new response fields: `tierDescription`, `quote`, `po`, and `resellerPo`.


## 2025-April

### Changed

* Updated the `GET /subscriptions/v1/subscriptions` documentation to list the filterable properties and added additional examples.


## 2025-March

### Changed

* The `POST /subscriptions/v1/subscriptions` and `PATCH /subscriptions/v1/subscriptions` API endpoints  support the new `dry-run` query parameter


## 2025-January

### Added

As part of the transition to the stable `v1` version, the following endpoints were added:

* `POST /subscriptions/v1/subscriptions`
* `GET /subscriptions/v1/async-operations/{id}`
* `GET /subscriptions/v1/subscriptions`
* `PATCH /subscriptions/v1/subscriptions`
* `GET /subscriptions/v1/subscriptions/{id}`
* `GET /subscriptions/v1/auto-subscription-settings`
* `GET /subscriptions/v1/auto-subscription-settings/{resource_id}`
* `PATCH /subscriptions/v1/auto-subscription-settings/{resource_id}`


### Deprecated

As part of the transition to the stable `v1` version, the following `v1beta1` and `v1alpha1` endpoints were deprecated and will no longer be available from 2025-05-05:

* `POST /subscriptions/v1beta1/subscriptions`
* `GET /subscriptions/v1beta1/async-operations/{id}`
* `GET /subscriptions/v1alpha1/subscriptions`
* `PATCH /subscriptions/v1beta1/subscriptions`
* `GET /subscriptions/v1beta1/subscriptions`
* `GET /subscriptions/v1beta1/subscriptions/{id}`
* `GET /subscriptions/v1alpha1/auto-subscription-settings`
* `GET /subscriptions/v1alpha1/auto-subscription-settings/{resource_id}`
* `PATCH /subscriptions/v1alpha1/auto-subscription-settings/{resource_id}`


## 2024-October

### Changed

* The rate limits for the `GET /subscriptions/v1beta1/subscriptions` and `GET /subscriptions/v1beta1/async-operations/{id}` APIs have increased.


## 2024-September

### Added

The following public API was added:

* `PATCH /subscriptions/v1beta1/subscriptions`


## 2024-May

### Added

The following public APIs were added:

* `GET /subscriptions/v1beta1/subscriptions`
* `GET /subscriptions/v1beta1/subscriptions/{id}`
* `GET /subscriptions/v1alpha1/auto-subscription-settings`
* `GET /subscriptions/v1alpha1/auto-subscription-settings/{resource_id}`
* `PATCH /subscriptions/v1alpha1/auto-subscription-settings/{resource_id}`


## 2023-November

### Added

The initial public APIs were added:

* `POST /subscriptions/v1beta1/subscriptions`
* `GET /subscriptions/v1beta1/async-operations/{id}`
* `GET /subscriptions/v1alpha1/subscriptions`