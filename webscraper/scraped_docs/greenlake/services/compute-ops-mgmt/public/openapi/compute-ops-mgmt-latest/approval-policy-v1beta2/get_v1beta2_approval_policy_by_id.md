---
title: "GET /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/approval-policy-v1beta2/get_v1beta2_approval_policy_by_id.md"
scraped_at: "2026-06-07T06:14:59.433498+00:00Z"
---

# Get approval policy by id

Retrieves approval policy by id

Endpoint: GET /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}
Version: latest
Security: Bearer

## Path parameters:

  - `policy_id` (string, required)
    Unique Policy Identifier

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for policy given by the system.
    Example: "4c102e14-87cd-4c00-8f5a-73073f85c9az"

  - `type` (string, required)
    Type of the resource

  - `createdAt` (string, required)
    Time of policy entry creation
    Example: "2025-03-01T10:50:33.736935+00:00"

  - `updatedAt` (string, required)
    Time of last policy update
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `generation` (integer, required)
    Monotonically increasing update counter
    Example: 8450

  - `name` (string)
    Policy name
    Example: "demo-policy"

  - `resourceUri` (string)
    URI to the policy itself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/approval-policies/4c102e14-87cd-4c00-8f5a-73073f85c9az"

  - `description` (string)
    Policy description
    Example: "Example policy"

  - `state` (string)
    Approval policy state
    Enum: "ACTIVE", "INACTIVE"

  - `remarks` (string)
    Comments on the policy
    Example: "This is a demo policy"

  - `policyData` (object)
    Information about approvers and other resources assigned to the policy

  - `policyData.approvables` (array)

  - `policyData.approvables.approvableName` (string)
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

  - `policyData.approvables.approvers` (array)
    Data concerning approvers for the approval policy. The specified approvers have the 
authority to approve or deny the requested action, identified as the 'Approvable Name' 
in the table above, for the designated server or servers in a group.

  - `policyData.approvables.approvers.email` (string)
    Approver email address
    Example: "test_user1@hpe.com"

  - `policyData.approvables.minApprovers` (integer)
    minApprovers set the number of required approvals.
An optional field indicating the minimum number of required approvers for the request.
If the number of approvers who approve the request is greater than or equal to this value, 
the request will be approved.
A single decline of the request will decline the request regardless of the minApprovers value.

  - `policyData.resources` (array)

  - `policyData.resources.resourceId` (string)
    unique identifier of resource assigned to the policy
    Example: "29d8ba78-16bd-4b2f-b3c1-0395f38ee741"

  - `policyData.resources.resourceType` (string)
    Type of the resource assigned to the policy.
Currently policy can be configured only for the group resource type.
    Example: "compute-ops-mgmt/group"

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


