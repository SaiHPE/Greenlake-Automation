---
title: "GET /consumption-analytics/v1/reports/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/public-reports-v1/public-reports-v1/reports/reports-v1-get-by-id.md"
scraped_at: "2026-06-07T06:14:57.274846+00:00Z"
---

# Retrieve a report definition

Fetches the details of a specific report definition by its ID. Use the id returned by List available report definitions as the path parameter.

Endpoint: GET /consumption-analytics/v1/reports/{id}
Version: 1.0.0
Security: glcUserBearerAuth

## Path parameters:

  - `id` (string, required)
    The ID of the report definition.
    Example: "7021d69d-de13-44bd-97e1-dbb05eef0759"

## Response 200 fields (application/json):

  - `charts` (array)
    A list of charts defined within the report, each describing a specific data visualization.

  - `charts.definition` (object, required)
    Contains the full configuration for the chart, including fields like metric, group by, and series. Used to define how the data is visualized.

  - `charts.definition.dualAxis` (boolean)
    If true, displays the chart with two Y-axes, typically used for combining metrics of different units or scales.

  - `charts.definition.excludeOther` (boolean)
    If true, excludes the 'Other' category from the chart display. Required for pie and grouped bar-style charts.

  - `charts.definition.group` (string)
    Optional field used to group data points in the chart. Required for GROUPED_BAR and HEATMAP charts.

  - `charts.definition.maxGroups` (integer)
    The maximum number of groups to display in the chart. Excess groups are collapsed into 'Other' if excludeOther is false.

  - `charts.definition.metric` (string)
    The name of a numeric field used as the chart metric. Required for all chart types except MULTI_METRICS_LINE, which uses metricDefinitions.

  - `charts.definition.metricAggFunction` (string)
    The aggregation function applied to the metric field. Examples include SUM, AVG, COUNT, and so on.
    Enum: "NONE", "SUM", "COUNT", "CARDINALITY", "MIN", "MAX", "AVG"

  - `charts.definition.metricDefinitions` (array)
    A list of metric + aggregation combinations for charts that support multiple metrics, such as MULTI_METRICS_LINE.

  - `charts.definition.metricDefinitions.metric` (string, required)
    A valid numeric field to be plotted in the chart. Must have valueType == INT or valueType == FLOAT.

  - `charts.definition.metricDefinitions.metricAggFunction` (string, required)
    The aggregation function applied to the metric field. Determines how the data points are summarized.
    Enum: "NONE", "SUM", "COUNT", "CARDINALITY", "MIN", "MAX", "AVG"

  - `charts.definition.orientation` (string)
    Orientation of the chart. Required for bar-based charts.
    Enum: "VERTICAL", "HORIZONTAL"

  - `charts.definition.series` (string)
    The field used to represent the series or X-axis. Typically a time-based field for line charts or a string field for bar and pie charts.

  - `charts.title` (string, required)
    The title of the chart, shown above the chart in reports. Helps users identify the chart's purpose.

  - `charts.type` (string, required)
    Defines the type of chart to render, such as bar, line, pie, or stacked bar. Determines which configuration fields are displayed.
    Enum: "PIE", "LINE", "BAR", "STACKED_BAR", "HEATMAP", "GROUPED_BAR", "MULTI_METRICS_LINE", "MULTI_LINE", "TIME_SERIES_BAR", "TIME_SERIES_STACKED_BAR"

  - `charts.description` (string)
    A short description that appears as a tooltip on the info icon in the report. Optional.

  - `charts.id` (string)
    The unique identifier of the chart. Assigned automatically upon creation.

  - `columns` (array)
    The list of fields (columns) included in the report table.
    Example: [{"aggFunction":"SUM","fieldName":"cost_f","formatting":{"placesAfterDecimal":2},"group":false,"sort":"DESC"}]

  - `columns.fieldName` (string, required)
    The name of the field to include in the report column. Fields can be dimensions, measures, or tags.        Common suffixes help identify type: _d for date, _f for float, _i for integer, _t for timestamp.
    Example: "cost_f"

  - `columns.aggFunction` (string)
    The aggregation function to apply to the field. Required for metric fields when data needs to be summarized.        Examples include SUM, AVG, COUNT, and so on.
    Enum: "NONE", "SUM", "COUNT", "CARDINALITY", "MIN", "MAX", "AVG"

  - `columns.formatting` (object)
    Optional formatting settings for the column, such as the number of decimal places to display.
    Example: {"placesAfterDecimal":2}

  - `columns.formatting.placesAfterDecimal` (integer)
    Specifies how many digits to display after the decimal point for floating-point values.         Useful for aligning report outputs with expected precision (for example, showing 2 decimal places for currency).
    Example: 2

  - `columns.group` (boolean)
    Indicates whether the field is used as a grouping dimension in the report.        Reports may include multiple group columns to organize and summarize data across multiple dimensions.

  - `columns.pivot` (string)
    Defines the time-based pivoting for this column, allowing data to be rearranged across intervals such as day, month, or year.
    Enum: "DAY", "WEEK", "MONTH", "QUARTER", "YEAR"

  - `columns.sort` (string)
    Optional sort order for the column values. Affects the order in which rows appear in the report.
    Enum: "ASC", "DESC"

  - `created` (object)
    Information about the user who created the report and when it was created.

  - `created.email` (string)
    The email address of the user who performed the action.

  - `created.id` (string)
    The unique identifier of the user who performed the action.

  - `created.name` (string)
    The display name of the user who performed the action.

  - `created.time` (string)
    The date and time when the action occurred.

  - `description` (string)
    A short summary of the report’s purpose or contents.
    Example: "Tracks monthly consumption grouped by service and region."

  - `filter` (object)
    The set of filters applied to the report data, including both date and field-level filters.

  - `filter.dateFilter` (object, required)
    The reporting date range, either relative or absolute.

  - `filter.dateFilter.type` (string, required)
    Defines whether the filter uses a relative date range or an absolute date range.
    Enum: "ABSOLUTE", "RELATIVE"

  - `filter.dateFilter.endDate` (string)
    The end date of the filter range. Used when the type is ABSOLUTE.

  - `filter.dateFilter.relativeRange` (string)
    A predefined time period relative to the current date.         Used when the type is set to RELATIVE.
    Enum: "YESTERDAY", "LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS", "LAST_60_DAYS", "LAST_90_DAYS", "LAST_120_DAYS", "LAST_QUARTER", "LAST_YEAR", "LAST_6_MONTHS", "LAST_13_MONTHS", "CURRENT_MONTH", "PREVIOUS_MONTH", "CURRENT_QUARTER", "PREVIOUS_QUARTER", "CURRENT_YEAR", "PREVIOUS_YEAR"

  - `filter.dateFilter.startDate` (string)
    The start date of the filter range. Used when the type is ABSOLUTE.

  - `filter.fieldFilters` (array, required)
    A list of field-level filter conditions that apply to the report.        Each condition specifies a field, comparison operator, and one or more values.

  - `filter.fieldFilters.name` (string, required)
    The name of the field to filter on.

  - `filter.fieldFilters.operator` (string, required)
    The comparison operator used to evaluate the field’s value.
    Enum: "EQ", "NOT_EQ", "IN", "NOT_IN", "TOP", "BOTTOM", "GT", "GTE", "LT", "LTE", "BETWEEN", "NOT_BETWEEN", "STARTS_WITH", "CONTAINS", "DOES_NOT_CONTAIN", "EMPTY", "IS_EMPTY", "NOT_EMPTY", "DOES_NOT_START_WITH"

  - `filter.fieldFilters.values` (array, required)
    One or more values to be used for filtering.         Can be strings, numbers, or dates, depending on the field type and operator.

  - `forecastCfg` (object)
    Configuration for forecasted data in the report, if applicable.     This includes settings for how forecasted values are calculated and displayed.

  - `forecastCfg.enableForecast` (boolean)

  - `forecastCfg.forecastPeriod` (integer)

  - `forecastCfg.interval` (string)
    Enum: "DAY", "MONTH", "QUARTER", "YEAR"

  - `id` (string)
    The unique identifier of the report.
    Example: "7021d69d-de13-44bd-97e1-dbb05eef0759"

  - `lastUpdated` (object)
    Information about the user who last modified the report and the timestamp.

  - `name` (string)
    The name of the report as shown in the UI.
    Example: "Monthly Usage Breakdown"

  - `owner` (boolean)
    Indicates whether the currently authenticated user is the report’s owner.

  - `pivot` (boolean)
    Indicates whether the report output is pivoted by a time-based dimension (for example, by month).

  - `shared` (boolean)

  - `sharing` (object)
    Controls whether the report is private (only visible to the owner) or public (visible to all tenant users).

  - `sharing.type` (string, required)
    The sharing mode of the report. If set to PUBLIC, the report is accessible to other users in the same tenant.        If set to PRIVATE, only the report owner can view and edit it.
    Enum: "PUBLIC", "PRIVATE"

