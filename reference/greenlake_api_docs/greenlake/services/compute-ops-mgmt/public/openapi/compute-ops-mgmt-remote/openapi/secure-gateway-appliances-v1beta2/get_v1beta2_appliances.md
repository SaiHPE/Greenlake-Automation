---
title: "GET /compute-ops-mgmt/v1beta2/appliances"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/secure-gateway-appliances-v1beta2/get_v1beta2_appliances.md"
scraped_at: "2026-06-07T06:14:40.606102+00:00Z"
---

# List all secure gateway appliances

Retrieve data for all secure gateway appliances.

Endpoint: GET /compute-ops-mgmt/v1beta2/appliances
Version: latest
Security: Bearer

## Query parameters:

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved charecters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

  - `sort` (string)
    The order in which to return the resources in the collection.

The value of the sort query parameter is a comma separated list of sort expressions. 
Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc 
(descending).

The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, 
and so on. If a direciton indicator is omitted the default direction is ascending.

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `items` (array, required)

  - `items.id` (string, required)
    Primary identifier for the appliance
    Example: "3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `items.type` (string, required)
    Type of resource

  - `items.ipAddress` (string)
    IP address of the appliance

  - `items.deviceId` (string)
    Primary unique identifier for the appliance
    Example: "gateway+3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `items.name` (string)
    Name of the appliance
    Example: "secure-gateway-appliance-01.net"

  - `items.createdAt` (string)
    Time of appliance entry creation
    Example: "2025-03-01T10:50:33.736935+00:00"

  - `items.generation` (integer)
    Monotonically increasing update counter
    Example: 2450

  - `items.hostname` (string)
    Host name of the appliance
    Example: "secure-gateway-appliance-01.net"

  - `items.modelNumber` (string)
    Model of the appliance
    Example: "HPE Compute Ops Management secure gateway"

  - `items.productId` (string)
    Product identifier for the appliance
    Example: "gateway"

  - `items.state` (string)
    Connectivity state of the appliance
    Enum: "CONNECTED", "NOT_ACTIVATED", "DISCONNECTED"

  - `items.updatedAt` (string)
    Time of last appliance updated
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `items.lastDisconnectedAt` (string)
    Time of last appliance disconnected
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `items.applianceType` (string)
    Type of the appliance
    Example: "GATEWAY"

  - `items.applianceCert` (string)
    Certificate of the appliance

  - `items.applianceMode` (string)
    Mode of the appliance
    Enum: "NORMAL", "MAINTENANCE"

  - `items.resource` (object)
    Resource URI of the appliance

  - `items.resource.id` (string)
    Primary unique identifier for the appliance
    Example: "gateway+3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `items.resource.resourceUri` (string)
    Resource URI of the appliance
    Example: "/compute-ops-mgmt/v1beta2/appliances/gateway+3abc1b2c-4a5d-4e6f-9c7b-2a1d8e7f6abc"

  - `items.version` (string)
    Version of the appliance
    Example: "1.0.2+506412"

  - `items.subscription` (string,null,string,null)
    Subscription details for the appliance

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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


