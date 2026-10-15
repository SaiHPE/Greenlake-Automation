---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/changelog.md"
scraped_at: "2026-06-07T06:13:34.111996+00:00Z"
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


## 2024-09-12

### Changed

The API servers host names were changed to adopt the standard regional
endpoint host names in the form: `<region>.api.greenlake.hpe.com`.

## 2024-May

### Added

The following public APIs was added:

* POST v1beta1/virtual-machines/{id}/update-hardware


### Fixed

* Fixed the URI for listing `hypervisor-folders` with missing `hypervisor-managers/{hypervisor-id}` in the path.


## 2024-March

### Added

The initial public API was added with the following top-level private cloud resources:

* virtual-machines
* datastores


The initial public API was added with the following top-level public cloud resources:

* csp-machine-images
* csp-machine-instances
* csp-machine-instance-types