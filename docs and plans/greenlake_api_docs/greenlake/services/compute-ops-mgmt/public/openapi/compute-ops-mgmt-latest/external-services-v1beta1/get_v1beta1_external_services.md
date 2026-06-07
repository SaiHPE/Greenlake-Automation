---
title: "GET /compute-ops-mgmt/v1beta1/external-services"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/get_v1beta1_external_services.md"
scraped_at: "2026-06-07T06:15:00.642975+00:00Z"
---

# List all external services

Get the list of external services configured


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta1/external-services
Version: latest
Security: Bearer

## Query parameters:

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

External Service can be filtered by:
  - serviceType

The following examples are not an exhaustive list of all possible filtering options.

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

  - `items.name` (string,string)
    Name given to resource

  - `items.serviceType` (string)
    Used for specifying the type of external service.
| Value           | Description                               |
|-----------------|-------------------------------------------|
| SERVICE_NOW     | ServiceNow integration                    |
| DSCC            | Data Services Cloud Console integration   |
| VMWARE_VCENTER  | VMware vCenter integration                |
    Enum: "SERVICE_NOW", "DSCC", "VMWARE_VCENTER"

  - `items.authenticationType` (string)
    Used to specify which authentication method is used for authenticating the external service.
| Value | Description                                                 |
|-------|-------------------------------------------------------------|
| OAUTH | OAuth authentication (for SERVICE_NOW, DSCC)                |
| BASIC | Basic authentication with username/password (for VMWARE_VCENTER) |
    Enum: "OAUTH", "BASIC"

  - `items.description` (string,null,string,null)
    An optional longer description of the external service
    Example: "Service now configuration"

  - `items.authentication` (any)

  - `items.serviceData` (any)

  - `items.status` (string)
    Status of the external service
    Enum: "ENABLED", "SUSPENDED"

  - `items.state` (string)
    State of the external service
    Enum: "ENABLED", "DISABLED"

  - `items.id` (string)
    Primary identifier for the external services resource given by the system.
    Example: "b870f080-6448-48c5-b23a-d04f2d489174"

  - `items.type` (string)
    Type of the resource

  - `items.resourceUri` (string)
    URI to the external-services itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/external-services/ff5798d5-b029-4452-b958-b33eabbe44d2"

  - `items.generation` (integer)
    Monotonically increasing update counter

  - `items.createdAt` (string)
    Time of external-services configuration creation

  - `items.updatedAt` (string)
    Time of the external-services configuration update

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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


