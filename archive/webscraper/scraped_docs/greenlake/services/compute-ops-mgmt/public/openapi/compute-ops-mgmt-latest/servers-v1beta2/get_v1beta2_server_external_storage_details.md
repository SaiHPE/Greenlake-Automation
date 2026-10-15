---
title: "GET /compute-ops-mgmt/v1beta2/servers/{id}/external-storage-details"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/get_v1beta2_server_external_storage_details.md"
scraped_at: "2026-06-07T06:15:11.831852+00:00Z"
---

# Get external storage details

Retrieves external storage hosts and volume details for a server specified by the server id


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta2/servers/{id}/external-storage-details
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique server identifier

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Response 200 fields (application/json):

  - `serverId` (string)
    The server id for the volume details

  - `createdAt` (string)
    Time the volume details were gathered

  - `updatedAt` (string)
    The last time the volume details were updated

  - `generation` (integer)
    Monotonically increasing update counter

  - `volumeDetails` (array)
    Details of the volumes attached to the server

  - `volumeDetails.lun` (integer)
    Logical unit number

  - `volumeDetails.name` (string)
    Name of the volume

  - `hostName` (string)
    Name of the host

  - `hostOs` (string)
    An enumeration.
    Enum: "UNKNOWN", "AIX", "APPLE", "CITRIX_HYPERVISOR", "HP_UX", "IBM_VIO_SERVER", "INFORM", "NETAPP", "OE_LINUX_UEK", "OPENVMS", "ORACLE_VM", "RHE_LINUX", "RHE_VIRTUALIZATION", "SOLARIS", "SUSE_LINUX", "SUSE_VIRTUALIZATION", "UBUNTU", "VMWARE_ESXI", "WINDOWS_SERVER"

  - `hostGroups` (array)
    Host groups to which the host belongs

  - `hostGroups.id` (string)

  - `hostGroups.name` (string)
    Name of the host group

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


