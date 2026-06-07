---
title: "GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_ilo_settings_compliance.md"
scraped_at: "2026-06-07T06:15:04.854036+00:00Z"
---

# Get iLO Settings compliance

List all the iLO Settings compliance detail

Endpoint: GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance
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

  - `items.id` (string)
    Primary identifier for the compliance given by the system

  - `items.type` (string)
    Type of the resource

  - `items.generation` (integer)
    Monotonically increasing update counter

  - `items.createdAt` (string)
    Time of compliance entry creation

  - `items.updatedAt` (string)
    This refers to when the firmware compliance was checked.

  - `items.resourceUri` (string)
    URI to the deviceCompliance itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/eb54e96e-21b8-4f54-9cd4-80fccbd06f55/ilo-settings-compliance/b73718fb-30c3-4b0f-bee3-f5dd598414f3"

  - `items.serial` (string)

  - `items.productId` (string)

  - `items.serverId` (string)

  - `items.deviations` (array)

  - `items.deviations.category` (string)
    Category of the settings
    Example: "1"

  - `items.deviations.settingName` (string)
    Example: "RequiredLoginForiLORBSU"

  - `items.deviations.currentValue` (string)
    Example: "False"

  - `items.deviations.expectedValue` (string)
    Example: "True"

  - `items.complianceState` (string)
    The compliance state of ilo settings
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `items.remediation` (object)
    Specifies remediation actions for the device

  - `items.complianceCategory` (any)
    This refers to the Compliance Category

  - `items.groupId` (string)
    The group id of the ilo settings

  - `items.serverUri` (string)
    Server URI
    Example: "/compute-ops/v1beta2/servers/975017-V69+8899975017569500"

  - `items.errorReason` (string)
    It will have the reason for why the compliance state is UNKNOWN. for other compliance states it will be empty string.

  - `total` (integer)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

  - `start` (integer)
    Zero-based resource offset, alias of offset

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


