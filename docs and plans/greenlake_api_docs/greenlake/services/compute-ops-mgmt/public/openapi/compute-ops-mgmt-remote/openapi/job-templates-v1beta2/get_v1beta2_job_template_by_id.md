---
title: "GET /compute-ops-mgmt/v1beta2/job-templates/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/job-templates-v1beta2/get_v1beta2_job_template_by_id.md"
scraped_at: "2026-06-07T06:14:47.284520+00:00Z"
---

# Get a job template

Note: This path operation is going to be deprecated and sunset!
- Deprecated at: Fri, 28 Feb 2025 23:59:59 GMT
- Sunset at : Tue, 1 Apr 2025 23:59:59 GMT
- This resource is being removed. The information necessary to create jobs is documented in the Jobs Definition section. There you can find all available jobs and details on how to create each job.

Retrieve details about the job template referenced by its id

Endpoint: GET /compute-ops-mgmt/v1beta2/job-templates/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique Job template identifier

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the job template given by the system

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of job template creation

  - `updatedAt` (string, required)
    Time of the last job template update

  - `resourceUri` (string)
    URI to the job template itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/job-templates/e94fea5a-115e-41b2-8ca2-406b4bf710df"

  - `name` (string)

  - `description` (string)

  - `schema` (object,null)
    JSON Schema that describes the required data for an instance of this job

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


