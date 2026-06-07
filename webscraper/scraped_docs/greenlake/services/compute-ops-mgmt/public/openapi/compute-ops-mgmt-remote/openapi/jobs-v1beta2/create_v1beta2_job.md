---
title: "POST /compute-ops-mgmt/v1beta2/jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/jobs-v1beta2/create_v1beta2_job.md"
scraped_at: "2026-06-07T06:14:48.070115+00:00Z"
---

# Create a job (deprecated)

Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 31 Jan 2025 23:59:59 GMT
- Sunset at : Mon, 3 Mar 2025 23:59:59 GMT
- Successor version: compute-ops-mgmt/v1/jobs

Create a job for a given resource. A job is a multi-step task performed by Compute Ops Manager.

This table summarizes the jobs and their template IDs. For more information about each job template, expand the Job
Definitions section and click on Overview to get started.

| Name                                 | Description                                         | Resource Type      | Template ID                          |
| ------------------------------------ | --------------------------------------------------  | ------------------ | ------------------------------------ |
| Server Power Off                     | Power off a server                                  | compute-ops/server | d0c13b58-748c-461f-9a61-c0c5c71f1bb4 |
| Server Power On                      | Power on a server                                   | compute-ops/server | 0cbb2377-1834-488d-840c-d5bf788c34fb |
| Server Restart                       | Restart a server                                    | compute-ops/server | 30110551-cad6-4069-95b8-dbce9bbd8525 |
| Server Cold Boot                     | Cold boot a server                                  | compute-ops/server | aacfb3e0-6575-4d4f-a711-1ee1ae768407 |
| Server Firmware Update               | Update firmware on a server                         | compute-ops/server | fd54a96c-cabc-42e3-aee3-374a2d009dba |
| Server iLO Firmware Update           | Update iLO component firmware on a server           | compute-ops/server | 94caa4ef-9ff8-4805-9e97-18a09e673b66 |
| Group Firmware Update                | Update firmware on servers in a group               | compute-ops/group  | 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 |
| Group Firmware Compliance            | Calculate firmware compliance of servers in a group | compute-ops/group  | 23b8ba2a-6c46-4223-b028-919382c7dcac |
| Group Apply Internal Storage Settings | Apply internal storage settings on servers in a group | compute-ops/group | 54095626-3911-4fea-9741-816e2531994e |
| Group Apply Server Setting           | Apply server setting on a group                     | compute-ops/group  | beff07ce-f36d-4699-9ac3-f872dcd63133 |
| Collect Server Inventory             | Collect complete or filtered server inventory       | compute-ops/server | d6595f1b-84e6-4587-ade5-656e2a5ea20d |
| Collect Server Network Connectivity  | Collect server adapter port to switch port mappings | compute-ops/server | b21ca9e2-8a1b-11ee-b9d1-0242ac120002 |
| Group iLO Settings Compliance        | Calculate ilo settings compliance of servers in a group | compute-ops/group  | a55c8b26-3c57-4044-a4ee-1d0e3c108286 |

Endpoint: POST /compute-ops-mgmt/v1beta2/jobs
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `jobTemplateUri` (string, required)
    Identifier of the job template for this job. Supports ID(aacfb3e0-6575-4d4f-a711-1ee1ae768407) in addition to URI(/compute-ops-mgmt/v1beta2/job-templates/aacfb3e0-6575-4d4f-a711-1ee1ae768407)

  - `resourceUri` (string, required)
    A resource URI that the job will operate on
    Example: "/compute-ops-mgmt/v1beta2/servers/abc+123"

  - `data` (object)
    Any additional data required by this job

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the job given by the system

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of job creation

  - `updatedAt` (string, required)
    Time of the last job update

  - `parentJobId` (string,null)
    The identifier of a job which triggered this job

  - `resourceUri` (string)
    URI to the job itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/jobs/2500759c-b7dd-4c68-ab7e-6b644bcf4b9c"

  - `name` (string)
    Name for the job

  - `jobTemplateUri` (string)

  - `associatedResourceUri` (string)

  - `resource` (object)
    Reference to the resource this job is operating against

  - `resource.resourceUri` (string)

  - `resource.type` (string)

  - `data` (object)
    Data needed for this job

  - `results` (object)
    Results from job execution

  - `state` (string)
    The current state of a job, indicating whether a job is waiting, running, or terminal
    Enum: "PENDING", "APPROVAL_PENDING", "RUNNING", "STALLED", "ERROR", "COMPLETE"

  - `status` (string)

  - `statusDetails` (object,null)
    Additional information about the jobs status

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


