---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:19.556567+00:00Z"
---

# Changelog

All notable changes to the public Consumption Analytics APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format follows semantic versioning principles, grouping changes by their impact:

* `Added` – New features or endpoints introduced.
* `Changed` – Modifications to existing functionality.
* `Deprecated` – Stable features that will be removed in a future release.
* `Removed` – Deprecated features that have now been removed.
* `Fixed` – Bug fixes or behavioral corrections.
* `Security` – Important updates related to vulnerabilities or compliance.


## 2026-05-13

### Changed

* **All v1 Reports endpoints** – Operation IDs have been renamed for consistency with the broader API naming scheme. The REST paths, request and response shapes, and all observable behaviour are unchanged. Updated operation IDs:
  * `public-reports-list` → `reports-v1-list`
  * `public-reports-get` → `reports-v1-get-by-id`
  * `public-reports-download-get` → `reports-v1-export-csv`
* **OpenAPI tag grouping** – The tag name for v1 Reports endpoints has been updated to a shorter, consumer-friendly name. `Public Reports v1` → `Reports`. This affects grouping in API documentation viewers but has no effect on the REST interface.
* **All v2 Reports endpoints** – Operation IDs have been renamed for consistency with the broader API naming scheme. The REST paths, request and response shapes, and all observable behaviour are unchanged. Updated operation IDs:
  * `public-reports-list-v2` → `reports-v2-list`
  * `public-reports-post-v2` → `reports-v2-gen-by-def`
  * `public-reports-execute-v2` → `reports-v2-gen-by-id`
* **OpenAPI tag grouping** – The tag name for v2 Reports endpoints has been updated to a shorter, consumer-friendly name. `Public Reports v2` → `Reports`. This affects grouping in API documentation viewers but has no effect on the REST interface.
* **All v1beta1 FOCUS Exports endpoints** – Operation IDs have been renamed for consistency with the broader API naming scheme. The REST paths, request and response shapes, and all observable behaviour are unchanged. Updated operation IDs:
  * `public-focus-exports-list` → `focus-v1beta1-list`
  * `public-focus-exports-get` → `focus-v1beta1-get`
  * `public-focus-exports-download-get` → `focus-v1beta1-export`
* **OpenAPI tag grouping** – The tag name for FOCUS Exports endpoints has been updated to a shorter, consumer-friendly name. `Public FOCUS Exports v1beta1` → `FOCUS Exports`. This affects grouping in API documentation viewers but has no effect on the REST interface.


## 2026-05-12

### Changed

* **`POST /consumption-analytics/v2/reports/execute`** – The request body now uses a fully public model (`PublicReportExecuteRequest`) instead of an internal framework type. The schema is unchanged for callers but is now formally documented as part of the public API contract. The request supports:
  * `filter` – A `PublicReportFilter` containing:
    * `dateFilter` – Required. A `PublicReportDateFilter` with a `type` of `RELATIVE` (supply `relativeRange`) or `ABSOLUTE` (supply `startDate` and `endDate`).
    * `fieldFilters` – Optional array of `PublicReportFieldCriteria`, each with a `name`, `operator`, and `values` array.
  * `columns` – Array of `PublicReportColumn` entries, each with a `fieldName` and optional `aggFunction`.
* **`POST /consumption-analytics/v2/reports/{id}/execute`** – The request body schema has been renamed from `PublicReportRequestV2` to `PublicReportDateFilterRequest`. The shape and accepted fields are unchanged; only the schema component name in the OpenAPI spec is different.


### Added

* **OpenAPI spec for FOCUS Exports v1beta1 published** – The OpenAPI reference specification for the `GET /consumption-analytics/v1beta1/focus-exports`, `GET /consumption-analytics/v1beta1/focus-exports/{id}`, and `GET /consumption-analytics/v1beta1/focus-exports/{id}/contents` endpoints is now available in the API reference portal.
* **`GET /consumption-analytics/v1beta1/focus-exports/{id}/contents`** – The API specification now includes structured error response examples for five distinct `400 Bad Request` scenarios:
  * `missingAllDates` – No date parameters were provided.
  * `missingPair` – Only one of `startDate` or `endDate` was provided.
  * `invalidOrImpossibleDate` – A date value is in the wrong format or is impossible (for example, `2025-02-30`).
  * `invalidRange` – `startDate` is after `endDate`.
  * `invalidRelativeDate` – The `relativeDate` parameter contains an unrecognised value.
* **`POST /consumption-analytics/v2/reports/execute`** – A request body example is now included in the API specification, showing a report definition with a relative date range filter.
* **`POST /consumption-analytics/v2/reports/{id}/execute`** – Request body examples are now included in the API specification, showing both relative date range and absolute date range request formats.


