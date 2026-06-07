---
title: "GET /compute-ops-mgmt/v1beta3/jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta3/get_v1beta3_jobs.md"
scraped_at: "2026-06-07T06:15:05.689387+00:00Z"
---

# List all jobs (deprecated)

Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs

Retrieve the list of jobs

Endpoint: GET /compute-ops-mgmt/v1beta3/jobs
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

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

  - `items` (array, required)

  - `items.id` (string, required)
    Primary identifier for the job given by the system
    Example: "2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `items.type` (string, required)
    Type of the resource

  - `items.generation` (integer, required)
    Monotonically increasing update counter
    Example: 9

  - `items.createdAt` (string, required)
    Time of job creation

  - `items.updatedAt` (string, required)
    Time of the last job update

  - `items.parentJobId` (string,null,string,null)
    The identifier of a job which triggered this job
    Example: "284f3b7a-7a17-4f0a-9b40-a51bc887c7d0"

  - `items.resourceUri` (string)
    URI to the job itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta3/jobs/2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `items.name` (string)
    Name for the job
    Example: "FirmwareUpdate.New"

  - `items.deleteOnComplete` (boolean)
    Automatically delete the job after it reaches the COMPLETE state.
    Example: true

  - `items.jobTemplateUri` (string)
    URI to the job template this job is using
    Example: "/compute-ops-mgmt/v1beta2/job-templates/fd54a96c-cabc-42e3-aee3-374a2d009dba"

  - `items.associatedResourceUri` (string)
    URI to the resource this job is operating against
    Example: "/compute-ops-mgmt/v1beta2/servers/744674-N19+8899744674319686"

  - `items.resource` (object)
    Reference to the resource this job is operating against

  - `items.resource.resourceUri` (string)
    Example: "/compute-ops-mgmt/v1beta2/servers/744674-N19+8899744674319686"

  - `items.resource.type` (string)
    Example: "servers"

  - `items.data` (object)
    Data needed for this job
    Example: {"state_reason_message":{"message_id":"FWI-100","message_args":["SPP 2022.12.00.00 (19 Dec 2022)"]}}

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

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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


