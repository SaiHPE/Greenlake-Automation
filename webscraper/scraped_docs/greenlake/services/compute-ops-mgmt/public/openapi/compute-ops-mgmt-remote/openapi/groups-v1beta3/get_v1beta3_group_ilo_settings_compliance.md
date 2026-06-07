---
title: "GET /compute-ops-mgmt/v1beta3/groups/{group-id}/ilo-settings-compliance"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1beta3/get_v1beta3_group_ilo_settings_compliance.md"
scraped_at: "2026-06-07T06:14:46.090293+00:00Z"
---

# List all devices iLO Settings compliance in a group

List all the device's iLO Settings compliance detail

Endpoint: GET /compute-ops-mgmt/v1beta3/groups/{group-id}/ilo-settings-compliance
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `items` (array, required)

  - `items.groupId` (string)

  - `items.serial` (string)

  - `items.productId` (string)

  - `items.deviceId` (string)

  - `items.deviations` (array)

  - `items.deviations.category` (string)
    Category of the settings
    Example: "SnmpService"

  - `items.deviations.settingName` (string)
    Example: "SNMPv1Enabled"

  - `items.deviations.currentValue` (string)
    Example: "False"

  - `items.deviations.expectedValue` (string)
    Example: "True"

  - `items.complianceState` (string)
    The compliance state of ilo settings
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `items.errorReason` (string)
    It will have the reason for why the compliance state is UNKNOWN. for other compliance states it will be empty string.

  - `items.complianceCategory` (any)
    This refers to the Compliance Category

  - `items.remediation` (object)
    Specifies remediation actions for the device

  - `items.id` (string)
    Primary identifier for the compliance given by the system

  - `items.type` (string)
    Type of the resource

  - `items.resourceUri` (string)
    URI to the deviceCompliance itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta3/groups/c26e618b-4048-4aee-8e75-fbc984897a51/ilo-settings-compliance/b73718fb-30c3-4b0f-bee3-f5dd598414f3"

  - `items.deviceUri` (string)
    Example: "/compute-ops-mgmt/v1beta2/servers/873357-P04+WKQ82425HD"

  - `items.generation` (integer)
    Monotonically increasing update counter

  - `items.createdAt` (string)
    Time of compliance entry creation

  - `items.updatedAt` (string)
    This refers to when the firmware compliance was checked.

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


