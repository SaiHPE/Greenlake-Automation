---
title: "GET /compute-ops-mgmt/v1beta1/utilization-over-time"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/utilization-over-time-v1beta1/get_utilization_over_time.md"
scraped_at: "2026-06-07T06:15:13.489033+00:00Z"
---

# Retrieve utilization data over time

Retrieve CPU, memory bus, I/O bus or CPU interconnect utilization data over a time interval.

Endpoint: GET /compute-ops-mgmt/v1beta1/utilization-over-time
Version: latest
Security: Bearer

## Query parameters:

  - `start-date` (string, required)
    Start date for utilization data retrieval.

  - `end-date` (string, required)
    End date for utilization data retrieval.

  - `resource-uri` (string, required)
    URI of the resource for which utilization data is to be retrieved.
This can be a server, filter or group URI.

  - `metric-type` (string, required)
    The metric type for which utilization data is to be retrieved.
    Enum: "CPU_UTILIZATION", "MEMORY_BUS_UTILIZATION", "IO_BUS_UTILIZATION", "CPU_INTERCONNECT_UTILIZATION"

  - `filter-tags` (string)
    Limit the resources operated on by tags or return only the subset of resources that match all the filter tags.

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `metricType` (string)
    The metric type for which utilization data is being retrieved.
    Enum: "CPU_UTILIZATION", "MEMORY_BUS_UTILIZATION", "IO_BUS_UTILIZATION", "CPU_INTERCONNECT_UTILIZATION"

  - `metricUnit` (string)
    The unit of the retrieved data.
    Example: "Percentage"

  - `items` (array)
    Array of utilization data objects. Each item contains resource details, averages, and time series data.

  - `items.resource` (object)
    Details of the resource for which utilization data is collected.

  - `items.resource.id` (string)
    ID of the resource.
    Example: "875765-S01+1M512501AB"

  - `items.resource.type` (string)
    Type of the resource.
    Enum: "compute-ops-mgmt/filter", "compute-ops-mgmt/server"

  - `items.averages` (object)
    Average utilization data for the resource.

  - `items.averages.collected` (number)
    Average utilization value of all servers for the given resource-uri for the given date range.
    Example: 75.5

  - `items.intervalsCollected` (array)
    Time series data for the resource's utilization.

  - `items.intervalsCollected.time` (string)
    Timestamp of the data point.
    Example: "2025-02-01T00:00:00"

  - `items.intervalsCollected.value` (number)
    Average utilization value for this time interval.
    Example: 80

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


