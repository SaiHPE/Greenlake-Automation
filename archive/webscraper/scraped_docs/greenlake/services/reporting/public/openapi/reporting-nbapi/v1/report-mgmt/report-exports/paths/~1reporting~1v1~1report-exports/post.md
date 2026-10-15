---
title: "POST /reporting/v1/report-exports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-exports/paths/~1reporting~1v1~1report-exports/post.md"
scraped_at: "2026-06-07T06:16:41.183769+00:00Z"
---

# Report exports

Use this API to asynchronously generate reports across supported report types. After you submit your report generation requests, they are processed in the background. Once complete, you receive a unique URI in the response header.  NOTE: You need to specify the columns you want to return in the report, and apply filter criteria to refine the data returned. To find out what columns and filter criteria are available, call the Report Exports Metadata API.

Endpoint: POST /reporting/v1/report-exports
Version: v1
Security: BearerAuth

## Request fields (application/json):

  - `name` (string)
    The name of the report.

  - `description` (string)
    A short summary of the report.

  - `kind` (string)

  - `type` (string)
    The type of the resource.

  - `definition` (object)

  - `definition.queryElements` (object)

  - `definition.queryElements.columns` (array)
    An array containing the supported columns.

  - `definition.queryElements.filterCriteria` (object)
    An array comprising of filter names and their corresponding data types.

  - `definition.queryElements.filterCriteria.key` (string)

  - `definition.queryElements.filterCriteria.operator` (any)
    Enum: "EQ", "NE", "GT", "GE", "LT", "LE", "IN"

  - `definition.queryElements.filterCriteria.value` (string)

  - `definition.enrollment` (object)

  - `definition.enrollment.delivery` (object)

  - `definition.enrollment.delivery.format` (any)
    The file type of the report.
    Enum: "CSV", "TXT", "PDF", "EXCEL"

  - `definition.enrollment.delivery.email` (object)

  - `definition.enrollment.delivery.email.subject` (string)
    The subject line of the email.

  - `definition.enrollment.delivery.email.recipients` (array)
    The email address of the recipients of the report.

## Response 202 fields (application/json):

  - `id` (string)
    UUID of generated resource

  - `name` (string)
    The name of the resource

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "GLP_GL_REPORTING_INVALID_ATTRIBUTE_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Invalid column name \"SUBSCRIPTION_KEY1\""

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_AUTHORIZATION_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Not authorized to initiate report export"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 403

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_FORBIDDEN_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Incorrect permissions to initiate report export for report type \"subscriptions\""

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
    Example: "Invalid datasource \"subscription1\""

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
    Example: "Failed to initiate report exports"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"


