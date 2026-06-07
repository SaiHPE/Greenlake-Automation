---
title: "POST /block-storage/v1alpha1/host-initiator-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-initiator-groups/hostgroupcreate.md"
scraped_at: "2026-06-07T06:14:30.757793+00:00Z"
---

# Create a host group

Create a host group with hosts having same protocol initiators

Endpoint: POST /block-storage/v1alpha1/host-initiator-groups
Version: 1.0.0
Security: bearer

## Request fields (application/json):

  - `name` (string,null, required)
    Name of the host group. The maximum supported length is 251 characters. Host Group name length greater than 27 characters is supported only for HPE Alletra Storage MP B10000 systems with OS version 10.4.2 and later.
    Example: "host-group1"

  - `comment` (string,null)
    Comment
    Example: "host-group-comment"

  - `hostIds` (array,null)
    List of host ids of existing hosts

  - `hostsToCreate` (array,null)
    List of hosts to be created and added to this hostGroup

  - `hostsToCreate.name` (string,null, required)
    Name of the host.
    Example: "host1"

  - `hostsToCreate.operatingSystem` (string,null, required)
    Host operating system. Possible Values are: - AIX - Apple - Citrix Hypervisor(XenServer) - HP-UX - IBM VIO Server - InForm - NetApp/ONTAP - OE Linux UEK - OpenVMS - Oracle VM x86 - RHE Linux - RHE Virtualization - Solaris - SuSE Linux - SuSE Virtualization - Ubuntu - VMware (ESXi) - Windows Server
    Enum: "AIX", "Apple", "Citrix Hypervisor(XenServer)", "HP-UX", "IBM VIO Server", "InForm", "NetApp/ONTAP", "OE Linux UEK", "OpenVMS", "Oracle VM x86", "RHE Linux", "RHE Virtualization", "Solaris", "SuSE Linux", "SuSE Virtualization", "Ubuntu", "VMware (ESXi)", "Windows Server"

  - `hostsToCreate.contact` (string,null)
    Contact information
    Example: "sanjay@hpe.com"

  - `hostsToCreate.fqdn` (string,null)
    Fully qualified domain name of the host.
    Example: "host1.hpe.com"

  - `hostsToCreate.hostGroupIds` (array,null)
    List of hostgroup IDs

  - `hostsToCreate.initiatorIds` (array,null)
    List of ids of existing initiators

  - `hostsToCreate.initiatorsToCreate` (array)
    List of initiators to be created and added to this host

  - `hostsToCreate.initiatorsToCreate.address` (string,null, required)
    Address of the initiator.
    Example: "iqn.1998-01.com.vmware:61f7c688-3e93-d360-8043-70106f7a7e18-0cba0054"

  - `hostsToCreate.initiatorsToCreate.protocol` (string,null, required)
    protocol supported are : FC, iSCSI or NVMe
    Example: "iSCSI"

  - `hostsToCreate.initiatorsToCreate.driverVersion` (string,null)
    Driver version of the host initiator.
    Example: "4.1"

  - `hostsToCreate.initiatorsToCreate.firmwareVersion` (string,null)
    Firmware version of the host initiator.
    Example: "10.0"

  - `hostsToCreate.initiatorsToCreate.hbaModel` (string,null)
    Host bus adaptor model of the host initiator
    Example: "model-5"

  - `hostsToCreate.initiatorsToCreate.hostSpeed` (integer,null)
    Host speed
    Example: 1000

  - `hostsToCreate.initiatorsToCreate.ipAddress` (string,null)
    IP address of the initiator. Supported only for iSCSI and NVMe protocols
    Example: "15.212.100.100"

  - `hostsToCreate.initiatorsToCreate.name` (string,null)
    Name of the initiator.
    Example: "init1"

  - `hostsToCreate.initiatorsToCreate.vendor` (string,null)
    Vendor of the host initiator
    Example: "hpe"

  - `hostsToCreate.ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `hostsToCreate.location` (string,null)
    location.
    Example: "India"

  - `hostsToCreate.model` (string,null)
    Model
    Example: "model1"

  - `hostsToCreate.persona` (string,null)
    Host persona details.
    Example: "AIX-Legacy"

  - `hostsToCreate.subnet` (string,null)
    subnet.
    Example: "255.255.255.0"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier for host group.
    Example: "d548ef683c27403e96caa51816ddc72c"

  - `type` (string, required)
    The type of resource.
    Example: "host-initiator-group"

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
    Host Update or Delete progress status. Possible status are: Update_In_Progress,Update_Success,Update_Failed,Delete_In_Progress,Delete_Failed,Not_Applicable,Merge_Success,Merge_In_Progress,Merge_Failed,Convert_In_Progress,Convert_Failed,Convert_Success.
    Example: "Delete_Failed"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627534116

  - `hosts` (array)
    List of hosts.

  - `hosts.id` (string, required)
    Identifier for host.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `hosts.associatedSystems` (array,null)
    system IDs to which the host belongs to.

  - `hosts.initiators` (array,null)
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
    Example: "init1"

  - `hosts.initiators.protocol` (string,null)
    protocol supported are : FC ,iSCSI or NVMe
    Example: "FC"

  - `hosts.ipAddress` (string,null)
    IP address of the host.
    Example: "15.212.100.100"

  - `hosts.isMergable` (boolean,null)
    Indicates whether host group has a duplicate. This field is applicable only when isMergable Filter is set to true on the GET All else will be set to false always.
    Example: true

  - `hosts.isVvolHost` (boolean,null)
    Indicates if this host is used to export VASA vVol over NVMe Protocol.
    Example: true

  - `hosts.markedForDelete` (boolean,null)
    Indicates whether host is marked for deletion or not
    Example: true

  - `hosts.name` (string,null)
    Name of the host.
    Example: "host1"

  - `markedForDelete` (boolean,null)
    Indicates whether host group is marked for deletion or not
    Example: true

  - `name` (string,null)
    Name of the host group.
    Example: "host-group1"

  - `systems` (array,null)
    system IDs to which the host group belongs to.

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


