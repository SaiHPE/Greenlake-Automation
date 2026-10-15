---
title: "GET /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupgetbyid.md"
scraped_at: "2026-06-07T06:14:22.126179+00:00Z"
---

# Get the host group details by {hostGroupId}

Get the host group details by {hostGroupId}

Endpoint: GET /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostGroupId` (string, required)
    Id of the host Group.
    Example: "e789e756496246859fde6c132b2091d3"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier for host group.
    Example: "e987ef683c27403e96caa51816ddc72c"

  - `type` (string, required)
    The type of resource.
    Example: "host-initiator-groups"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource URI

  - `associatedLinks.type` (string)
    Resource Name

  - `associatedSystems` (array,null)
    system IDs to which the host group belongs to.

  - `comment` (string,null)
    Comment
    Example: "host-group-comment"

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `editStatus` (string,null)
    Host group Update or Delete progress status. Possible status are: Update_In_Progress,Update_Success,Update_Failed,Delete_In_Progress,Delete_Failed,Not_Applicable,Merge_Success,Merge_In_Progress,Merge_Failed,Convert_In_Progress,Convert_Failed,Convert_Success.
    Example: "Delete_Failed"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627534116

  - `hosts` (array,null)
    List of hosts.

  - `hosts.id` (string, required)
    Identifier for host.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `hosts.initiators` (array)
    Initiator to which the host belongs to.

  - `hosts.initiators.id` (string, required)
    Identifier for an initiator.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `hosts.initiators.address` (string,null)
    Address of the initiator.
    Example: "100008F1EABFE61C"

  - `hosts.initiators.ipAddress` (string,null)
    IP address of the initiator.
    Example: "15.212.100.100"

  - `hosts.initiators.name` (string,null)
    Name of the initiator.

  - `hosts.initiators.pathType` (string,null)
    Transport type of the protocol. Valid values are FC, iSCSI NVMe/FC and NVMe/TCP.
    Example: "FC"

  - `hosts.initiators.systems` (array,null)
    system IDs to which the initiator belongs to.

  - `hosts.ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `hosts.isMergable` (boolean,null)
    Indicates whether host group has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
    Example: true

  - `hosts.isVvolHost` (boolean,null)
    Indicates if this host is created with NVMe initiator to be used by VASA vvol or not
    Example: true

  - `hosts.markedForDelete` (boolean,null)
    Indicates whether host is marked for deletion or not
    Example: true

  - `hosts.name` (string,null)
    Name of the host.
    Example: "host1"

  - `hosts.systems` (array,null)
    system IDs to which the host belongs to

  - `hosts.userCreated` (boolean,null)
    Indicates whether user created host or discovered host
    Example: true

  - `isMergable` (boolean,null)
    Indicates whether host has a duplicate. This field is applicable only when isMergable filter is set to true on the GET All else will be set to false always.
    Example: true

  - `markedForDelete` (boolean,null)
    Indicates whether host group is marked for deletion or not
    Example: true

  - `name` (string,null)
    Name of the host group
    Example: "host-group1"

  - `systems` (array,null)
    system IDs to which the host group belongs to

  - `userCreated` (boolean,null)
    Idicates whether user created host or discovered host
    Example: true

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response default fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


