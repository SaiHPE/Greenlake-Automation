---
title: "GET /reporting/v1/statuses"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-status/getreportingstatuses.md"
scraped_at: "2026-06-07T06:16:41.128384+00:00Z"
---

# Get statuses of all the reports belonging to a workspace

This API is designed to fetch the status of all reports for a specific workspace. Only reports belonging to the workspace ID and username are returned. This API supports pagination, allowing you to use offset and limit parameters.

Endpoint: GET /reporting/v1/statuses
Version: v1
Security: BearerAuth

## Query parameters:

  - `filter` (string, required)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.

For example, the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

  - `sort` (string)
    The order in which to return the resources in the collection.The value of the sort query parameter is a comma separated list of sort expressions. Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc (descending).The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, and so on. If a direction indicator is omitted the default direction is ascending.

  - `limit` (integer)
    The maximum number of reports to return.
    Example: 50

  - `offset` (integer)
    Zero-based resource offset to start the response from.
    Example: 20

## Response 200 fields (application/json):

  - `count` (integer)
    Number of items returned

  - `limit` (integer)
    The maximum number of reports to return.

  - `offset` (integer)
    Zero-based resource offset

  - `items` (array)

  - `items.id` (string, required)
    Unique identifier of the report

  - `items.type` (string, required)
    Type of the resource

  - `items.status` (string, required)
    The current status of the report generation stage, indicating whether the report stage is, for example, in progress or completed.

  - `items.stage` (string, required)
    The current stage in the report generation process.

  - `items.message` (string, required)
    Short description of the progress, which may be empty.

  - `items.reportType` (string, required)
    The type of report.

  - `items.userName` (string, required)
    The username of whoever created the report.

  - `items.recipientEmailId` (string, required)
    The email address the report was sent to.

  - `items.startTime` (string, required)
    The date and time the report request was initiated.

  - `items.statusTimestamp` (string, required)
    The date and time the report status last changed.

  - `items.name` (string)
    The display name of the report.

  - `items.description` (string)
    A description of the report supplied by a user.

  - `items.resourceUri` (string)
    URI to the report metadata resource itself.

  - `items.isExpired` (string)
    A boolean that declares if the report has expired or not.

  - `items.reportDownloadUrl` (string)
    The URL at which you can view the report.

  - `items.createdAt` (string)
    The date and time the report was created.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 401

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "HPE_GL_REPORTING_AUTHORIZATION_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Not authorized to get report statuses\""

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


