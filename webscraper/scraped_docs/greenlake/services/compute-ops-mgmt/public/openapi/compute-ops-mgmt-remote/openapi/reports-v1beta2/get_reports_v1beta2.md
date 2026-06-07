---
title: "GET /compute-ops-mgmt/v1beta2/reports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/reports-v1beta2/get_reports_v1beta2.md"
scraped_at: "2026-06-07T06:14:49.519391+00:00Z"
---

# List all reports

Retrieve a paginated collection of report metadata resources.  Currently, only the latest report of each
type is retained.

Endpoint: GET /compute-ops-mgmt/v1beta2/reports
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Reports can be filtered by:
- createdAt
- generation
- id
- reportDataEndAt
- reportDataStartAt
- reportType
- resourceUri
- type
- updatedAt
- status

The following examples are not an exhaustive list of all possible filtering options.

  - `sort` (string)
    The order in which to return the resources in the collection.

The value of the sort query parameter is a comma separated list of sort expressions. 
Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc 
(descending).

The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, 
and so on. If a direciton indicator is omitted the default direction is ascending.

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

  - `items` (array, required)
    Array of resources in the page of the collection.

  - `items.id` (string)
    Primary identifier for the report metadata resource given by the system.
    Example: "843023bd-9412-46c2-8ac2-a3691f657fdb"

  - `items.name` (string)
    The display name of the report.
    Example: "Carbon Footprint Report (All Servers)"

  - `items.type` (string)
    The type of the resource.

  - `items.generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `items.createdAt` (string)
    Time of report resource creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.updatedAt` (string)
    Time of the last update to the report resource.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.resourceUri` (string)
    URI to the report metadata resource itself (i.e. a self link).
    Example: "/compute-ops-mgmt/v1beta2/reports/843023bd-9412-46c2-8ac2-a3691f657fdb"

  - `items.reportDataUri` (string)
    URI to the data for the report.
    Example: "/compute-ops-mgmt/v1beta2/reports/843023bd-9412-46c2-8ac2-a3691f657fdb/data"

  - `items.reportType` (any)

  - `items.reportTypeDisplayName` (string)
    The display name for the type of the report.
    Example: "Carbon Footprint Report"

  - `items.deviceIds` (any)

  - `items.reportDataStartAt` (any)

  - `items.reportDataEndAt` (any)

  - `items.status` (string)
    The current status of report generation, indicating whether a report is in progress, completed, or failed
    Enum: "IN_PROGRESS", "COMPLETED", "FAILED"

  - `items.reportMetadata` (object)
    Metadata of the report.

  - `items.reportMetadata.associatedResourceName` (string)
    Name of the resource for which report generation was requested
    Example: "Demo group"

  - `items.reportMetadata.associatedResourceUri` (string)
    URI of the resource for which report generation was requested
    Example: "/compute-ops-mgmt/v1/groups/420372b6-af2e-464d-970d-e9339abfc74f"

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


