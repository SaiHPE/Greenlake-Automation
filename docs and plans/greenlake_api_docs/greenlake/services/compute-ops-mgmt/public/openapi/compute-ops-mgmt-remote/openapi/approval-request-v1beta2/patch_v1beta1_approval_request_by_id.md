---
title: "PATCH /compute-ops-mgmt/v1beta2/approval-requests/{request_id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/approval-request-v1beta2/patch_v1beta1_approval_request_by_id.md"
scraped_at: "2026-06-07T06:14:42.114390+00:00Z"
---

# Update the request by id

Updates an approval request

Endpoint: PATCH /compute-ops-mgmt/v1beta2/approval-requests/{request_id}
Version: latest
Security: Bearer

## Path parameters:

  - `request_id` (string, required)
    Unique Request Identifier

## Header parameters:

  - `Content-Type` (string, required)
    Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed.

## Request fields (application/merge-patch+json):

  - `approvalState` (string)
    Set the state of the approval request.
The request can be cancelled only if it is in the PENDING state and only the requester
has the authority to cancel the request.

  - `requestRemarks` (string)
    Comments when modifying the request. This is an optional parameter.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for request given by the system.
    Example: "30fa7c27-64a0-4331-9462-73b0e004d4b9"

  - `type` (string, required)
    Type of resource

  - `createdAt` (string, required)
    Time of request entry creation
    Example: "2025-03-01T10:50:33.736935+00:00"

  - `updatedAt` (string, required)
    Time of last request update
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `generation` (integer, required)
    Monotonically increasing update counter
    Example: 8450

  - `resourceUri` (string)
    URI to the request ifself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/approval-requests/30fa7c27-64a0-4331-9462-73b0e004d4b9"

  - `policy` (object)
    Information about the policy that request is associated with.

  - `policy.id` (string)
    Unique identifier of the policy applied.
    Example: "f196db43-b56b-441c-a60e-73ca3bb53c5d"

  - `policy.resourceUri` (string)
    Resource URI
    Example: "/compute-ops-mgmt/v1beta2/approval-policies/f196db43-b56b-441c-a60e-73ca3bb53c5d"

  - `policy.type` (string)
    Policy resource Type

  - `approvableName` (string)
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
    Example: "Reset"

  - `approvableResource` (object)
    The approvableResource is the identifier of the resource for which the request is created.
This can refer to a server or group.

  - `approvableResource.id` (string)
    Unique identifier for resource associated to the request.
    Example: "215881-H98+8899215881198831"

  - `approvableResource.type` (string)
    The type of resource for which the request is created.
This can refer to a server or group.
    Example: "compute-ops-mgmt/server"

  - `operation` (object)
    This field indicates the action that is being performed on the resource.
The action can be a job or a scheduled job. When a request is created, the operation field will be populated 
with the job or schedule details.

  - `operation.id` (string)
    Unique identifier for operation
    Example: "e0f1ac57-9fab-468f-afab-67d6746267ee"

  - `operation.type` (string)
    Operation type
    Example: "compute-ops-mgmt/job"

  - `requester` (object)
    Indicates details on the requester of the approval request.

  - `requester.firstName` (string)
    First name of the requester
    Example: "Test"

  - `requester.lastName` (string)
    Last name of the requester
    Example: "User1"

  - `requester.email` (string)
    email of the requester
    Example: "anybody@email.org"

  - `approvalState` (string)
    The state of the request.
    Enum: "APPROVED", "CANCELLED", "DECLINED", "EXPIRED", "PENDING", "OTHER"

  - `requestRemarks` (string)
    Comments on the request

  - `cancelledBy` (string)
    Reason for cancellation of the request

  - `minApprovers` (integer)
    Minimum number of approvers required for the request to be approved
    Example: 2

  - `requestData` (object)
    Data for the approval request containing information about approvers ( they have the authority to approve or deny the requested action )
and the state of the request.

  - `requestData.approvals` (object)

  - `requestData.approvals.approverId` (object)

  - `requestData.approvals.approverId.firstName` (string)
    First name of the approver
    Example: "Test"

  - `requestData.approvals.approverId.lastName` (string)
    Last name of the approver
    Example: "User3"

  - `requestData.approvals.approverId.email` (string)
    Approver email address
    Example: "anybody@email.org"

  - `requestData.approvals.approvalState` (string)
    The state set by the user when approving or declining an approval request.
    Enum: "APPROVED", "DECLINED"

  - `requestData.approvals.remarks` (string)
    Comments on request

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


