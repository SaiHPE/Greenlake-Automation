---
title: "POST /compute-ops-mgmt/v1/jobs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/jobs-v1/create_v1_job.md"
scraped_at: "2026-06-07T06:14:47.707287+00:00Z"
---

# Create a job

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
| Server External Storage Details      | Collect external storage details for a server       | compute-ops/server | 9310319e-7b7f-41ba-8b24-8b34eed1ca62 |
| Server Firmware Download             | Download firmware on a server                       | compute-ops/server | 0683ada8-1a89-49dd-bf04-6df715b708a6 |
| Server Set UID Indicator On          | Turn on the UID indicator light on a server         | compute-ops/server | a46b210a-b0c7-4223-ab43-c4c1e77e680c |
| Server Set UID Indicator Off         | Turn off the UID indicator light on a server        | compute-ops/server | fd837434-a2f2-4bc8-b1b4-ec068bd036aa |
| Server Enable Maintenance Mode       | Enable maintenance mode for a server                | compute-ops/server | 4eb92af1-1ce4-4cb0-8581-fb5a7dcdbf2b |
| Server Disable Maintenance Mode      | Disable maintenance mode for a server               | compute-ops/server | 2798720f-b090-427d-b210-e48d33ce2f27 |
| Appliance Software Update            | Update OneView appliance                            | compute-ops/oneview-appliance | 1c4ac4be-8eeb-49f2-a86a-fd8c9182616c |
| Synchronize firmware baseline        | Synchronize firmware baseline of a vcenter          | compute-ops/external-service | 0fe73adb-9d52-4f00-9540-6ec82f265d82 |
| Remove vCenter                       | Remove a vCenter                                    | compute-ops/external-service | 3f06fd6b-dfb1-4bad-bd04-939951797e97 |
| Group Firmware Update                | Update firmware on servers in a group               | compute-ops/group  | 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 |
| Group Firmware Compliance            | Calculate firmware compliance of servers in a group | compute-ops/group  | 23b8ba2a-6c46-4223-b028-919382c7dcac |
| Group Appliance Update               | Update OneView appliances in a group                | compute-ops/group  | f69f553a-5004-4a08-9283-5b60abd9eb4a |
| Group Apply Internal Storage Settings | Apply internal storage settings on servers in a group | compute-ops/group | 54095626-3911-4fea-9741-816e2531994e |
| Group Apply Server Setting           | Apply server setting on a group                     | compute-ops/group  | beff07ce-f36d-4699-9ac3-f872dcd63133 |
| Group Apply External Storage Settings | Apply external storage settings on servers in a group | compute-ops/group  | fcb79270-5954-42e9-9374-6a065b6d494a |
| Group External Storage Compliance    | Calculate external storage compliance of servers in a group | compute-ops/group | 7177aa6a-e8f8-4e9b-ae31-e01dafcc81df |
| Group Firmware Download              | Download firmware on servers in a group             | compute-ops/group  | a17a7aa9-4540-4c21-bbf2-31af4ff65e98 |
| Collect Server Inventory             | Collect complete or filtered server inventory       | compute-ops/server | d6595f1b-84e6-4587-ade5-656e2a5ea20d |
| Collect Server Network Connectivity  | Collect server adapter port to switch port mappings | compute-ops/server | b21ca9e2-8a1b-11ee-b9d1-0242ac120002 |
| Group Operating System Installation  | Install operating system on servers in a group      | compute-ops/group  | e2952628-2629-4088-93db-91742304ef0c |
| Collect Server log                   | Collect server log                                  | compute-ops/server | 2d744494-22d4-4d61-8c65-647ccadeb6b6 |

Endpoint: POST /compute-ops-mgmt/v1/jobs
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

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

## Request fields (application/json):

  - `jobTemplate` (string, required)
    ID of the job template for this job.
    Example: "aacfb3e0-6575-4d4f-a711-1ee1ae768407"

  - `resourceId` (string, required)
    Id of the resource to run this job on
    Example: "744674-N19+8899744674319686"

  - `resourceType` (string, required)
    Type of the resource to run this job on
    Example: "compute-ops-mgmt/server"

  - `jobParams` (object)
    Parameters needed to define this job (based on the job schema)

## Response 201 fields (application/json):

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


