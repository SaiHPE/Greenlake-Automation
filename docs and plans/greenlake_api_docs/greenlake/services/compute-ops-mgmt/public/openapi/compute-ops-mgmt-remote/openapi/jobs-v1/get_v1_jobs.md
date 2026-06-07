---
title: "GET /compute-ops-mgmt/v1/jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/jobs-v1/get_v1_jobs.md"
scraped_at: "2026-06-07T06:14:47.673587+00:00Z"
---

# List all jobs

Retrieve the list of jobs

Endpoint: GET /compute-ops-mgmt/v1/jobs
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

Jobs can be filtered by:
- id
- type
- parentJobId
- createdAt
- updatedAt
- deleteOnComplete
- cancellable
- name
- jobParams
- state
- resultCode
- status
- statusDetails
- generation
- results
- resource/id
- resource/type
- jobTemplate 

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

  - `offset` (integer)
    Zero-based resource offset

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

  - `items` (array)

  - `items.id` (string)
    Primary identifier for the job given by the system
    Example: "2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `items.parentJobId` (string,null,string,null)
    The identifier of a job which triggered this job
    Example: "284f3b7a-7a17-4f0a-9b40-a51bc887c7d0"

  - `items.type` (string)
    Type of the resource

  - `items.resourceUri` (string)
    URI to the job itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/jobs/2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `items.name` (string)
    Name for the job
    Example: "FirmwareUpdate.New"

  - `items.generation` (integer)
    Monotonically increasing update counter
    Example: 9

  - `items.deleteOnComplete` (boolean)
    Automatically delete the job after it reaches the COMPLETE state.
    Example: true

  - `items.createdAt` (string)
    Time of job creation

  - `items.updatedAt` (string)
    Time of the last job update

  - `items.jobTemplate` (string)
    ID of the job template this job is using
    Example: "fd54a96c-cabc-42e3-aee3-374a2d009dba"

  - `items.resource` (object)
    Reference to the associated resource this job is operating against

  - `items.resource.id` (string)
    Example: "744674-N19+8899744674319686"

  - `items.resource.type` (string)
    Example: "compute-ops-mgmt/server"

  - `items.jobParams` (object)
    Parameters used to define this job

  - `items.results` (object)
    Results from job execution

  - `items.state` (string)
    The current state of a job, indicating whether a job is waiting, running, or terminal
    Enum: "PENDING", "APPROVAL_PENDING", "RUNNING", "STALLED", "ERROR", "COMPLETE"

  - `items.resultCode` (any)

  - `items.status` (string)
    Status message about the job

  - `items.statusDetails` (object,null,object,null)
    Additional information about the job's status

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


