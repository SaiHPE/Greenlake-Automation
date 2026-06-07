---
title: "PATCH /compute-ops-mgmt/v1/jobs/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/jobs-v1/patch_v1_job_by_id.md"
scraped_at: "2026-06-07T06:14:47.681683+00:00Z"
---

# Patch a job by ID

Updates an existing job

Endpoint: PATCH /compute-ops-mgmt/v1/jobs/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Job identifier

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Query parameters:

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

## Request fields (application/merge-patch+json):

  - `state` (string)
    New state for the job (currently only Complete or Error is supported)
    Enum: "COMPLETE", "ERROR"

  - `input` (object)
    Additional input (optional) for the job

  - `input.stopOnRequest` (boolean)
    Use this optional property to cancel a server group firmware update that is in  progress with the Serial update option enabled. Updates cannot be cancelled on  servers that have started or completed the firmware update and servers that  are in a stalled state.

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier for the job given by the system
    Example: "2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `parentJobId` (string,null)
    The identifier of a job which triggered this job
    Example: "284f3b7a-7a17-4f0a-9b40-a51bc887c7d0"

  - `type` (string)
    Type of the resource

  - `resourceUri` (string)
    URI to the job itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/jobs/2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `name` (string)
    Name for the job
    Example: "FirmwareUpdate.New"

  - `generation` (integer)
    Monotonically increasing update counter
    Example: 9

  - `deleteOnComplete` (boolean)
    Automatically delete the job after it reaches the COMPLETE state.
    Example: true

  - `createdAt` (string)
    Time of job creation

  - `updatedAt` (string)
    Time of the last job update

  - `jobTemplate` (string)
    ID of the job template this job is using
    Example: "fd54a96c-cabc-42e3-aee3-374a2d009dba"

  - `resource` (object)
    Reference to the associated resource this job is operating against

  - `resource.id` (string)
    Example: "744674-N19+8899744674319686"

  - `resource.type` (string)
    Example: "compute-ops-mgmt/server"

  - `jobParams` (object)
    Parameters used to define this job

  - `results` (object)
    Results from job execution

  - `state` (string)
    The current state of a job, indicating whether a job is waiting, running, or terminal
    Enum: "PENDING", "APPROVAL_PENDING", "RUNNING", "STALLED", "ERROR", "COMPLETE"

  - `resultCode` (any)

  - `status` (string)
    Status message about the job

  - `statusDetails` (object,null)
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

## Response 404 fields (application/json):

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

## Response 412 fields (application/json):

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

## Response 415 fields (application/json):

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


