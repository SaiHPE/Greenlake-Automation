---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:26.174320+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format is to group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2026-04-23

### Added

The support case resource was updated to include two new attributes:

* `source` — Indicates how the support case was created (`manual` or `auto`).
* `details` — Contains curated details for manually created support cases, including category, description, priority, contacts, and device information. Only present when `source` is `manual`.


New filter parameters were added for `GET wellness/v2/support-cases`:

* `source`
* `details/category`
* `details/serialNumber`
* `details/subscriptionKey`
* `details/primaryContact/email`
* `details/alternateContact/email`


## 2025-06-23

### Changed

The event resource was updated to include two new attributes: `region` and `serviceManager`.

Example:


```json
"region": "us-east",
"serviceManager": {
  "id": "0001b67f-9518-4d0f-9b17-70cec7763632",
  "resourceUri": "/wellness/v2/service-managers/0001b67f-9518-4d0f-9b17-70cec7763632"
}
```

## 2024-09-19

### Added

The following public APIs were added.

* `GET wellness/v2/events`
* `GET wellness/v2/events/{id}`
* `PATCH wellness/v2/events/{id}`
* `GET wellness/v2/support-cases`
* `GET wellness/v2/support-cases/{id}`
* `POST wellness/v2/support-cases`
* `GET wellness/v2/async-operations`
* `GET wellness/v2/async-operations/{id}`


### Deprecated

The following public APIs were deprecated.

* `GET wellness/v2beta2/events`
* `GET wellness/v2beta2/events/{id}`
* `PATCH wellness/v2beta2/events/{id}`
* `GET wellness/v2beta2/support-cases`
* `GET wellness/v2beta2/support-cases/{id}`
* `POST wellness/v2beta2/support-cases`
* `GET wellness/v2beta2/async-operations`
* `GET wellness/v2beta2/async-operations/{id}`


## 2024-06-12

### Added

The following public APIs were added.

* `GET wellness/v2beta2/support-cases`
* `POST wellness/v2beta2/support-cases`
* `GET wellness/v2beta2/support-cases/{id}`
* `GET wellness/v2beta2/async-operations`
* `GET wellness/v2beta2/async-operations/{id}`


### Changed

The following public APIs were updated with new response object and query parameters.

* `GET wellness/v2beta2/events`
* `GET wellness/v2beta2/events/{id}`


## 2024-02-22

Introduced version v2beta2 for the Wellness API.

### Added

The following public APIs were added.

* `PATCH wellness/v2beta2/events/{id}`


### Changed

The following public APIs were updated with new response object and supported filters.

* `GET wellness/v2beta2/events`
* `GET wellness/v2beta2/events/{id}`


### Deprecated

The following public APIs will be deprecated.

* `GET wellness/v2beta1/events`
* `GET wellness/v2beta1/events/{id}`


## 2023-10-23

Introduced version v2beta1 for WellnessAPI.

### Added

The following public APIs were added.

* `GET wellness/v2beta1/events`
* `GET wellness/v2beta1/events/{id}`