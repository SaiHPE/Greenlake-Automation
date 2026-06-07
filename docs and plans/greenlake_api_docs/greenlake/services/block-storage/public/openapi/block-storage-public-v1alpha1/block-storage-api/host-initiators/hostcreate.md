---
title: "POST /block-storage/v1alpha1/host-initiators"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiators/hostcreate.md"
scraped_at: "2026-06-07T06:14:31.330022+00:00Z"
---

# Create a host

Create a host with same protocol initiators

Endpoint: POST /block-storage/v1alpha1/host-initiators
Version: 1.0.0
Security: bearer

## Request fields (application/json):

  - `name` (string,null, required)
    Name of the host.
    Example: "host1"

  - `operatingSystem` (string,null, required)
    Host operating system. Possible Values are: - AIX - Apple - Citrix Hypervisor(XenServer) - HP-UX - IBM VIO Server - InForm - NetApp/ONTAP - OE Linux UEK - OpenVMS - Oracle VM x86 - RHE Linux - RHE Virtualization - Solaris - SuSE Linux - SuSE Virtualization - Ubuntu - VMware (ESXi) - Windows Server
    Enum: "AIX", "Apple", "Citrix Hypervisor(XenServer)", "HP-UX", "IBM VIO Server", "InForm", "NetApp/ONTAP", "OE Linux UEK", "OpenVMS", "Oracle VM x86", "RHE Linux", "RHE Virtualization", "Solaris", "SuSE Linux", "SuSE Virtualization", "Ubuntu", "VMware (ESXi)", "Windows Server"

  - `comment` (string,null)
    Comment
    Example: "comment1"

  - `contact` (string,null)
    Contact information
    Example: "sanjay@hpe.com"

  - `fqdn` (string,null)
    Fully qualified domain name of the host.
    Example: "host1.hpe.com"

  - `hostGroupIds` (array,null)
    List of hostgroup IDs

  - `initiatorIds` (array,null)
    List of ids of existing initiators

  - `initiatorsToCreate` (array)
    List of initiators to be created and added to this host

  - `initiatorsToCreate.address` (string,null, required)
    Address of the initiator.
    Example: "iqn.1998-01.com.vmware:61f7c688-3e93-d360-8043-70106f7a7e18-0cba0054"

  - `initiatorsToCreate.protocol` (string,null, required)
    protocol supported are : FC, iSCSI or NVMe
    Example: "iSCSI"

  - `initiatorsToCreate.driverVersion` (string,null)
    Driver version of the host initiator.
    Example: "4.1"

  - `initiatorsToCreate.firmwareVersion` (string,null)
    Firmware version of the host initiator.
    Example: "10.0"

  - `initiatorsToCreate.hbaModel` (string,null)
    Host bus adaptor model of the host initiator
    Example: "model-5"

  - `initiatorsToCreate.hostSpeed` (integer,null)
    Host speed
    Example: 1000

  - `initiatorsToCreate.ipAddress` (string,null)
    IP address of the initiator. Supported only for iSCSI and NVMe protocols
    Example: "15.212.100.100"

  - `initiatorsToCreate.name` (string,null)
    Name of the initiator.
    Example: "init1"

  - `initiatorsToCreate.vendor` (string,null)
    Vendor of the host initiator
    Example: "hpe"

  - `ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `location` (string,null)
    location.
    Example: "India"

  - `model` (string,null)
    Model
    Example: "model1"

  - `persona` (string,null)
    Host persona details.
    Example: "AIX-Legacy"

  - `subnet` (string,null)
    subnet.
    Example: "255.255.255.0"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier for host.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `type` (string, required)
    The type of resource.
    Example: "host-initiator"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource URI

  - `associatedLinks.type` (string)
    Resource Name

  - `associatedSystems` (array,null)
    system IDs to which the host belongs to.

  - `comment` (string,null)
    Comment
    Example: "a sample host comment"

  - `contact` (string,null)
    Contact information
    Example: "sanjay@hpe.com"

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `editStatus` (string,null)
    Host Update or Delete progress status. Possible status are: Update_In_Progress,Update_Success,Update_Failed,Delete_In_Progress,Delete_Failed,Not_Applicable,Merge_Success,Merge_In_Progress,Merge_Failed,Convert_In_Progress,Convert_Failed,Convert_Success.
    Example: "Delete_Failed"

  - `fqdn` (string,null)
    Fully qualified domain name of the host.
    Example: "host1.hpe.com"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627534116

  - `hostGroups` (array)
    Host group to which the host belongs to.

  - `hostGroups.id` (string, required)
    Identifier for host group.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `hostGroups.associatedSystems` (array,null)
    system IDs to which the host group belongs to.

  - `hostGroups.isMergable` (boolean,null)
    Indicates whether host has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
    Example: true

  - `hostGroups.markedForDelete` (boolean,null)
    Indicates whether host group is marked for deletion or not
    Example: true

  - `hostGroups.name` (string,null)
    Name of the host group
    Example: "host-group1"

  - `initiators` (array)
    Host initiator list this host is associated with.

  - `initiators.id` (string, required)
    Identifier for an initiator.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `initiators.address` (string,null)
    Address of the initiator.
    Example: "100008F1EABFE61C"

  - `initiators.ipAddress` (string,null)
    IP address of the initiator.
    Example: "15.212.100.100"

  - `initiators.name` (string,null)
    Name of the initiator.
    Example: "init1"

  - `initiators.protocol` (string,null)
    protocol supported are : FC ,iSCSI or NVMe
    Example: "FC"

  - `ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `isVvolHost` (boolean,null)
    Indicates if this host is created with NVMe initiator to be used by VASA vvol or not
    Example: true

  - `location` (string,null)
    location.
    Example: "India"

  - `markedForDelete` (boolean,null)
    Indicates whether host is marked for deletion or not
    Example: true

  - `model` (string,null)
    Model
    Example: "model1"

  - `name` (string,null)
    Name of the host.
    Example: "host1"

  - `operatingSystem` (string,null)
    Host operating system.
    Example: "Windows"

  - `persona` (string,null)
    Host persona details.
    Example: "AIX-Legacy"

  - `subnet` (string,null)
    subnet.
    Example: "255.255.255.0"

  - `systems` (array,null)
    system IDs to which the host belongs to.

  - `userCreated` (boolean,null)
    Indicates whether user created host or discovered host
    Example: true

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


