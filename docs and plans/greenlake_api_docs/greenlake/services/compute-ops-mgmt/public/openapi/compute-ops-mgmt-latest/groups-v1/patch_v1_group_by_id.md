---
title: "PATCH /compute-ops-mgmt/v1/groups/{group-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1/patch_v1_group_by_id.md"
scraped_at: "2026-06-07T06:15:02.286110+00:00Z"
---

# Patch a group

Partially update a group.

Endpoint: PATCH /compute-ops-mgmt/v1/groups/{group-id}
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed.

## Request fields (application/merge-patch+json):

  - `name` (string)
    Example: "Production Group"

  - `description` (string)
    Example: "All prod servers"

  - `settingsUris` (array)
    URIs for group device settings
    Example: ["/compute-ops-mgmt/v1/settings/00000000-0000-0000-0000-800000000001"]

  - `policies` (any)

  - `autoAddTags` (object)
    A case insensitive tag that can be associated with a group to automatically add devices to the group. A group can have a maximum of one tag and multiple groups can not have the same tag.

When a device is onboarded or has its tags changed, the devices's tags will be checked against the group's autoAddTags.  If at least one of the device tags matches one group's autoAddTags, the device will be placed into the associated group. Once a device has been connected, it becomes ineligible for automatically being placed into groups, even if it is later disconnected.

If a device's tags match more than one group, it will not be put into any group.

If a devices is in a group, any further tag changes will not move it to another group.  If the device was added to a group but has been removed, is not in any group, and still has not been activated, changing the device tags will automatically assign it to the matching group.

Tags can contain any alphaneumeric characters, any Unicode space separators, and the following characters: _ . : = + - @. An example of one of these tags can be seen in the sample request on this page.
    Example: {"Department":"Development - Texas"}

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


