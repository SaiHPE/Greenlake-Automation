---
title: "GET /compute-ops/v1beta2/groups/{group-id}/compliance/{compliance-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/groups-v1beta2/get_v1beta2_compliance_by_compliance_id.md"
scraped_at: "2026-06-07T06:14:46.834795+00:00Z"
---

# Get a device compliance by compliance Id

Get a specific device compliance detail of the group by passing group id and compliance id.

Endpoint: GET /compute-ops/v1beta2/groups/{group-id}/compliance/{compliance-id}
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

  - `compliance-id` (string, required)

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the compliance given by the system

  - `type` (string, required)
    Type of the resource

  - `generation` (integer, required)
    Monotonically increasing update counter

  - `createdAt` (string, required)
    Time of compliance entry creation

  - `updatedAt` (string, required)
    This refers to when the firmware compliance was checked.

  - `resourceUri` (string)
    URI to the deviceCompliance itself (i.e. a self link)
    Example: "/compute-ops/v1beta2/groups/c26e618b-4048-4aee-8e75-fbc984897a51/compliance/b73718fb-30c3-4b0f-bee3-f5dd598414f3"

  - `groupId` (string)

  - `serial` (string)

  - `productId` (string)

  - `serverId` (string)

  - `complianceStatus` (string)
    This state defines the compliance status of a device.
If all devices in a group are COMPLIANT, the group state will be compliant.
If a group contains devices that are COMPLIANT or UNKNOWN, the UNKNOWN state
overrides the COMPLIANT state and the group state will be UNKNOWN.
If a group contains devices that are NOT_COMPLIANT, COMPLIANT, or UNKNOWN
the NOT_COMPLIANT state will override the COMPLIANT and UNKNOWN states, so
the group state will be NOT_COMPLIANT. Finally, the NOT_APPLICABLE state
overrides all others so if a device in a group is NOT_APPLICABLE or if the
group has no devices, the group state will be NOT_APPLICABLE.
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `deviations` (array)

  - `deviations.componentName` (string)
    Description of the firmware component which has a deviation with group firmware baseline

  - `deviations.installedVersion` (string)
    Installed version of firmware component

  - `deviations.expectedVersion` (string)
    Expected version for firmware component

  - `deviations.componentFilename` (string)
    Name of the firmware component file

  - `errorReason` (string)
    It will have the reason for why the compliance state is UNKNOWN. for other compliance states it will be empty string.

  - `complianceCategory` (any)
    This refers to the Compliance Category

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


