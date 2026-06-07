---
title: "GET /private-cloud-business/v1beta1/configuration-analysis-reports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/configuration-analysis-reports/listlatestconfiganalysisreport.md"
scraped_at: "2026-06-07T06:15:36.297579+00:00Z"
---

# Returns a list of config analysis rules execution results.

Returns the list of latest config analysis reports for all systems.
It also accepts 'filter' query parameter where if 'systemId' is provided as 'filter',
it returns the latest config analysis report for that system.

Endpoint: GET /private-cloud-business/v1beta1/configuration-analysis-reports
Version: 1.1.0
Security: bearer

## Query parameters:

  - `filter` (string)
    Filter criteria - e.g. systemId eq c0930136-5317-5647-8d92-87ca3984c5f9

  - `sort` (string)
    The resource property to sort by followed by the response order.
Response order can be either “asc” (ascending) or “desc” (descending)
    Example: "totalFailed desc"

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    CA report id

  - `items.type` (string, required)
    The type of resource.

  - `items.createdAt` (string)
    Timestamp when the config analysis rules execution result is created

  - `items.createdBy` (string)
    Source type of config analysis rules execution

  - `items.nextScheduledRunAt` (string)
    Timestamp when the config analysis rules execution is next scheduled

  - `items.results` (object)
    Execution results data in json format

  - `items.runStartedAt` (string)
    Timestamp when the config analysis rules execution is started

  - `items.runType` (string)
    run type of config analysis rules execution (Manual/Scheduled)

  - `items.systemId` (string)
    UUID of System

  - `items.systemName` (string)
    Name of System

  - `items.totalFailed` (integer)
    Number of failed rules in config analysis execution

  - `items.totalPassed` (integer)
    Number of rules passed in config analysis execution

  - `items.totalWarning` (integer)
    Number of warnings in config analysis execution

  - `count` (integer, required)

  - `offset` (number)

  - `total` (integer)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


