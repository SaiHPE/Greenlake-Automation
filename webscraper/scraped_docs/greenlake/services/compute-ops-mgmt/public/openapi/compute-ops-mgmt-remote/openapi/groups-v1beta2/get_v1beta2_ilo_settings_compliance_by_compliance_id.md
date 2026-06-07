---
title: "GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1beta2/get_v1beta2_ilo_settings_compliance_by_compliance_id.md"
scraped_at: "2026-06-07T06:14:47.053494+00:00Z"
---

# Get a device iLO Settings compliance by iLO Settings compliance Id

Get a specific device compliance detail of the group by passing group id and iLO Settings compliance id.

Endpoint: GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

  - `ilo-settings-compliance-id` (string, required)

## Response 200 fields (application/json):

  - `id` (string)
    Primary identifier for the compliance given by the system

  - `type` (string)
    Type of the resource

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of compliance entry creation

  - `updatedAt` (string)
    This refers to when the firmware compliance was checked.

  - `resourceUri` (string)
    URI to the deviceCompliance itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/eb54e96e-21b8-4f54-9cd4-80fccbd06f55/ilo-settings-compliance/b73718fb-30c3-4b0f-bee3-f5dd598414f3"

  - `serial` (string)

  - `productId` (string)

  - `serverId` (string)

  - `deviations` (array)

  - `deviations.category` (string)
    Category of the settings
    Example: "1"

  - `deviations.settingName` (string)
    Example: "RequiredLoginForiLORBSU"

  - `deviations.currentValue` (string)
    Example: "False"

  - `deviations.expectedValue` (string)
    Example: "True"

  - `complianceState` (string)
    The compliance state of ilo settings
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `remediation` (object)
    Specifies remediation actions for the device

  - `complianceCategory` (any)
    This refers to the Compliance Category

  - `groupId` (string)
    The group id of the ilo settings

  - `serverUri` (string)
    Server URI
    Example: "/compute-ops/v1beta2/servers/975017-V69+8899975017569500"

  - `errorReason` (string)
    It will have the reason for why the compliance state is UNKNOWN. for other compliance states it will be empty string.

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


