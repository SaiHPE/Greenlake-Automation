---
title: "HPE GreenLake Consumption Analytics Glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/glossary.md"
scraped_at: "2026-06-07T05:46:07.948683+00:00Z"
---

# HPE GreenLake Consumption Analytics Glossary

## Terms

### Chart

A visual representation, for example, a bar chart or a pie chart, defined within a report. Although visual rendering is not exposed through the public API, chart definitions are available in the report structure.

### Comparison operator

The logical operation used in a field criterion to compare field values. Supported operators include:

* `EQ` – equal to
* `NOT_EQ` – not equal to
* `STARTS_WITH` – value begins with the specified string
* `IN` – value is one of the specified values
* `NOT_IN` – value is not any of the specified values


### Date filter

A component of a report filter that scopes report execution to a specific time window. Supports two modes:

* **Relative** – Specify a named range such as `LAST_7_DAYS` or `LAST_30_DAYS` using the `relativeRange` field.
* **Absolute** – specify an explicit `startDate` and `endDate` in `YYYY-MM-DD` format. Both values must be supplied together.


When both a relative range and absolute dates are present in the same request, the relative range takes precedence.

### Field criteria

A condition applied to a specific metadata field in the dataset. Each criterion specifies a `name` (the field identifier), an `operator` (the comparison to perform), and a `values` array (the values to compare against). Multiple field criteria can be combined in the `fieldFilters` array of a report filter.

### Field filter

A type of filter applied to a specific metadata field in the dataset, for example, service category or account ID.

### Filter

A set of criteria used to limit the data in a report. Filters may include date ranges or field-based conditions.

### Report

A saved analytical configuration that defines how consumption data should be filtered, grouped, and aggregated. Reports can be retrieved and downloaded via the API.

### Report contents

The result of executing a report, returned as a downloadable CSV file. The structure depends on the report’s columns and filters.

### Report definition

The full structure of a report, including filters, selected columns, charts, and sharing settings.

### Report identifier

A lightweight representation of a report, including its ID, name, and metadata. Used primarily when listing available reports.