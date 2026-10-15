---
title: "GET /block-storage/v1alpha1/initiators"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostinitiatorlist.md"
scraped_at: "2026-06-07T06:14:23.572826+00:00Z"
---

# Get the list of initiators

Get the list of initiators

Endpoint: GET /block-storage/v1alpha1/initiators
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

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier for an initiator.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    The type of resource.
    Example: "initiator"

  - `items.address` (string,null)
    Address of the initiator. Filter
    Example: "100008F1EABFE61C"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource URI

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.driverVersion` (string,null)
    Driver version of the host initiator.
    Example: "4.1"

  - `items.firmwareVersion` (string,null)
    Firmware version of the host initiator.
    Example: "10.0"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627534116

  - `items.hbaModel` (string,null)
    Host bus adaptor model of the host initiator
    Example: "myobject-5"

  - `items.hostSpeed` (integer,null)
    Host speed
    Example: 1000

  - `items.hosts` (array)
    List of hosts.

  - `items.hosts.id` (string, required)
    Identifier for host.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.hosts.editStatus` (string,null)
    Host Update or Delete progress status. Possible status are: Update_In_Progress,Update_Success,Update_Failed,Delete_In_Progress,Delete_Failed,Not_Applicable,Merge_Success,Merge_In_Progress,Merge_Failed,Convert_In_Progress,Convert_Failed,Convert_Success. Filter
    Example: "Update_Success"

  - `items.hosts.hostGroups` (array,null)
    Host group to which the host belongs to. Sort by count.

  - `items.hosts.hostGroups.id` (string, required)
    Identifier for host group.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `items.hosts.hostGroups.isMergable` (boolean,null)
    Indicates whether host group has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
    Example: true

  - `items.hosts.hostGroups.markedForDelete` (boolean,null)
    Indicates whether host group is marked for deletion or not
    Example: true

  - `items.hosts.hostGroups.name` (string,null)
    Name of the host group
    Example: "host-group1"

  - `items.hosts.hostGroups.systems` (array,null)
    system IDs to which the host group belongs to

  - `items.hosts.hostGroups.userCreated` (boolean,null)
    Idicates whether user created host or discovered host
    Example: true

  - `items.hosts.ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `items.hosts.isMergable` (boolean,null)
    Indicates whether host has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
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

  - `items.ipAddress` (string,null)
    IP address of the initiator.
    Example: "15.212.100.100"

  - `items.name` (string,null)
    Name of the initiator.
    Example: "init1"

  - `items.pathType` (string,null)
    Transport type of the protocol. Valid values are FC, iSCSI ,NVMe/FC and NVMe/TCP.

  - `items.protocol` (string,null)
    protocol supported are : FC ,iSCSI or NVMe
    Example: "FC"

  - `items.systems` (array,null)
    System IDs associated with the host initiator

  - `items.vendor` (string,null)
    Vendor of the host initiator
    Example: "hpe"

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


