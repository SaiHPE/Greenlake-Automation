---
title: "GET /private-cloud-business/v1beta1/configuration-analysis-reports/{reportId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/configuration-analysis-reports/listconfiganalysisreportbyid.md"
scraped_at: "2026-06-07T06:15:38.179090+00:00Z"
---

# Returns a config analysis rules execution results for the provided reportId.

Returns config analysis rules execution report identified by 'reportId'
parameter.

Endpoint: GET /private-cloud-business/v1beta1/configuration-analysis-reports/{reportId}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `reportId` (string, required)
    Unique identifier of a Config Analysis Report.

## Response 200 fields (application/json):

  - `id` (string, required)
    CA report id

  - `type` (string, required)
    The type of resource.

  - `createdAt` (string)
    Timestamp when the config analysis rules execution result is created

  - `createdBy` (string)
    Source type of config analysis rules execution

  - `nextScheduledRunAt` (string)
    Timestamp when the config analysis rules execution is next scheduled

  - `results` (object)
    Execution results data in json format

  - `runStartedAt` (string)
    Timestamp when the config analysis rules execution is started

  - `runType` (string)
    run type of config analysis rules execution (Manual/Scheduled)

  - `systemId` (string)
    UUID of System

  - `systemName` (string)
    Name of System

  - `totalFailed` (integer)
    Number of failed rules in config analysis execution

  - `totalPassed` (integer)
    Number of rules passed in config analysis execution

  - `totalWarning` (integer)
    Number of warnings in config analysis execution

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


