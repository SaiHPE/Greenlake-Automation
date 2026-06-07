---
title: "GET /compute-ops-mgmt/v1beta2/approval-policies"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/get_v1beta2_approval_policies.md"
scraped_at: "2026-06-07T06:14:59.065415+00:00Z"
---

# List all approval policies

Retrieves all active approval policies

Endpoint: GET /compute-ops-mgmt/v1beta2/approval-policies
Version: latest
Security: Bearer

## Query parameters:

  - `offset` (integer)
    Zero-based resource offset to start the response from
    Example: 10

  - `limit` (integer)
    The maximum number of records to return.
    Example: 10

  - `filter` (string)
    Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint,
return only the subset of resources that match the filter. The filter grammar is a subset
of OData 4.0.

NOTE: The filter query parameter must use URL encoding.
Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.  
The reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] must be encoded with percent encoded equivalents.
Server IDs contain a +, which must be encoded as %2B.  
For example: the value P06760-B21+2M212504P8 must be encoded as P06760-B21%2B2M212504P8 when it is used in a query parameter.

| CLASS     |  EXAMPLES                                          |
|-----------|----------------------------------------------------|
| Types     | integer, decimal, timestamp, string, boolean, null |
| Operations| eq, ne, gt, ge, lt, le, in                         |
| Logic     | and, or, not                                       |

Approval policies can be filtered by:
- createdAt
- description
- name
- policyData/resources/id
- policyData/resources/type
- updatedAt

The following examples are not an exhaustive list of all possible filtering options.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned
    Example: 1

  - `offset` (integer, required)
    Zero-based resource offset

  - `items` (array, required)

  - `items.id` (string, required)
    Primary identifier for policy given by the system.
    Example: "4c102e14-87cd-4c00-8f5a-73073f85c9az"

  - `items.type` (string, required)
    Type of the resource

  - `items.createdAt` (string, required)
    Time of policy entry creation
    Example: "2025-03-01T10:50:33.736935+00:00"

  - `items.updatedAt` (string, required)
    Time of last policy update
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `items.generation` (integer, required)
    Monotonically increasing update counter
    Example: 8450

  - `items.name` (string)
    Policy name
    Example: "demo-policy"

  - `items.resourceUri` (string)
    URI to the policy itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/approval-policies/4c102e14-87cd-4c00-8f5a-73073f85c9az"

  - `items.description` (string)
    Policy description
    Example: "Example policy"

  - `items.state` (string)
    Approval policy state
    Enum: "ACTIVE", "INACTIVE"

  - `items.remarks` (string)
    Comments on the policy
    Example: "This is a demo policy"

  - `items.policyData` (object)
    Information about approvers and other resources assigned to the policy

  - `items.policyData.approvables` (array)

  - `items.policyData.approvables.approvableName` (string)
    approvableName is used to identify the type of operation that requires approval.
A case-sensitive field that must contain a value from the "Approvable Name" column below.
The actions that are supported for approval follow:
  | Approvable Name                      |  Description                                                                  |
  |--------------------------------------|-------------------------------------------------------------------------------|
  | Update firmware                      | Updating the firmware of server or servers in a group.                        |
  | Apply internal storage configuration | Applying internal storage configuration to the server or servers in a group.  |
  | Install operating system image       | Installing the operating system image on the server or servers in a group.    |
  | Apply external storage configuration | Applying external storage configuration to the server or servers in a group.  |
  | Power on                             | Powering on the server.                                                       |
  | Power off                            | Powering off the server.                                                      |
  | Reset                                | Resetting the server.                                                         |
  | Cold boot                            | Cold booting the server.                                                      |
  | Update iLO firmware                  | Updating the iLO firmware on the server or servers in a group                 |
  | Apply server settings (BIOS and iLO) | Applying server settings (BIOS and iLO) to the server or servers in a group   |
    Example: "Apply internal storage configuration"

  - `items.policyData.approvables.approvers` (array)
    Data concerning approvers for the approval policy. The specified approvers have the 
authority to approve or deny the requested action, identified as the 'Approvable Name' 
in the table above, for the designated server or servers in a group.

  - `items.policyData.approvables.minApprovers` (integer)
    minApprovers set the number of required approvals.
An optional field indicating the minimum number of required approvers for the request.
If the number of approvers who approve the request is greater than or equal to this value, 
the request will be approved.
A single decline of the request will decline the request regardless of the minApprovers value.

  - `items.policyData.resources` (array)

  - `items.policyData.resources.resourceId` (string)
    unique identifier of resource assigned to the policy
    Example: "29d8ba78-16bd-4b2f-b3c1-0395f38ee741"

  - `items.policyData.resources.resourceType` (string)
    Type of the resource assigned to the policy.
Currently policy can be configured only for the group resource type.
    Example: "compute-ops-mgmt/group"

  - `total` (integer, required)
    Total number of items in the collection that match the filter query, if one was provided in the request
    Example: 12

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

## Response 422 fields (application/json):

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


