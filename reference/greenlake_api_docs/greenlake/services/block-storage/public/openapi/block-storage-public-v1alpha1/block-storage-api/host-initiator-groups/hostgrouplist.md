---
title: "GET /block-storage/v1alpha1/host-initiator-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiator-groups/hostgrouplist.md"
scraped_at: "2026-06-07T06:14:30.756719+00:00Z"
---

# Get the list of host groups

Get the list of host groups

Endpoint: GET /block-storage/v1alpha1/host-initiator-groups
Version: 1.0.0
Security: bearer

## Query parameters:

  - `filter` (string)
    oData query to filter hostservice by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004817"

  - `sort` (string)
    oData query to sort hostservice by Key.
    Example: "name desc"

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier for host group. Filter
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    The type of resource.
    Example: "host-initiator-group"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource URI

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.associatedSystems` (array,null)
    system IDs to which the host group belongs to.

  - `items.comment` (string,null)
    Comment
    Example: "host-group-comment"

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.editStatus` (string,null)
    Host Update or Delete progress status. Possible status are: Update_In_Progress,Update_Success,Update_Failed,Delete_In_Progress,Delete_Failed,Not_Applicable,Merge_Success,Merge_In_Progress,Merge_Failed,Convert_In_Progress,Convert_Failed,Convert_Success. Filter
    Example: "Delete_Failed"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627534116

  - `items.hosts` (array,null)
    List of hosts. Filter by hostId. Sort by count.

  - `items.hosts.id` (string, required)
    Identifier for host.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.hosts.initiators` (array)
    Initiator to which the host belongs to. Sort by count.

  - `items.hosts.initiators.id` (string, required)
    Identifier for an initiator.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `items.hosts.initiators.address` (string,null)
    Address of the initiator.
    Example: "100008F1EABFE61C"

  - `items.hosts.initiators.ipAddress` (string,null)
    IP address of the initiator.
    Example: "15.212.100.100"

  - `items.hosts.initiators.name` (string,null)
    Name of the initiator.

  - `items.hosts.initiators.pathType` (string,null)
    Transport type of the protocol. Valid values are FC, iSCSI NVMe/FC and NVMe/TCP.
    Example: "FC"

  - `items.hosts.initiators.systems` (array,null)
    system IDs to which the initiator belongs to.

  - `items.hosts.ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `items.hosts.isMergable` (boolean,null)
    Indicates whether host group has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
    Example: true

  - `items.hosts.isVvolHost` (boolean,null)
    Indicates if this host is created with NVMe initiator to be used by VASA vvol or not
    Example: true

  - `items.hosts.markedForDelete` (boolean,null)
    Indicates whether host is marked for deletion or not
    Example: true

  - `items.hosts.name` (string,null)
    Name of the host.
    Example: "host1"

  - `items.hosts.systems` (array,null)
    system IDs to which the host belongs to

  - `items.hosts.userCreated` (boolean,null)
    Indicates whether user created host or discovered host
    Example: true

  - `items.isMergable` (boolean,null)
    Indicates whether host group has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.Sort
    Example: true

  - `items.markedForDelete` (boolean,null)
    Indicates whether host group is marked for deletion or not
    Example: true

  - `items.name` (string,null)
    Name of the host group. Filter, Sort
    Example: "host-group1"

  - `items.systems` (array,null)
    system IDs to which the host group belongs to. Filter. Sort by count.

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

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


