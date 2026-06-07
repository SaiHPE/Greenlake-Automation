---
title: "GET /compute-ops-mgmt/v1beta2/approval-requests"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/approval-request-v1beta2/get_v1beta1_approval_requests.md"
scraped_at: "2026-06-07T06:14:42.090640+00:00Z"
---

# List all approval requests

Retrieves all active approval requests

Endpoint: GET /compute-ops-mgmt/v1beta2/approval-requests
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

Approval requests can be filtered by:
- approvableName
- approvableResource/id
- approvableResource/type
- approvalState
- createdAt
- operation/id
- operation/type
- policy/id
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
    Primary identifier for request given by the system.
    Example: "30fa7c27-64a0-4331-9462-73b0e004d4b9"

  - `items.type` (string, required)
    Type of resource

  - `items.createdAt` (string, required)
    Time of request entry creation
    Example: "2025-03-01T10:50:33.736935+00:00"

  - `items.updatedAt` (string, required)
    Time of last request update
    Example: "2025-03-01T11:05:00.554140+00:00"

  - `items.generation` (integer, required)
    Monotonically increasing update counter
    Example: 8450

  - `items.resourceUri` (string)
    URI to the request ifself (i.e. a self link)
    Example: "/compute-ops-mgmt/v1beta2/approval-requests/30fa7c27-64a0-4331-9462-73b0e004d4b9"

  - `items.policy` (object)
    Information about the policy that request is associated with.

  - `items.policy.id` (string)
    Unique identifier of the policy applied.
    Example: "f196db43-b56b-441c-a60e-73ca3bb53c5d"

  - `items.policy.resourceUri` (string)
    Resource URI
    Example: "/compute-ops-mgmt/v1beta2/approval-policies/f196db43-b56b-441c-a60e-73ca3bb53c5d"

  - `items.policy.type` (string)
    Policy resource Type

  - `items.approvableName` (string)
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

  - `items.approvableResource` (object)
    The approvableResource is the identifier of the resource for which the request is created.
This can refer to a server or group.

  - `items.approvableResource.id` (string)
    Unique identifier for resource associated to the request.
    Example: "215881-H98+8899215881198831"

  - `items.approvableResource.type` (string)
    The type of resource for which the request is created.
This can refer to a server or group.
    Example: "compute-ops-mgmt/server"

  - `items.operation` (object)
    This field indicates the action that is being performed on the resource.
The action can be a job or a scheduled job. When a request is created, the operation field will be populated 
with the job or schedule details.

  - `items.operation.id` (string)
    Unique identifier for operation
    Example: "e0f1ac57-9fab-468f-afab-67d6746267ee"

  - `items.operation.type` (string)
    Operation type
    Example: "compute-ops-mgmt/job"

  - `items.requester` (object)
    Indicates details on the requester of the approval request.

  - `items.requester.firstName` (string)
    First name of the requester
    Example: "Test"

  - `items.requester.lastName` (string)
    Last name of the requester
    Example: "User1"

  - `items.requester.email` (string)
    email of the requester
    Example: "anybody@email.org"

  - `items.approvalState` (string)
    The state of the request.
    Enum: "APPROVED", "CANCELLED", "DECLINED", "EXPIRED", "PENDING", "OTHER"

  - `items.requestRemarks` (string)
    Comments on the request

  - `items.cancelledBy` (string)
    Reason for cancellation of the request

  - `items.minApprovers` (integer)
    Minimum number of approvers required for the request to be approved
    Example: 2

  - `items.requestData` (object)
    Data for the approval request containing information about approvers ( they have the authority to approve or deny the requested action )
and the state of the request.

  - `items.requestData.approvals` (object)

  - `items.requestData.approvals.approverId` (object)

  - `items.requestData.approvals.approverId.firstName` (string)
    First name of the approver
    Example: "Test"

  - `items.requestData.approvals.approverId.lastName` (string)
    Last name of the approver
    Example: "User3"

  - `items.requestData.approvals.approverId.email` (string)
    Approver email address
    Example: "anybody@email.org"

  - `items.requestData.approvals.approvalState` (string)
    The state set by the user when approving or declining an approval request.
    Enum: "APPROVED", "DECLINED"

  - `items.requestData.approvals.remarks` (string)
    Comments on request

  - `total` (integer, required)
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


