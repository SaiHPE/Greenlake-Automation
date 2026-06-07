---
title: "GET /compute-ops-mgmt/v1beta2/appliances/{device_id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/secure-gateway-appliances-v1beta2/get_v1beta2_appliances_by_id.md"
scraped_at: "2026-06-07T06:14:58.795737+00:00Z"
---

# Get a secure gateway appliance by id

Get a specific secure gateway appliance by id.

Endpoint: GET /compute-ops-mgmt/v1beta2/appliances/{device_id}
Version: latest
Security: Bearer

## Path parameters:

  - `device_id` (string, required)
    Unique identifier of the appliance for which information is retrieved

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the appliance
    Example: "3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `type` (string, required)
    Type of resource

  - `ipAddress` (string)
    IP address of the appliance

  - `deviceId` (string)
    Primary unique identifier for the appliance
    Example: "gateway+3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `name` (string)
    Name of the appliance
    Example: "secure-gateway-appliance-01.net"

  - `createdAt` (string)
    Time of appliance entry creation
    Example: "2025-03-01T10:50:33.736935+00:00"

  - `generation` (integer)
    Monotonically increasing update counter
    Example: 2450

  - `hostname` (string)
    Host name of the appliance
    Example: "secure-gateway-appliance-01.net"

  - `modelNumber` (string)
    Model of the appliance
    Example: "HPE Compute Ops Management secure gateway"

  - `productId` (string)
    Product identifier for the appliance
    Example: "gateway"

  - `state` (string)
    Connectivity state of the appliance
    Enum: "CONNECTED", "NOT_ACTIVATED", "DISCONNECTED"

  - `updatedAt` (string)
    Time of last appliance updated
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `lastDisconnectedAt` (string)
    Time of last appliance disconnected
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `applianceType` (string)
    Type of the appliance
    Example: "GATEWAY"

  - `applianceCert` (string)
    Certificate of the appliance

  - `applianceMode` (string)
    Mode of the appliance
    Enum: "NORMAL", "MAINTENANCE"

  - `resource` (object)
    Resource URI of the appliance

  - `resource.id` (string)
    Primary unique identifier for the appliance
    Example: "gateway+3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `resource.resourceUri` (string)
    Resource URI of the appliance
    Example: "/compute-ops-mgmt/v1beta2/appliances/gateway+3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `version` (string)
    Version of the appliance
    Example: "1.0.2+506412"

  - `subscription` (string,null)
    Subscription details for the appliance

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

## Response 409 fields (application/json):

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


