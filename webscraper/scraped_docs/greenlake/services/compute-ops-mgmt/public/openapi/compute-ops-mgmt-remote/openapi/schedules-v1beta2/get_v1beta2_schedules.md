---
title: "GET /compute-ops-mgmt/v1beta2/schedules"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/schedules-v1beta2/get_v1beta2_schedules.md"
scraped_at: "2026-06-07T06:14:49.653627+00:00Z"
---

# List all schedules

Retrieve a paginated collection of schedule resources.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta2/schedules
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

Schedules can be filtered by:
- createdAt
- generation
- historyUri
- id
- nextStartAt
- operation/body
- operation/headers
- operation/method
- operation/query
- operation/timeoutInSec
- operation/type
- operation/uri
- resourceUri
- schedule/intervalInSec
- schedule/startAt
- type
- updatedAt

The following examples are not an exhaustive list of all possible filtering options.

  - `sort` (string)
    The order in which to return the resources in the collection.

The value of the sort query parameter is a comma separated list of sort expressions. 
Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc 
(descending).

The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, 
and so on. If a direciton indicator is omitted the default direction is ascending.

  - `select` (string)
    Limit the properties of the resource returned in a successful response.  When applied to
write operations, select controls only the properties that are returned, not which
properties are operated on. All properties are returned if the select parameter is omitted.

The value of the select query parameter is a comma separated list of properties to include
in the response. Nested properties use / as a separator, e.g. select=interfaces/name
selects the name property within an interfaces object.

For operations that return paginated collections, select operates on the resources in
the collection. The pagination properties like count and items are always included even
when select is specified.

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
    Array of schedule resources in the page of the collection.

  - `items.id` (string, required)
    Primary identifier for the schedule resource given by the system.
    Example: "37f66ae4-20a1-48f1-b552-b515457639ca"

  - `items.type` (string, required)
    The type of the resource.

  - `items.name` (string, required)
    The display name of the schedule. Note that multiple schedules can have the same name, so schedules should likely always also be displayed with their start time.

  - `items.schedule` (object, required)
    When to execute the scheduled operation.

  - `items.schedule.startAt` (string, required)
    For a one-time schedule, the time the schedule should be executed. For a fixed interval schedule, the time the schedule should first be executed. The start must be within a year of the current time.
    Example: "2022-02-14T04:35:00.000000+00:00"

  - `items.schedule.interval` (string,null,string,null)
    How long between successive executions for a recurring schedule, or null for a one-time schedule. PT15M < interval < P1Y
    Example: "P7D"

  - `items.operation` (any, required)

  - `items.generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `items.createdAt` (string)
    Time of schedule resource creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.updatedAt` (string)
    Time of the last update to the schedule resource.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `items.resourceUri` (string)
    URI to the schedule resource itself (i.e. a self link).
    Example: "/compute-ops-mgmt/v1beta2/schedules/37f66ae4-20a1-48f1-b552-b515457639ca"

  - `items.historyUri` (string)
    URI of collection of history entries for the schedule.
    Example: "/compute-ops-mgmt/v1beta2/schedules/37f66ae4-20a1-48f1-b552-b515457639ca/history"

  - `items.description` (string,null,string,null)
    A longer description of the schedule provided by the client.

  - `items.purpose` (string,null,string,null)
    A machine-readable category for the schedule.

  - `items.associatedResourceUri` (string,null,string,null)
    Another compute-ops resource the schedule is associated with. If the resource associated with a schedule is deleted, the schedule is also deleted.
    Example: "/compute-ops/v1beta2/groups/cad23390-5209-43d1-b38d-bc96258b47e5"

  - `items.nextStartAt` (string,null,string,null)
    The time the operation is scheduled to execute next, or null if no future executions are scheduled.
    Example: "2022-02-14T04:35:00.000000+00:00"

  - `items.lastRun` (any)

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


