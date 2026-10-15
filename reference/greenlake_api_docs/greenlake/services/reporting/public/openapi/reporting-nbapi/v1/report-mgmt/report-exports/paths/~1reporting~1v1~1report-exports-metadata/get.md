---
title: "GET /reporting/v1/report-exports-metadata"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-exports/paths/~1reporting~1v1~1report-exports-metadata/get.md"
scraped_at: "2026-06-07T06:16:41.301077+00:00Z"
---

# Report exports metadata

This API is a support tool that assists with generating a report. Use it to find the supported columns, filter criteria, and values for a report type.  In a response, the API returns:

  - columns&mdash;An array containing the supported columns.
  - filterCriteria&mdash;An array comprising of filter names and their corresponding data types.
  - supportedOperators&mdash;A collection of supported operators assisting you in selecting the correct operator to use in a filter attribute. The following operators are supported:
    - EQ&mdash;Checks if a field is equal to a value.
    - NE&mdash;Checks if a field is not equal to a value.
    - LT&mdash;Checks if a field is less than a value.
    - LE&mdash;Checks if a field is less than or equal to a value.
    - GT&mdash;Checks if a field is greater than a value.
    - GE&mdash;Checks if a field is greater than or equals to a value.
    - IN&mdash;Checks if a value is in a list.

Endpoint: GET /reporting/v1/report-exports-metadata
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

For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

  - `select` (string, required)
    The select query parameter is used to limit the properties returned for a resource. The value of the select query parameter is a comma-separated list of properties.
    Example: {"equals":{"summary":"select with equality check","description":"Return activities where a property equals a value.\n","value":"select=name"}}

  - `sort` (string, required)
    The order in which to return the resources in the collection. The value of the sort query parameter is a comma separated list of sort expressions. Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc (descending). The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, and so on. If a direction indicator is omitted, the default direction is ascending.

  - `limit` (integer)
    The maximum number of reports to return.
    Example: 10

  - `offset` (integer)
    Zero-based resource offset to start the response from.
    Example: 20

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    The unique identifier of the report.

  - `items.kind` (string, required)

  - `items.type` (string, required)
    The type of the resource.

  - `items.name` (string, required)
    The name of the report.

  - `items.columns` (array, required)

  - `items.columns.displayName` (string, required)
    The display name of the column.

  - `items.columns.name` (string, required)
    The internal name of the column.

  - `items.columns.dataType` (string, required)
    The classification of data accepted by the column.

  - `items.filterCriteria` (array, required)

  - `items.filterCriteria.name` (string, required)
    The name of the filter criteria.

  - `items.filterCriteria.supportedOperators` (array, required)
    The classification of the logical operator supported by the filter criteria.

  - `count` (integer, required)
    Number of items returned

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request.

  - `offset` (integer, required)
    Zero-based resource offset to start the response from

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error
    Example: "GLP_GL_REPORTING_INVALID_ATTRIBUTE_ERROR"

  - `message` (string, required)
    User-friendly error message
    Example: "Invalid attribute: type1"

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
    Example: "Not authorized to retrieve report export metadata"

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
    Example: "Incorrect permission to retrieve report export metadata for report type \"subscriptions\""

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
    Example: "Invalid type \"subscription1\""

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
    Example: "Failed to retrieve report exports metadata"

  - `debugId` (string, required)
    Unique identifier for the instance of this error
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"


