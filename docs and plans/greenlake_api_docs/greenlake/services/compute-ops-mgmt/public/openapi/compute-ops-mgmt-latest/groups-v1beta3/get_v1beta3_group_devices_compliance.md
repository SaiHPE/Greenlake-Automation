---
title: "GET /compute-ops-mgmt/v1beta3/groups/{group-id}/compliance"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta3/get_v1beta3_group_devices_compliance.md"
scraped_at: "2026-06-07T06:15:03.158938+00:00Z"
---

# List all devices compliance in a group

List all the device's compliance detail

Endpoint: GET /compute-ops-mgmt/v1beta3/groups/{group-id}/compliance
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

Group compliance can be filtered by:
  - bundleId
  - complianceCategory
  - complianceState
  - createdAt
  - generation
  - productId
  - remediation
  - score
  - updatedAt


The following examples are not an exhaustive list of all possible filtering options.

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

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

  - `items.bundleId` (string)
    Primary identifier for the firmware bundle

  - `items.deviations` (array)

  - `items.deviations.componentName` (string)
    Description of the firmware component which has a deviation with group firmware baseline

  - `items.deviations.installedVersion` (string)
    Installed version of firmware component

  - `items.deviations.expectedVersion` (string)
    Expected version for firmware component

  - `items.deviations.componentFilename` (string)
    Name of the firmware component file

  - `items.score` (integer)

  - `items.complianceState` (string)
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

  - `items.errorReason` (string)
    It will have the reason for why the compliance state is UNKNOWN. for other compliance states it will be empty string.

  - `items.remediation` (object)
    Specifies remediation actions for the device

  - `items.complianceCategory` (any)
    This refers to the Compliance Category

  - `items.id` (string)
    Primary identifier for the compliance given by the system

  - `items.type` (string)
    Type of the resource

  - `items.resourceUri` (string)
    URI to the deviceCompliance itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta3/groups/c26e618b-4048-4aee-8e75-fbc984897a51/compliance/b73718fb-30c3-4b0f-bee3-f5dd598414f3"

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


