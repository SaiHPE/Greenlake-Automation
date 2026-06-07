---
title: "POST /compute-ops-mgmt/v1/groups/{group-id}/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/assign_v1_group_devices.md"
scraped_at: "2026-06-07T06:15:02.744122+00:00Z"
---

# Assign device(s) to a group

Assign device(s) to a group using an asynchronous operation. On a successful request this endpoint will return a 202 Accepted response with a Location header that contains the resource URI of the operation. That resource URI can then be used to monitor the asynchronous operation's status.

Endpoint: POST /compute-ops-mgmt/v1/groups/{group-id}/devices
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/json' in order for the request to be performed.

## Request fields (application/json):

  - `devices` (array, required)
    Specifies the devices to be assigned to the group.

  - `devices.deviceId` (string, required)
    The device to assign to the group.
    Example: "LUKEB1-G11+TUXED0CA77"

  - `devices.eTag` (string)
    This property is required when a device is moved from one group to another. It is optional (and can be omitted) for all other requests.

When moving a device from one group to another, the latest eTag for that device must be specified. A device's eTag will change as it moves between groups, so it is essential to use the latest eTag to avoid any errors when moving a device.

In the rare case that a request is made to assign a device to the group it is already in, the eTag check will not be performed. In other words, the device's assignment will have zero effect because the desired outcome has already been achieved.
    Example: "0xb2e9346d"

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


## Response 202 fields
