---
title: "PATCH /compute-ops-mgmt/v1beta3/jobs/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/jobs-v1beta3/patch_v1beta3_job_by_id.md"
scraped_at: "2026-06-07T06:15:05.607794+00:00Z"
---

# Patch a job by ID (deprecated)

Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs/id

Updates an existing job

Endpoint: PATCH /compute-ops-mgmt/v1beta3/jobs/{id}
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

## Request fields (application/merge-patch+json):

  - `state` (string)
    New state for the job (currently only Complete or Error is supported)
    Enum: "COMPLETE", "ERROR"

  - `input` (object)
    Additional input (optional) for the job

  - `input.stopOnRequest` (boolean)
    Use this optional property to cancel a server group firmware update that is in  progress with the Serial update option enabled. Updates cannot be cancelled on  servers that have started or completed the firmware update and servers that  are in a stalled state.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the job given by the system
    Example: "2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter
    Example: 9

  - `createdAt` (string, required)
    Time of job creation

  - `updatedAt` (string, required)
    Time of the last job update

  - `parentJobId` (string,null)
    The identifier of a job which triggered this job
    Example: "284f3b7a-7a17-4f0a-9b40-a51bc887c7d0"

  - `resourceUri` (string)
    URI to the job itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta3/jobs/2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `name` (string)
    Name for the job
    Example: "FirmwareUpdate.New"

  - `deleteOnComplete` (boolean)
    Automatically delete the job after it reaches the COMPLETE state.
    Example: true

  - `jobTemplateUri` (string)
    URI to the job template this job is using
    Example: "/compute-ops-mgmt/v1beta2/job-templates/fd54a96c-cabc-42e3-aee3-374a2d009dba"

  - `associatedResourceUri` (string)
    URI to the resource this job is operating against
    Example: "/compute-ops-mgmt/v1beta2/servers/744674-N19+8899744674319686"

  - `resource` (object)
    Reference to the resource this job is operating against

  - `resource.resourceUri` (string)
    Example: "/compute-ops-mgmt/v1beta2/servers/744674-N19+8899744674319686"

  - `resource.type` (string)
    Example: "servers"

  - `data` (object)
    Data needed for this job
    Example: {"state_reason_message":{"message_id":"FWI-100","message_args":["SPP 2022.12.00.00 (19 Dec 2022)"]}}

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


