---
title: "GET /reporting/v1/statuses/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-status/getreportingstatusbyid.md"
scraped_at: "2026-06-07T06:16:41.180321+00:00Z"
---

# Get Report Status by ID

Retrieve the status of a specific report by passing the report status ID.

Endpoint: GET /reporting/v1/statuses/{id}
Version: v1
Security: BearerAuth

## Path parameters:

  - `id` (string, required)
    The report status identifier.
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier of the report

  - `type` (string, required)
    Type of the resource

  - `status` (string, required)
    The current status of the report generation stage, indicating whether the stage is, for example, in progress or completed.

  - `stage` (string, required)
    The current stage in the report generation process.

  - `message` (string, required)
    A short description of the current progress. This field may be empty.

  - `reportType` (string, required)
    The type of report.

  - `userName` (string, required)
    The username of whoever created the report.

  - `recipientEmailId` (string, required)
    The email address the report was sent to.

  - `startTime` (string, required)
    The date and time the report request was initiated.

  - `statusTimestamp` (string, required)
    The date and time the report request was initiated.

  - `name` (string)

  - `description` (string)

  - `resourceUri` (string)
    URI to the report status resource itself.

  - `isExpired` (string)
    A boolean that declares if the report has expired or not.

  - `reportDownloadUrl` (string)
    The URL at which you can view the report.

  - `createdAt` (string)
    The date and time the report request was initiated.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_NOT_FOUND_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Invalid characters in 'id'. Only alphanumeric and hyphens are allowed."

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_FORBIDDEN_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Not authorized to get report status of id = \"1fa85f64-5434-9980-b3fc-3c963f44fgh9\""

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 404

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_NOT_FOUND_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Report status not found. No reports match the given criteria."

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 500

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_INTERNAL_SERVER_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Failed to fetch status"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"


