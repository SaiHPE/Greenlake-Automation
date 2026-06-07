---
title: "GET /consumption-analytics/v2/reports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v2/public-reports-v2/reports/reports-v2-list.md"
scraped_at: "2026-06-07T06:15:14.802701+00:00Z"
---

# List report definitions

List the report definitions that are available.

Endpoint: GET /consumption-analytics/v2/reports
Version: 1.0.0
Security: glcUserBearerAuth

## Query parameters:

  - `limit` (integer)
    The maximum number of items to return.

  - `offset` (integer)
    The number of items to skip before starting to collect the result set.

## Response 200 fields (application/json):

  - `count` (integer)

  - `items` (array)

  - `items.createdAt` (string)

  - `items.description` (string)

  - `items.generation` (string)

  - `items.id` (string)

  - `items.name` (string)

  - `items.owner` (boolean)

  - `items.shared` (boolean)

  - `items.type` (string)

  - `items.updatedAt` (string)

  - `offset` (integer)

  - `total` (integer)

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


