---
title: "POST /compute-ops/v1beta2/groups/{group-id}/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1beta2/assign_v1beta2_group_devices.md"
scraped_at: "2026-06-07T06:14:46.824046+00:00Z"
---

# Assign a device to a group

Assign a device to a group

Endpoint: POST /compute-ops/v1beta2/groups/{group-id}/devices
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Query parameters:

  - `dry-run` (boolean)
    When set to false, servers will be assigned or moved to the group specified by group-id barring any errors.

When set to true, servers will not be assigned or moved to the specified group. This dry-run request will return useful information about the servers involved in the request, such as the latest eTags.

## Request fields (application/json):

  - `devices` (array, required)

  - `devices.serial` (string)

  - `devices.productId` (string)

  - `devices.eTag` (string)
    This property is required when a server is moved from one group to another. It is optional (and can be omitted) for all other requests.

When moving a server from one group to another, the latest eTag for that server must be specified. To find the latest eTag(s) associated with one or more servers, send this request specifying those servers and set the query parameter dry-run to true. A server's eTag will change as it moves between groups, so it is essential to use the latest eTag to avoid any errors when moving a server.

In the rare case that a request is made to assign a server to the group it is already in, the eTag check will not be performed. In other words, the device's assignment will have zero effect because the desired outcome has already been achieved.

  - `devices.serverId` (string)

## Response 200 fields (application/json):

  - `devices` (array, required)

  - `devices.id` (string, required)
    Primary identifier for the device given by the system

  - `devices.type` (string, required)
    Type of the resource

  - `devices.resourceUri` (string)
    URI to the device itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/6081a383-b9e5-45e3-8371-1e0ba7b72068/devices/873357-P04+WKQ82425HD"

  - `devices.serial` (string)

  - `devices.productId` (string)

  - `devices.eTag` (string)

  - `devices.serverId` (string)

  - `devices.serverUri` (string)
    Example: "/api/compute/v1/servers/873357-P04+WKQ82425HD"

  - `devices.state` (string)
    An enumeration.
    Enum: "ASSIGNED", "FAILED", "ACTIVE", "QUARANTINE", "APPLYING_FIRMWARE", "APPLYING_SCHEMA", "APPLYING_OS"

  - `devices.groupId` (string)

  - `devices.subscriptionState` (string)
    Subscription state.
    Enum: "REQUIRED", "SUBSCRIBED", "EXPIRED"

  - `devices.subscriptionTier` (string)
    Subscription tier.
    Enum: "ENHANCED"

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

## Response 412 fields (application/json):

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


