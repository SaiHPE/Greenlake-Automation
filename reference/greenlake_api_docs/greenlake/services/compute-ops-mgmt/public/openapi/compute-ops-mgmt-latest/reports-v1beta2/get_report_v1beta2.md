---
title: "GET /compute-ops-mgmt/v1beta2/reports/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/reports-v1beta2/get_report_v1beta2.md"
scraped_at: "2026-06-07T06:15:07.249788+00:00Z"
---

# Get report metadata

Retrieve a single report metadata resource by ID.

Endpoint: GET /compute-ops-mgmt/v1beta2/reports/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Report ID

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier for the report metadata resource given by the system.
    Example: "843023bd-9412-46c2-8ac2-a3691f657fdb"

  - `name` (string)
    The display name of the report.
    Example: "Carbon Footprint Report (All Servers)"

  - `type` (string)
    The type of the resource.

  - `generation` (integer)
    Monotonically increasing update counter.
    Example: 1

  - `createdAt` (string)
    Time of report resource creation.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `updatedAt` (string)
    Time of the last update to the report resource.
    Example: "2022-02-11T01:04:20.799937+00:00"

  - `resourceUri` (string)
    URI to the report metadata resource itself (i.e. a self link).
    Example: "/compute-ops-mgmt/v1beta2/reports/843023bd-9412-46c2-8ac2-a3691f657fdb"

  - `reportDataUri` (string)
    URI to the data for the report.
    Example: "/compute-ops-mgmt/v1beta2/reports/843023bd-9412-46c2-8ac2-a3691f657fdb/data"

  - `reportType` (any)

  - `reportTypeDisplayName` (string)
    The display name for the type of the report.
    Example: "Carbon Footprint Report"

  - `deviceIds` (any)
    Example: "875765-S01+1M512501AB"

  - `reportDataStartAt` (any)
    Example: "2022-02-04T01:04:20+00:00"

  - `reportDataEndAt` (any)
    Example: "2022-02-11T01:04:20+00:00"

  - `status` (string)
    The current status of report generation, indicating whether a report is in progress, completed, or failed
    Enum: "IN_PROGRESS", "COMPLETED", "FAILED"

  - `reportMetadata` (object)
    Metadata of the report.

  - `reportMetadata.associatedResourceName` (string)
    Name of the resource for which report generation was requested
    Example: "Demo group"

  - `reportMetadata.associatedResourceUri` (string)
    URI of the resource for which report generation was requested
    Example: "/compute-ops-mgmt/v1/groups/420372b6-af2e-464d-970d-e9339abfc74f"

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


