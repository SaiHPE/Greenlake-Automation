---
title: "GET /block-storage/v1alpha1/initiators/{initiatorId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiators/hostinitiatorgetbyid.md"
scraped_at: "2026-06-07T06:14:32.253864+00:00Z"
---

# Get the initiator details by {initiatorId}

Get the initiator details by {initiatorId}

Endpoint: GET /block-storage/v1alpha1/initiators/{initiatorId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `initiatorId` (string, required)
    UID of Initiator.
    Example: "e789e756496246859fde6c132b2091d3"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier for an initiator.
    Example: "e748ef683c27403e96caa51816ddc72c"

  - `type` (string, required)
    The type of resource.
    Example: "initiator"

  - `address` (string,null)
    Address of the initiator.
    Example: "100008F1EABFE61C"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource URI

  - `associatedLinks.type` (string)
    Resource Name

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `driverVersion` (string,null)
    Driver version of the host initiator.
    Example: "4.1"

  - `firmwareVersion` (string,null)
    Firmware version of the host initiator.
    Example: "10.0"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627534116

  - `hbaModel` (string,null)
    Host bus adaptor model of the host initiator
    Example: "myobject-5"

  - `hostSpeed` (integer,null)
    Host speed
    Example: 1000

  - `hosts` (array)
    List of hosts. Filter by hostId.

  - `hosts.id` (string, required)
    Identifier for host.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `hosts.hostGroups` (array,null)
    Host group to which the host belongs to.

  - `hosts.hostGroups.id` (string, required)
    Identifier for host group.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `hosts.hostGroups.isMergable` (boolean,null)
    Indicates whether host group has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
    Example: true

  - `hosts.hostGroups.markedForDelete` (boolean,null)
    Indicates whether host group is marked for deletion or not
    Example: true

  - `hosts.hostGroups.name` (string,null)
    Name of the host group
    Example: "host-group1"

  - `hosts.hostGroups.systems` (array,null)
    system IDs to which the host group belongs to

  - `hosts.hostGroups.userCreated` (boolean,null)
    Idicates whether user created host or discovered host
    Example: true

  - `hosts.ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `hosts.isMergable` (boolean,null)
    Indicates whether host has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
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

  - `ipAddress` (string,null)
    IP address of the initiator.
    Example: "15.212.100.100"

  - `name` (string,null)
    Name of the initiator.
    Example: "init1"

  - `pathType` (string,null)
    Transport type of the protocol. Valid values are FC, iSCSI, NVMe/FC and NVMe/TCP.
    Example: "FC"

  - `protocol` (string,null)
    protocol supported are : FC ,iSCSI or NVMe
    Example: "FC"

  - `systems` (array,null)
    System IDs associated with the host initiator

  - `vendor` (string,null)
    Vendor of the host initiator
    Example: "hpe"

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


