---
title: "GET /compute-ops-mgmt/v1beta3/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_ilo_settings_compliance_by_compliance_id.md"
scraped_at: "2026-06-07T06:15:03.782327+00:00Z"
---

# Get a device compliance by iLO Settings compliance Id

Get a specific device compliance detail of the group by passing group id and iLO Settings compliance id.

Endpoint: GET /compute-ops-mgmt/v1beta3/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

  - `ilo-settings-compliance-id` (string, required)

## Response 200 fields (application/json):

  - `groupId` (string)

  - `serial` (string)

  - `productId` (string)

  - `deviceId` (string)

  - `deviations` (array)

  - `deviations.category` (string)
    Category of the settings
    Example: "SnmpService"

  - `deviations.settingName` (string)
    Example: "SNMPv1Enabled"

  - `deviations.currentValue` (string)
    Example: "False"

  - `deviations.expectedValue` (string)
    Example: "True"

  - `complianceState` (string)
    The compliance state of ilo settings
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `errorReason` (string)
    It will have the reason for why the compliance state is UNKNOWN. for other compliance states it will be empty string.

  - `complianceCategory` (any)
    This refers to the Compliance Category

  - `remediation` (object)
    Specifies remediation actions for the device

  - `id` (string)
    Primary identifier for the compliance given by the system

  - `type` (string)
    Type of the resource

  - `resourceUri` (string)
    URI to the deviceCompliance itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta3/groups/c26e618b-4048-4aee-8e75-fbc984897a51/ilo-settings-compliance/b73718fb-30c3-4b0f-bee3-f5dd598414f3"

  - `deviceUri` (string)
    Example: "/compute-ops-mgmt/v1beta2/servers/873357-P04+WKQ82425HD"

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of compliance entry creation

  - `updatedAt` (string)
    This refers to when the firmware compliance was checked.

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