## Response 400 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "860a9caa39ffa07effc84d6da9173236"

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_CA_NAME_TOO_LONG"

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 400

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid yearMonth format, should be yyyyMM."

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Example: "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "limit"

  - `errorDetails.issues.description` (string)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Must be a numeric value which is 0 or greater."

  - `errorDetails.type` (string, required)
    The part of the request with an issue.
    Example: "hpe.greenlake.bad_request"

  - `flowContextId` (string)

  - `status` (integer)

## Response 401 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "860a9caa39ffa07effc84d6da9173236"

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_CA_NAME_TOO_LONG"

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 400

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid yearMonth format, should be yyyyMM."

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Example: "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "limit"

  - `errorDetails.issues.description` (string)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Must be a numeric value which is 0 or greater."

  - `errorDetails.type` (string, required)
    The part of the request with an issue.
    Example: "hpe.greenlake.bad_request"

  - `flowContextId` (string)

  - `status` (integer)

## Response 403 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "860a9caa39ffa07effc84d6da9173236"

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_CA_NAME_TOO_LONG"

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 400

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid yearMonth format, should be yyyyMM."

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Example: "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "limit"

  - `errorDetails.issues.description` (string)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Must be a numeric value which is 0 or greater."

  - `errorDetails.type` (string, required)
    The part of the request with an issue.
    Example: "hpe.greenlake.bad_request"

  - `flowContextId` (string)

  - `status` (integer)

