---
title: "GET /compute-ops-mgmt/v1beta1/utilization-by-entity"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/utilization-by-entity-v1beta1/get_utilization_by_entity.md"
scraped_at: "2026-06-07T06:15:13.449267+00:00Z"
---

# Retrieve utilization data by entity

Retrieve CPU, memory bus, I/O bus or CPU interconnect utilization data per entity.

Endpoint: GET /compute-ops-mgmt/v1beta1/utilization-by-entity
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

  - `excluded-servers` (boolean)
    When it is set to true, the response will have details of servers which do not have utilization data available.
    Example: true

  - `filter-tags` (string)
    Limit the resources operated on by tags or return only the subset of resources that match all the filter tags.

  - `sort` (string)
    The order in which to return the resources in the collection.
Sort expression is a property name, followed by asc (ascending) or desc (descending).

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

  - `count` (integer)
    Number of items in the response.
    Example: 2

  - `offset` (integer)
    Offset of the returned items.

  - `total` (integer)
    Total number of items available.
    Example: 2

  - `excluded` (integer)
    Number of excluded servers for which utilization data is not available.

  - `metricDetails` (object)
    Details about the metric type for which utilization data is being retrieved.

  - `metricDetails.metricType` (string)
    The metric type for which utilization data is being retrieved.
    Enum: "CPU_UTILIZATION", "MEMORY_BUS_UTILIZATION", "IO_BUS_UTILIZATION", "CPU_INTERCONNECT_UTILIZATION"

  - `metricDetails.metricUnit` (string)
    The unit of the retrieved data.
    Example: "Percentage"

  - `items` (array)
    List of individual entity utilization data.

  - `items.id` (string)
    Unique identifier of the entity
    Example: "ABCDEF-B21+MXQLABC"

  - `items.name` (string)
    Name of the entity
    Example: "server-ABC"

  - `items.type` (string)
    Type of entity
    Enum: "SERVER"

  - `items.metadata` (any)
    Details about different server components.

  - `items.collected` (object)
    High, low and average utilization values for the entity.

  - `items.collected.high` (number)
    Maximum daily average utilization value for the entity.
    Example: 95

  - `items.collected.low` (number)
    Minimum daily average utilization value for the entity.
    Example: 10

  - `items.collected.average` (number)
    Average utilization value for the entity.
    Example: 75.5

  - `items.status` (string)
    Represents whether data is available for the server.
If data is available, the status will show "COMPLETE". 
If data is not fully available, the status will show "PARTIAL".
    Example: "COMPLETE"

  - `items.statusReason` (string)
    The reason for the current status.
    Example: "DATA_INSUFFICIENT"

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


