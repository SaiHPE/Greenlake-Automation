---
title: "GET /consumption-analytics/v1/reports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/public-reports-v1/public-reports-v1/reports/reports-v1-list.md"
scraped_at: "2026-06-07T06:14:57.066306+00:00Z"
---

# List available report definitions

List the report definitions that are available to the caller.

Endpoint: GET /consumption-analytics/v1/reports
Version: 1.0.0
Security: glcUserBearerAuth

## Response 200 fields (application/json):

  - `created` (object)
    Captures metadata about a user action, such as report creation or last update.    Used to display audit information including who made the change and when it occurred.

  - `created.email` (string)
    The email address of the user who performed the action.

  - `created.id` (string)
    The unique identifier of the user who performed the action.

  - `created.name` (string)
    The display name of the user who performed the action.

  - `created.time` (string)
    The date and time when the action occurred.

  - `description` (string)

  - `id` (string)

  - `lastUpdated` (object)
    Captures metadata about a user action, such as report creation or last update.    Used to display audit information including who made the change and when it occurred.

  - `name` (string)

  - `owner` (boolean)

  - `shared` (boolean)

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


