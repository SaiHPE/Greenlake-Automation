---
title: "GET /compute-ops/v1beta2/groups/{group-id}/external-storage-compliance"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/groups-v1beta2/get_v1beta2_group_external_storage_compliance.md"
scraped_at: "2026-06-07T06:15:04.758815+00:00Z"
---

# Get external storage compliance

List all the external storage's compliance detail

Endpoint: GET /compute-ops/v1beta2/groups/{group-id}/external-storage-compliance
Version: latest
Security: Bearer

## Path parameters:

  - `group-id` (string, required)

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `groupId` (string)
    The group id of the external storage

  - `createdAt` (string)
    Time of compliance entry creation

  - `updatedAt` (string)
    This refers to when the compliance was checked.

  - `generation` (integer)
    Monotonically increasing update counter

  - `hostOs` (string)
    The host OS of the external storage
    Enum: "UNKNOWN", "AIX", "APPLE", "CITRIX_HYPERVISOR", "HP_UX", "IBM_VIO_SERVER", "INFORM", "NETAPP", "OE_LINUX_UEK", "OPENVMS", "ORACLE_VM", "RHE_LINUX", "RHE_VIRTUALIZATION", "SOLARIS", "SUSE_LINUX", "SUSE_VIRTUALIZATION", "UBUNTU", "VMWARE_ESXI", "WINDOWS_SERVER"

  - `complianceState` (string)
    The compliance state of the external storage
    Enum: "COMPLIANT", "NOT_COMPLIANT", "UNKNOWN", "NOT_APPLICABLE"

  - `deviations` (object)
    The deviations from the compliance check

  - `deviations.mismatchOperatingSystem` (array)
    The server and host with mismatched operating systems

  - `deviations.mismatchOperatingSystem.server` (object)
    The server with mismatched operating system

  - `deviations.mismatchOperatingSystem.server.id` (string)
    Primary identifier for the server

  - `deviations.mismatchOperatingSystem.server.name` (string)
    Name of the server

  - `deviations.mismatchOperatingSystem.host` (object)
    The host with mismatched operating system

  - `deviations.mismatchOperatingSystem.host.name` (string)
    Name of the host

  - `deviations.mismatchOperatingSystem.operatingSystem` (string)
    The operating system of the host
    Enum: "UNKNOWN", "AIX", "APPLE", "CITRIX_HYPERVISOR", "HP_UX", "IBM_VIO_SERVER", "INFORM", "NETAPP", "OE_LINUX_UEK", "OPENVMS", "ORACLE_VM", "RHE_LINUX", "RHE_VIRTUALIZATION", "SOLARIS", "SUSE_LINUX", "SUSE_VIRTUALIZATION", "UBUNTU", "VMWARE_ESXI", "WINDOWS_SERVER"

  - `deviations.missingInitiators` (array)
    The server and initiators that are missing from the host

  - `deviations.missingInitiators.server` (object)
    The server that is missing initiators

  - `deviations.missingInitiators.initiators` (array)
    Example: ["11:00:00:ab:00:01:20:01"]

  - `deviations.extraInitiator` (array)
    The host and initiators that are extra

  - `deviations.extraInitiator.host` (object)
    The host that is extra

  - `deviations.missingHostsFromHostGroup` (array)
    The server that is missing from the host group

  - `deviations.missingHostsFromHostGroup.server` (object)
    The server that is missing from the host group

  - `deviations.extraHostsInHostGroup` (array)
    The host that is extra in the host group

  - `deviations.extraHostsInHostGroup.host` (object)
    The host that is extra in the host group

  - `deviations.initiatorsWithMultipleHosts` (array)
    The server and hosts with multiple initiators

  - `deviations.initiatorsWithMultipleHosts.server` (object)
    The server with multiple initiators

  - `deviations.initiatorsWithMultipleHosts.hosts` (array)
    The hosts with multiple initiators

  - `deviations.missingHostGroups` (array)
    The host groups that are missing

  - `deviations.missingHostGroups.hostGroup` (object)
    The host group that is missing

  - `deviations.missingHostGroups.hostGroup.name` (string)
    Name of the host group

  - `deviations.hostGroupsNotCreated` (array)
    The host groups that are not created

  - `deviations.hostGroupsNotCreated.hostGroup` (object)
    The host group that is not created

  - `deviations.noInitiators` (array)
    Servers with no initiators

  - `deviations.noInitiators.server` (object)
    The server with no initiators

  - `deviations.preExistingHostNames` (array)
    Hosts that are pre-existing

  - `deviations.preExistingHostNames.server` (object)
    The server with pre-existing host

  - `deviations.preExistingHostNames.host` (object)
    The host that is pre-existing

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

## Response 401 fields (application/json):

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

## Response 406 fields (application/json):

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


