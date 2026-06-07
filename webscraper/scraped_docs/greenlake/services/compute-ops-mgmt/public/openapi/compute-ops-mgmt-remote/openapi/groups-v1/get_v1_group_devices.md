---
title: "GET /compute-ops-mgmt/v1/groups/{group-id}/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1/get_v1_group_devices.md"
scraped_at: "2026-06-07T06:14:44.639341+00:00Z"
---

# List all devices in a group

List all devices in a group

Endpoint: GET /compute-ops-mgmt/v1/groups/{group-id}/devices
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

## Query parameters:

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Device IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Devices in a group can be filtered by:
  - eTag
  - groupId
  - overallSecurityStatus
  - productId
  - serial
  - subscriptionState
  - subscriptionTier


The following examples are not an exhaustive list of all possible filtering options.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `items` (array, required)

  - `items.id` (string)
    Primary identifier for the device given by the system
    Example: "497f6eca-6276-4993-bfeb-53cbbbba6f08"

  - `items.type` (string)
    Type of the resource

  - `items.resourceUri` (string)
    URI to the device itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1/groups/6081a383-b9e5-45e3-8371-1e0ba7b72068/devices/873357-P04+WKQ82425HD"

  - `items.serial` (string)
    Example: "SYN1002J11"

  - `items.productId` (string)
    Example: "P43990-121"

  - `items.eTag` (string)
    Example: "0xb2e9346d"

  - `items.deviceId` (string)
    Example: "P43990-121+SYN1002J11"

  - `items.deviceUri` (string)
    Example: "/compute-ops-mgmt/v1/servers/873357-P04+WKQ82425HD"

  - `items.groupId` (string)

  - `items.subscriptionState` (string)
    Subscription state.
    Enum: "REQUIRED", "SUBSCRIBED", "EXPIRED"

  - `items.subscriptionTier` (string)
    Subscription tier.
    Enum: "ENHANCED"

  - `items.overallSecurityStatus` (string)
    The current security status of a device
    Enum: "IGNORED", "OK", "RISK", "UNKNOWN", "UNSUPPORTED"

  - `total` (integer)
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


