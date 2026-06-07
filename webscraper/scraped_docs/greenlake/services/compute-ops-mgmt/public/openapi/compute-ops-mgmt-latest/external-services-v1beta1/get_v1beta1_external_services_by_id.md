---
title: "GET /compute-ops-mgmt/v1beta1/external-services/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/external-services-v1beta1/get_v1beta1_external_services_by_id.md"
scraped_at: "2026-06-07T06:15:00.681389+00:00Z"
---

# Get an external-services item by ID

Get a specific external-services item by external-services id.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta1/external-services/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `name` (string)
    Name given to resource

  - `serviceType` (string)
    Used for specifying the type of external service.
| Value           | Description                               |
|-----------------|-------------------------------------------|
| SERVICE_NOW     | ServiceNow integration                    |
| DSCC            | Data Services Cloud Console integration   |
| VMWARE_VCENTER  | VMware vCenter integration                |
    Enum: "SERVICE_NOW", "DSCC", "VMWARE_VCENTER"

  - `authenticationType` (string)
    Used to specify which authentication method is used for authenticating the external service.
| Value | Description                                                 |
|-------|-------------------------------------------------------------|
| OAUTH | OAuth authentication (for SERVICE_NOW, DSCC)                |
| BASIC | Basic authentication with username/password (for VMWARE_VCENTER) |
    Enum: "OAUTH", "BASIC"

  - `description` (string,null)
    An optional longer description of the external service
    Example: "Service now configuration"

  - `authentication` (any)
    Authentication credentials based on authenticationType

  - `serviceData` (object)
    Service data corresponding to the specified serviceType

  - `status` (string)
    Status of the external service
    Enum: "ENABLED", "SUSPENDED"

  - `state` (string)
    State of the external service
    Enum: "ENABLED", "DISABLED"

  - `id` (string)
    Primary identifier for the external services resource given by the system.
    Example: "b870f080-6448-48c5-b23a-d04f2d489174"

  - `type` (string)
    Type of the resource

  - `resourceUri` (string)
    URI to the external-services itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta1/external-services/ff5798d5-b029-4452-b958-b33eabbe44d2"

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of external-services configuration creation

  - `updatedAt` (string)
    Time of the external-services configuration update

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


