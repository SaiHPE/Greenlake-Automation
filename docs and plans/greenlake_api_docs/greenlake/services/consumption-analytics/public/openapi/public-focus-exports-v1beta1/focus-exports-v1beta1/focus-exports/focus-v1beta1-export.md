---
title: "GET /consumption-analytics/v1beta1/focus-exports/{id}/contents"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/public-focus-exports-v1beta1/focus-exports-v1beta1/focus-exports/focus-v1beta1-export.md"
scraped_at: "2026-06-07T06:14:56.611511+00:00Z"
---

# Download FOCUS export CSV data

Executes the given FOCUS export configuration and retrieves it as a CSV file. Use the id returned by List available FOCUS export configurations as the path parameter.

Endpoint: GET /consumption-analytics/v1beta1/focus-exports/{id}/contents
Version: 1.0.0
Security: glcUserBearerAuth

## Path parameters:

  - `id` (string, required)
    The ID of the FOCUS export configuration to execute.
    Example: "7021d69d-de13-44bd-97e1-dbb05eef0759"

## Query parameters:

  - `relativeDate` (string)
    Relative date range for the export. If specified, this parameter takes precedence over startDate and endDate. Dates are mandatory: you must provide either relativeDate or the startDate/endDate pair.

  - `startDate` (string)
    Start date for an absolute export range (YYYY-MM-DD). Must be used together with endDate; otherwise a 400 Bad Request is returned.

  - `endDate` (string)
    End date for an absolute export range (YYYY-MM-DD). Must be used together with startDate; otherwise a 400 Bad Request is returned.

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


