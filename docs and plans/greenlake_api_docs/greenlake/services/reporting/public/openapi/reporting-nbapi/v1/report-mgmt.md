---
title: "HPE GreenLake for Reporting"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt.md"
scraped_at: "2026-06-07T06:13:43.043482+00:00Z"
---

# HPE GreenLake for Reporting

The HPE GreenLake for Reporting service provides a collection of RESTful APIs for generating reports, retrieving supported columns and filters, monitoring asynchronous operations, and querying the status of reports.

Version: v1
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### BearerAuth

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake for Reporting](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt.yaml)

## Report Status

### Get statuses of all the reports belonging to a workspace

 - [GET /reporting/v1/statuses](https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-status/getreportingstatuses.md): This API is designed to fetch the status of all reports for a specific workspace. Only reports belonging to the workspace ID and username are returned. This API supports pagination, allowing you to use offset and limit parameters.

### Get Report Status by ID

 - [GET /reporting/v1/statuses/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-status/getreportingstatusbyid.md): Retrieve the status of a specific report by passing the report status ID.

## Report exports

### Report exports

 - [POST /reporting/v1/report-exports](https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-exports/paths/~1reporting~1v1~1report-exports/post.md): Use this API to asynchronously generate reports across supported report types. After you submit your report generation requests, they are processed in the background. Once complete, you receive a unique URI in the response header.  NOTE: You need to specify the columns you want to return in the report, and apply filter criteria to refine the data returned. To find out what columns and filter criteria are available, call the Report Exports Metadata API.

### Report exports metadata

 - [GET /reporting/v1/report-exports-metadata](https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/report-exports/paths/~1reporting~1v1~1report-exports-metadata/get.md): This API is a support tool that assists with generating a report. Use it to find the supported columns, filter criteria, and values for a report type.  In a response, the API returns:

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

## Async operations

### Asynchronous operation details

 - [GET /reporting/v1/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/reporting/public/openapi/reporting-nbapi/v1/report-mgmt/async-operations/paths/~1reporting~1v1~1async-operations~1%7Bid%7D/get.md): Retrieve information about asynchronous operations within the reporting service. Provide the unique identifier of the operation in the parameter to monitor the progress of asynchronous tasks.  This API returns the following attributes:

  - status—Indicates the current status of the asynchronous task.
  - startedAt—Specifies the timestamp when the operation was initiated.
  - endedAt—Indicates the timestamp when the operation was completed.
  - logMessages—Provides a list of progress updates for the asynchronous operation.
  - progressPercent—Represents the progress of the operation as a percentage value ranging from 0 to 100.
  - sourceResourceUri—References the source URI that triggered the asynchronous task.
  - results—The results array provides a link to /reporting/v1/statuses/{id} to get the complete details of the report status.

