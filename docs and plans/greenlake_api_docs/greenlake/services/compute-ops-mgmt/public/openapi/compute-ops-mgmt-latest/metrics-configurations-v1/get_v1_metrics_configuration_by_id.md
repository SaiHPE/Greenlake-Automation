---
title: "GET /compute-ops-mgmt/v1/metrics-configurations/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/metrics-configurations-v1/get_v1_metrics_configuration_by_id.md"
scraped_at: "2026-06-07T06:15:06.266188+00:00Z"
---

# Get metrics-configuration item by ID

Get specific metrics-configuration item by metrics-configuration id.

Endpoint: GET /compute-ops-mgmt/v1/metrics-configurations/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier for the metrics configuration resource given by the system.
    Example: "b870f080-6448-48c5-b23a-d04f2d489174"

  - `type` (string)
    Type of the resource

  - `resourceUri` (string)
    URI to the metrics-configuration itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/metrics-configurations/b870f080-6448-48c5-b23a-d04f2d489174"

  - `metricsCollection` (string)
    Metrics collection method to indicate if the metrics collection is scheduled or generated on demand.
    Enum: "SYSTEM_SCHEDULED", "ON_DEMAND"

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of metrics configuration creation
    Example: "2023-07-07T05:51:02.624513+00:00"

  - `updatedAt` (string)
    Time of the metrics configuration update
    Example: "2023-07-07T05:51:02.624513+00:00"

  - `powerThresholdAlerts` (boolean)
    Boolean to indicate whether power utilization alerts have to be enabled or not.

  - `powerUtilizationThresholdPercentage` (integer)
    Threshold value in percentage beyond which power utilization alerts will be generated.

  - `alertResources` (array)
    Alerts resources for power utilization alerts

  - `alertResources.id` (string)
    Primary identifier for the alerts resource.
    Example: "a761f080-6448-48c5-d34a-d04f2d489159"

  - `alertResources.name` (string)
    Unique name for the alert resource provided by the user.
    Example: "Production Group"

  - `alertResources.type` (string)
    The type of the resource for which power utilization is calculated.
    Example: "group"

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


