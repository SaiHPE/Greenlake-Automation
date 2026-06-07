---
title: "GET /audit-log/v2beta1/logs/{id}/details"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/audit-trail-external-v2beta1/fetch-audit-logs/getauditlogdetails.md"
scraped_at: "2026-06-07T06:13:54.831708+00:00Z"
---

# Get a specific audit log details.

Endpoint: GET /audit-log/v2beta1/logs/{id}/details
Version: v2beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Provide the ID of the audit log record to fetch the audit log details.

## Response 200 fields (application/json):

  - `id` (string, required)
    Audit log ID

  - `type` (string, required)
    Resource type

  - `header` (string, required)
    Heading summarizing the audit log details.

  - `body` (array, required)
    Array of action or detail strings describing the audit event.

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 403 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 404 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)
    Additional detailed information about the error.

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


