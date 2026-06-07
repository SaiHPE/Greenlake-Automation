---
title: "POST /compute-ops-mgmt/v1beta1/oneview-appliances"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/oneview-appliances-v1beta1/add_v1beta1_oneview_appliances.md"
scraped_at: "2026-06-07T06:14:48.845453+00:00Z"
---

# Add a OneView appliance

Add a OneView appliance for management.

URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: POST /compute-ops-mgmt/v1beta1/oneview-appliances
Version: latest
Security: Bearer

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `id` (string)
    Unique identifier of the OneView appliance to be added
    Example: "497f6eca-6276-4993-bfeb-53cbbbbaabcd"

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the appliance
    Example: "87654321-f71a-43d2-8b93-4c7391b31234"

  - `type` (string, required)
    Type of resource
    Example: "compute-ops-mgmt/oneview-appliance"

  - `ipaddress` (string)
    IP address of the appliance

  - `device-id` (string)
    Primary unique identifier for the appliance
    Example: "oneview+87654321-f71a-43d2-8b93-4c7391b31234"

  - `activationKey` (string)
    Key to be used by customers to activate the appliance
    Example: "ABCDEFGHOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwY2lkIjoiNjg0YTVhMWEyOTU3MTFlZGE1MDF"

  - `applicationCustomerId` (string)
    Primary identifier for application customer

  - `complianceId` (string)
    Primary identifier for compliance state entry

  - `name` (string)
    Name of the appliance
    Example: "ci-005056abcdef.com"

  - `complianceLastChecked` (string)
    Time of last compliance check being performed

  - `complianceState` (string)
    Compliance state of the appliance
    Enum: "Compliant", "Not_compliant", "Unknown"

  - `createdAt` (string)
    Time of appliance entry creation
    Example: "2023-03-01T10:50:33.736935+00:00"

  - `generation` (integer)
    Monotonically increasing update counter
    Example: 1

  - `hostname` (string)
    Host name of the appliance
    Example: "ci-005056abcdef.com"

  - `lastModified` (string)
    Time of the last appliance update

  - `modelNumber` (string)
    Model of the appliance
    Example: "HPE OneView VM - VMware vSphere"

  - `platformCustomerId` (string)
    Primary identifier for platform customer

  - `productId` (string)
    Product identifier for the appliance
    Example: "oneview"

  - `state` (string)
    Connectivity state of the appliance
    Enum: "connected", "not activated", "disconnected"

  - `templateId` (string)
    Primary identifier of settings template created using this appliance

  - `templateName` (string)
    Name of the settings template
    Example: "Snmp_template"

  - `updatedAt` (string)
    Time of last appliance updated
    Example: "2023-03-01T11:05:00.554140+00:00"

  - `version` (string)
    Version of the OneView appliance
    Example: "8.00.00"

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


