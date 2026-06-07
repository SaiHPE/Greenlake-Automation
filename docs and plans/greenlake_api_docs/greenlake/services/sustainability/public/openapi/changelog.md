---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:25.226162+00:00Z"
---

# Changelog

All notable changes to the endpoints are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format is group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2024-02-22

Introduced the HPE Sustainability Insight Center APIs with version v1beta1.

### Added

The following public endpoints were added.

* `/sustainability-insight-ctr/v1beta1/usage-by-entity`
* `/sustainability-insight-ctr/v1beta1/usage-totals`
* `/sustainability-insight-ctr/v1beta1/usage-series`


## 2024-06-19

Added a few new APIs to v1beta1.

### Added

The following public endpoints were added.

* `GET /sustainability-insight-ctr/v1beta1/coefficients`
* `POST /sustainability-insight-ctr/v1beta1/coefficients`
* `GET /sustainability-insight-ctr/v1beta1/coefficients/{id}`
* `GET /sustainability-insight-ctr/v1beta1/ingests`
* `POST /sustainability-insight-ctr/v1beta1/ingests`
* `GET /sustainability-insight-ctr/v1beta1/ingests/{id}`
* `GET /sustainability-insight-ctr/v1beta1/datasources`
* `GET /sustainability-insight-ctr/v1beta1/datasources/{id}`


## 2024-11-12

Added support for tag filtering and currency codes, and made other small modifications to existing endpoints.

## 2024-12-XX

Added the public cloud feature.

### Added

The following public cloud endpoints were added.

* `/sustainability-insight-ctr/v1beta1/cloud-usage-by-entity`
* `/sustainability-insight-ctr/v1beta1/cloud-usage-totals`
* `/sustainability-insight-ctr/v1beta1/cloud-usage-series`