## Response 404 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "860a9caa39ffa07effc84d6da9173236"

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_CA_NAME_TOO_LONG"

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 400

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid yearMonth format, should be yyyyMM."

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Example: "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "limit"

  - `errorDetails.issues.description` (string)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Must be a numeric value which is 0 or greater."

  - `errorDetails.type` (string, required)
    The part of the request with an issue.
    Example: "hpe.greenlake.bad_request"

  - `flowContextId` (string)

  - `status` (integer)

## Response 500 fields (application/json):

  - `debugId` (string, required)
    A unique identifier for the instance of this error. This can be used to help with troubleshooting.
    Example: "860a9caa39ffa07effc84d6da9173236"

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_CA_NAME_TOO_LONG"

  - `httpStatusCode` (integer, required)
    The HTTP equivalent status code.
    Example: 400

  - `message` (string, required)
    A user-friendly error message
    Example: "Invalid yearMonth format, should be yyyyMM."

  - `errorDetails` (array)
    Additional detailed information about the error

  - `errorDetails.issues` (array, required)
    Array of bad request issues.

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.
    Example: "query.parameter"

  - `errorDetails.issues.subject` (string, required)
    The specific issue key.
    Example: "limit"

  - `errorDetails.issues.description` (string)
    An elaborate description of issue. This can be used by developers to understand how the failure can be addressed.
    Example: "Must be a numeric value which is 0 or greater."

  - `errorDetails.type` (string, required)
    The part of the request with an issue.
    Example: "hpe.greenlake.bad_request"

  - `flowContextId` (string)

  - `status` (integer)


