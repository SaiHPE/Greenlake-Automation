---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/changelog.md"
scraped_at: "2026-06-07T06:13:31.772124+00:00Z"
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


## 2026-February

### Changed

* The `POST /devices/v2beta1/devices` endpoint now supports the addition of a device along with location information and user contact information.
* The `PATCH /devices/v2beta1/devices` endpoint now supports additional operations for updating location information and user contact information.


## 2025-November

### Changed

* The response for the `GET /devices/v1/devices` and `GET /devices/v1/devices/{id}` endpoints now includes the following additional subscription fields: `key`, `tier`, `startDate`, and `endDate`.


## 2025-September

### Changed

* The response for the `GET /devices/v1/devices` and `GET /devices/v1/devices/{id}` endpoints now includes the following additional location fields: `city`, `state`, `country`, `latitude`, `longitude`, `postalCode`, `locationName`, `streetAddress`, and `locationSource`.


## 2025-July

### Changed

* The response for the `GET /devices/v1/devices` and `GET /devices/v1/devices/{id}` endpoints now includes three new fields: `deviceName`, `secondaryName`, and `dedicatedPlatformWorkspace`.
* The rate limit for `PATCH /devices/v2beta1/devices` and `PATCH /devices/v1/devices` has been raised to 20 requests per minute per workspace.


## 2025-June

### Changed

* A new response field, `assignedState`, was added to the response of the `GET /devices/v1/devices` and `GET /devices/v1/devices/{id}` API endpoints.


## 2025-March

### Added

The following API endpoints were added

* `POST /devices/v2beta1/devices`
* `PATCH /devices/v2beta1/devices`


### Changed

* The `POST /devices/v1/devices` and `PATCH /devices/v1/devices` API endpoints support the new `dry-run` query parameter


## 2025-January

### Added

As part of the transition to the stable `v1` version, the following endpoints were added:

* `POST /devices/v1/devices`
* `PATCH /devices/v1/devices`
* `GET /devices/v1/devices`
* `GET /devices/v1/async-operations/{id}`
* `GET /devices/v1/devices/{id}`


### Deprecated

As part of the transition to the stable `v1` version, the following `v1beta1` endpoints were deprecated and will no longer be available from 2025-05-05:

* `POST /devices/v1beta1/devices`
* `PATCH /devices/v1beta1/devices`
* `GET /devices/v1beta1/devices`
* `GET /devices/v1beta1/async-operations/{id}`
* `GET /devices/v1beta1/devices/{id}`


## 2024-October

### Changed

* The rate limits for the `POST /devices/v1beta1/devices`, `GET /devices/v1beta1/devices` and `GET /devices/v1beta1/async-operations/{id}` APIs have increased.


## 2024-May

### Added

The following public APIs were added:

* `GET /devices/v1beta1/devices/{id}`


### Changed

* The `GET /devices/v1beta1/devices` API now supports filtering supports IN, NOT along with exiting operators. Filter based on Tags is also supported.


## 2023-November

### Added

The initial public APIs were added:

* `POST /devices/v1beta1/devices`
* `PATCH /devices/v1beta1/devices`
* `GET /devices/v1beta1/devices`
* `GET /devices/v1beta1/async-operations/{id}`