## 2026-03-23

### Added

* **`GET /consumption-analytics/v1/reports/{id}/contents`** – Added a new `include-currency-symbol` boolean query parameter (default: `false`). When set to `true`, cost fields in the exported CSV will include the currency symbol alongside the numeric value.


## 2026-03-09

### Changed

* **`POST /consumption-analytics/v2/reports/{id}/execute`** – Decimal number columns (fields with a `_f` suffix) now default to **10 decimal places** when the caller has not explicitly set `formatting.placesAfterDecimal`. Previously, the analytics service applied its own default of 4 decimal places, which was unsuitable for raw data consumers requiring full numeric precision. Explicitly provided values are always honoured; non-numeric columns are unaffected.


### Fixed

* **`POST /consumption-analytics/v2/reports/{id}/execute`** – Report ID validation now correctly accepts UUIDs case-insensitively and with or without hyphens. Previously, some valid UUID representations were rejected at the API boundary even though they identified the same report.
* **`POST /consumption-analytics/v2/reports/{id}/execute`** – The request body is now validated as non-null at the API boundary. Submitting a request with no body now returns a `400 Bad Request` response instead of propagating a null value to the underlying service.


## 2026-02-12

### Fixed

* **`POST /consumption-analytics/v2/reports/{id}/execute`** – Report ID path parameter validation is now case-insensitive and accepts UUIDs both with and without hyphens (e.g. `7021d69dde1344bd97e1dbb05eef0759` is now treated as equivalent to `7021d69d-de13-44bd-97e1-dbb05eef0759`).


## 2026-02-09

### Fixed

* **`GET /consumption-analytics/v1beta1/focus-exports/{id}/contents`** – Requesting an export using an unrecognised or invalid export configuration ID now correctly returns `404 Not Found`. Previously the endpoint returned `204 No Content` in this case, making it impossible for callers to distinguish between a successful empty export and a missing resource.


## 2026-02-03

### Changed

* **`POST /consumption-analytics/v2/reports/execute`** and **`POST /consumption-analytics/v2/reports/{id}/execute`** – Error responses now conform to the GLP error response standard. Validation failures return structured `errorDetails` alongside the top-level `errorCode` and `message` fields, giving callers machine-readable detail about which field or constraint caused the error.


## 2025-12-11

### Added

* **`POST /consumption-analytics/v2/reports/{id}/execute`** – Added support for date-range filtering. Callers can now scope the report execution to a specific time window using either:
  * `relativeDate` – a relative range identifier (e.g. `last_30_days`). Takes precedence over the absolute range parameters when both are supplied.
  * `startDate` + `endDate` – an absolute date range in `YYYY-MM-DD` format. Both parameters must be provided together; supplying only one returns a `400 Bad Request`.


## 2025-12-05

### Changed

* **`GET /consumption-analytics/v2/reports`** – The list endpoint now supports **pagination** via two optional query parameters:
  * `limit` – Maximum number of items to return (default: `10`).
  * `offset` – Number of items to skip before returning results (default: `0`).


## 2025-12-04

### Added

Initial release of the **v2 Reports API**.

* Base path: `/consumption-analytics/v2/reports`
* The following endpoints were introduced:
  * `POST /reports/execute` – Generates report metadata from a full report definition provided in the request body, without requiring a pre-saved report ID.
  * `GET /reports` – Lists report definitions available to the caller (see pagination added 2025-12-05).
  * `POST /reports/{id}/execute` – Executes a saved report definition by ID and returns the results as a JSON table.


Initial release of the **v1beta1 FOCUS Exports API**.

* Base path: `/consumption-analytics/v1beta1/focus-exports`
* The following endpoints were introduced:
  * `GET /focus-exports` – Lists the FOCUS export configurations available to the caller.
  * `GET /focus-exports/{id}` – Retrieves the full definition of a specific FOCUS export configuration.
  * `GET /focus-exports/{id}/contents` – Executes the given FOCUS export configuration and returns the result as a FOCUS-compliant CSV file. Requires date-range parameters: either `relativeDate` or the `startDate` + `endDate` pair.


## 2025-03-21

### Added

Initial release of the public Consumption Analytics Reports API v1.

* Base path: `/consumption-analytics/v1/reports`
* The following endpoints were introduced:
  * `GET /reports` – Lists the reports available to the authenticated user.
  * `GET /reports/{id}` – Retrieves the full definition of a specific report.
  * `GET /reports/{id}/contents` – Executes a report and returns the result as a downloadable CSV file.