---
title: "POST /consumption-analytics/v2/reports/execute"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/public-reports-v2/public-reports-v2/reports/reports-v2-gen-by-def.md"
scraped_at: "2026-06-07T06:15:14.386518+00:00Z"
---

# Generate report from definition

Generates the report based on report definition provided in the request body.

Endpoint: POST /consumption-analytics/v2/reports/execute
Version: 1.0.0
Security: glcUserBearerAuth

## Request fields (application/json):

  - `columns` (array, required)
    The list of columns to include in the report. Each column specifies a field and optional aggregation function.

  - `columns.fieldName` (string, required)
    The reference name of the field to include in the report column. Example system fields: 'sys_Provider_s', 'sys_Cost_f'. Example tag and custom fields: 'ext_f8693b3b4c321cc6c7b711be5733f288_s', 'ext_b8697b3b4c391cc6c7b711be5733f333_f'.

  - `columns.aggFunction` (string)
    The aggregation function to apply to the field. Required for metric fields when data needs to be summarized.  Examples include SUM, AVG, COUNT, and so on.
    Enum: "NONE", "SUM", "COUNT", "CARDINALITY", "MIN", "MAX", "AVG"

  - `filter` (object, required)
    The filters to apply to the report, including date range and optional field-level conditions.

  - `filter.dateFilter` (object, required)
    The reporting date range, either relative or absolute.

  - `filter.dateFilter.type` (string, required)
    Defines whether the filter uses a relative date range or an absolute date range.
    Enum: "ABSOLUTE", "RELATIVE"

  - `filter.dateFilter.endDate` (string)
    The end date of the filter range. Used when the type is ABSOLUTE.

  - `filter.dateFilter.relativeRange` (string)
    A predefined time period relative to the current date. Used when the type is set to RELATIVE.
    Enum: "YESTERDAY", "LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS", "LAST_60_DAYS", "LAST_90_DAYS", "LAST_120_DAYS", "LAST_QUARTER", "LAST_YEAR", "LAST_6_MONTHS", "LAST_13_MONTHS", "CURRENT_MONTH", "PREVIOUS_MONTH", "CURRENT_QUARTER", "PREVIOUS_QUARTER", "CURRENT_YEAR", "PREVIOUS_YEAR"

  - `filter.dateFilter.startDate` (string)
    The start date of the filter range. Used when the type is ABSOLUTE.

  - `filter.fieldFilters` (array)
    An optional list of field-level filter conditions that apply to the report. Each condition specifies a field, comparison operator, and one or more values.

  - `filter.fieldFilters.name` (string, required)
    The name of the field to filter on.

  - `filter.fieldFilters.operator` (string, required)
    The comparison operator used to evaluate the field's value.
    Enum: "EQ", "NOT_EQ", "IN", "NOT_IN", "TOP", "BOTTOM", "GT", "GTE", "LT", "LTE", "BETWEEN", "NOT_BETWEEN", "STARTS_WITH", "CONTAINS", "DOES_NOT_CONTAIN", "EMPTY", "IS_EMPTY", "NOT_EMPTY", "DOES_NOT_START_WITH"

  - `filter.fieldFilters.values` (array, required)
    One or more values to be used for filtering. Can be strings, numbers, or dates, depending on the field type and operator.

## Response 200 fields (application/json):

  - `items` (array)

  - `totalCount` (integer)

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


