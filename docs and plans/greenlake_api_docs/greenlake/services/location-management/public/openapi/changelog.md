---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:22.462891+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format groups changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## May 2026

### Changed

* Updated documentation for location update flows to clarify partial update behavior.
* Added documented response fields for coordinates (`lat`, `lng`), location `tags`, and tag `id`.
* Updated array schema definitions for address, contact, and tag collections.


### Fixed

* Updated endpoint error responses to include applicable `403` and `409` codes.


## February 2026

### Fixed

* Fixed address type fields in `server.CreateAddressNBRequest` and `server.UpdateAddressNBRequest` to be string enums with appropriate values and made the type field required in update requests.
* Updated address operation descriptions to clarify type restrictions: only "shipping_receiving" addresses can be added, and address types cannot be changed during updates.


## January 2026

### Changed

* Revised the API response structure for the reverse geocode endpoint (`GET /locations/v1/address/revgeocode`) to return a single location object instead of a paginated response.


## November 2025

### Added

Added a new endpoint to check the Locations service status. The new API endpoint is:

* `GET /locations/v1/locations/status`


### Removed

Removed the deprecated `v1beta1` endpoints as they are no longer available.

## October 2025

### Changed

* Added the required fields **First Name** and **Last Name** to the upload file in the **Create locations using CSV file** (`POST /locations/v1/locations/locations-csv-upload`) API.


## March 2025

### Added

Added a new endpoint to bulk upload locations by uploading a CSV file. The new API endpoint is:

* `POST /locations/v1/locations/locations-csv-upload`
* `POST /locations/v1/locations/async-operation/{id}`


Added the equality operator (`eq`) to the filter query parameter in the `GET /locations/v1/locations` endpoint. The equality operator (`eq`) can be used with city and country properties. For example:

* `GET https://global.api.greenlake.hpe.com/locations/v1/locations?filter=city eq 'cityName'`
* `GET https://global.api.greenlake.hpe.com/locations/v1/locations?filter=country eq 'countryName'`


## November 2024

### Added

Added a new API to reverse geocode a location. The new API endpoint is:

* `GET /locations/v1/address/revgeocode`


Further, as part of the transition to the stable `v1` version, the following endpoints were added:

* `GET /locations/v1/locations`
* `GET /locations/v1/locations/{id}`
* `GET /locations/v1/locations/tags`
* `GET /locations/v1/locations/tags/{id}`
* `POST /locations/v1/locations`
* `PATCH /locations/v1/locations/{id}`
* `DELETE /locations/v1/locations/{id}`
* `PATCH /locations/v1/locations/update/{id}`
* `PATCH /locations/v1/locations/tags`


### Deprecated

As part of the transition to the stable `v1` version, the following `v1beta1` endpoints were deprecated and will no longer be available from 2024-11-04:

* `GET /locations/v1beta1/locations`
* `GET /locations/v1beta1/locations/{id}`
* `GET /locations/v1beta1/locations/tags`
* `GET /locations/v1beta1/locations/tags/{id}`
* `POST /locations/v1beta1/locations`
* `PATCH /locations/v1beta1/locations/{id}`
* `DELETE /locations/v1beta1/locations/{id}`
* `PATCH /locations/v1beta1/locations/update/{id}`
* `PATCH /locations/v1beta1/locations/tags`


### Changed

* The contact type "Support" option is deprecated in the create location `POST /locations/v1/locations` API.
* You can assign a contact within or outside of the HPE GreenLake platform. Provide the name 'NONGLP' for a contact outside the HPE GreenLake platform.


## July 2024

Three APIs added that help you retrieve location tag information and manage location tags.

### Added

The following public APIs were added.

* `GET /locations/v1beta1/locations/tags`
* `GET /locations/v1beta1/locations/tags/{id}`
* `PATCH /locations/v1beta1/locations/tags`


## 2024-11-22

The initial release of the HPE GreenLake for Locations APIs.

### Added

The following public APIs were added.

* `GET /locations/v1beta1/locations`
* `GET /locations/v1beta1/locations/{id}`
* `POST /locations/v1beta1/locations`
* `PATCH /locations/v1beta1/locations/{id}`
* `DELETE /locations/v1beta1/locations/{id}`