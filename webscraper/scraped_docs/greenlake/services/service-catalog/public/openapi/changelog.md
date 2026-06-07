---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:24.277337+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format is group changes to describe their impact on the project, as follows:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for once-stable features removed in upcoming releases.
- `Removed` for deprecated features removed in this release.
- `Fixed` for any bug fixes.
- `Security` to invite users to upgrade in case of vulnerabilities.


## 2025-Nov

### Added/Changed

Fixed inconsistent name casing in schema descriptions.

## 2025-July

### Added/Changed

The `reason` field was added.

- `GET /service-catalog/v1beta1/service-provisions/{id}`


## 2025-June

### Added

The following v1beta1 endpoints were added:

- `GET /service-catalog/v1beta1/service-offers/{id}`
- `GET /service-catalog/v1beta1/service-offers`
- `GET /service-catalog/v1beta1/service-offer-regions`
- `GET /service-catalog/v1beta1/service-offer-regions/{id}`
- `POST /service-catalog/v1beta1/service-provisions`
- `DELETE /service-catalog/v1beta1/service-provisions/{id}`
- `GET /service-catalog/v1beta1/service-provisions/{id}`
- `GET /service-catalog/v1beta1/service-provisions`
- `POST /service-catalog/v1beta1/service-provisions/{id}/retry-unprovision`
- `POST /service-catalog/v1beta1/service-provisions/{id}/retry`


## 2025-February

### Added

As part of the transition to the stable v1 version, the following endpoints were added:

- `GET service-catalog/v1/service-managers`
- `GET service-catalog/v1/service-managers/{id}`
- `GET service-catalog/v1/per-region-service-managers`
- `GET service-catalog/v1/per-region-service-managers{id}`
- `POST /service-catalog/v1/service-manager-provisions`
- `GET /service-catalog/v1/service-manager-provisions`
- `GET /service-catalog/v1/service-manager-provisions/{id}`
- `DELETE /service-catalog/v1/service-manager-provisions/{id}`


### Deprecated

As part of the transition to the stable `v1` version, the following `v1beta1` endpoints were deprecated and will no longer be available from 2025-06-30:

- `GET service-catalog/v1beta1/service-managers`
- `GET service-catalog/v1beta1/service-managers/{id}`
- `GET service-catalog/v1beta1/per-region-service-managers`
- `GET service-catalog/v1beta1/per-region-service-managers{id}`
- `POST /service-catalog/v1beta1/service-manager-provisions`
- `GET /service-catalog/v1beta1/service-manager-provisions`
- `GET /service-catalog/v1beta1/service-manager-provisions/{id}`
- `DELETE /service-catalog/v1beta1/service-manager-provisions/{id}`


## 2024-November

### Added

The initial public APIs for service registry were added with the following top-level resources:

- Service catalog
- Service offer regions
- UI management
- Service provision


## 2024-February

### Added

The initial public API was added with the following top-level resources:

- Service manager
- Service manager provision