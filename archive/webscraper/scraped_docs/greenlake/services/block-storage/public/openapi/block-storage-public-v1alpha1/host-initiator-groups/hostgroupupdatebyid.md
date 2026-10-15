---
title: "PUT /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiator-groups/hostgroupupdatebyid.md"
scraped_at: "2026-06-07T06:14:22.291949+00:00Z"
---

# Update host group by {hostGroupId}

Update host group details by {hostGroupId}. Hostgroup can be updated with hosts containing same protocol initiators

Endpoint: PUT /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostGroupId` (string, required)
    Id of the host Group.
    Example: "e789e756496246859fde6c132b2091d3"

## Request fields (application/json):

  - `hostProximityValues` (array)
    Change Proximity for list of hosts

  - `hostProximityValues.groupName` (string,null)
    Replication Group Name
    Example: "RCGName"

  - `hostProximityValues.groupUid` (string,null)
    Replication Group ID
    Example: "rcg1"

  - `hostProximityValues.hostId` (string,null)
    Host ID
    Example: "12345"

  - `hostProximityValues.hostName` (string,null)
    Host name
    Example: "host1"

  - `hostProximityValues.proximitySystemName` (string,null)
    Host proximity value
    Example: "primary"

  - `hostProximityValues.systemName` (string,null)
    Source system name
    Example: "system1"

  - `hostProximityValues.systemUid` (string,null)
    Source system serial number
    Example: "SGH014XGSP"

  - `hostProximityValues.targetName` (string,null)
    Target system name
    Example: "system2"

  - `hostProximityValues.targetSystemId` (string,null)
    Target system serial number
    Example: "7CE751P312"

  - `hostsToCreate` (array,null)
    List of hosts to be replaced to the group

  - `hostsToCreate.name` (string,null, required)
    Name of the host.
    Example: "host1"

  - `hostsToCreate.operatingSystem` (string,null, required)
    Host operating system. Possible Values are: - AIX - Apple - Citrix Hypervisor(XenServer) - HP-UX - IBM VIO Server - InForm - NetApp/ONTAP - OE Linux UEK - OpenVMS - Oracle VM x86 - RHE Linux - RHE Virtualization - Solaris - SuSE Linux - SuSE Virtualization - Ubuntu - VMware (ESXi) - Windows Server
    Enum: "AIX", "Apple", "Citrix Hypervisor(XenServer)", "HP-UX", "IBM VIO Server", "InForm", "NetApp/ONTAP", "OE Linux UEK", "OpenVMS", "Oracle VM x86", "RHE Linux", "RHE Virtualization", "Solaris", "SuSE Linux", "SuSE Virtualization", "Ubuntu", "VMware (ESXi)", "Windows Server"

  - `hostsToCreate.comment` (string,null)
    Comment
    Example: "comment1"

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

  - `name` (string,null)
    Name of the host group. The maximum supported length is 251 characters. Host Group name length greater than 27 characters is supported only for HPE Alletra Storage MP B10000 systems with OS version 10.4.2 and later.
    Example: "host-group1"

  - `removedHosts` (array)
    List of host IDs to be removed from the group

  - `updatedHosts` (array)
    List of host IDs to be added to the group

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

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


