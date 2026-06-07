---
title: "POST /backup-recovery/v1beta1/virtual-machines/{id}/restore"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machines/virtualmachinerestore.md"
scraped_at: "2026-06-07T06:14:07.793534+00:00Z"
---

# Restore a virtual machine from snapshot or backup.

Restores a virtual machine from the selected snapshot or backup.

Endpoint: POST /backup-recovery/v1beta1/virtual-machines/{id}/restore
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the virtual machine
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `restoreType` (string, required)
    Specifies the type of restore that needs to be performed.
    Enum: "PARENT", "ALTERNATE"

  - `snapshotId` (string, required)
    UUID string uniquely identifying the snapshot. Mandatory if the restore is from a snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `backupId` (string, required)
    UUID string uniquely identifying the backup. Mandatory if the restore is from a backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `targetVmInfo` (object)
    Provides the details about the target VM location, compute, etc These inputs are required only if the restore type is 'ALTERNATE'.

  - `targetVmInfo.appInfo` (object)
    Hypervisor specific information.

  - `targetVmInfo.appInfo.vmware` (object)
    VMware specific app info.

  - `targetVmInfo.appInfo.vmware.datastoreId` (string)
    Specifies the destination datastore in case of
alternate restore.

  - `targetVmInfo.appInfo.vmware.resourcePoolId` (string)
    To specify a destination resource pool.

  - `targetVmInfo.clusterId` (string)
    The target hypervisor cluster onto which the new virtual machine is hosted.
Either hostId or clusterId has to be provided as input.
Both can not be specified at the same time.

  - `targetVmInfo.description` (string)
    A brief description about the new VM.

  - `targetVmInfo.folderId` (string)
    The identifier of the folder into which the virtual machine needs to be placed.

  - `targetVmInfo.hostId` (string)
    The target hypervisor host onto which the new virtual machine is hosted.
Either hostId or clusterId has to be provided as input.
Both can not be specified at the same time.

  - `targetVmInfo.hypervisorManagerId` (string)
    Specifies the destination hypervisor manager.

  - `targetVmInfo.name` (string)
    Name of the virtual machine as configured in the hypervisor manager.
    Example: "vm-1-windows"

  - `targetVmInfo.powerOn` (boolean)
    True if the new VM to be powered on after successful creation.

  - `targetVmInfo.storageInfo` (object)
    Target storage information required to provision the new storage,
required only in case of alternate datastore restore.

  - `targetVmInfo.storageInfo.storageSystemId` (string)
    Target storage system where the new volumes will be provisioned in case of alternate restore.

  - `targetVmInfo.vmHardwareCustomization` (object)

  - `targetVmInfo.vmHardwareCustomization.networkAdapters` (array)

  - `targetVmInfo.vmHardwareCustomization.networkAdapters.name` (string)
    Name of the network adapter.

  - `targetVmInfo.vmHardwareCustomization.networkAdapters.networkDetails` (object)

  - `targetVmInfo.vmHardwareCustomization.networkAdapters.networkDetails.connectAtPowerOn` (boolean)
    Specifies if the network has to be connected at power on.

  - `targetVmInfo.vmHardwareCustomization.networkAdapters.networkDetails.id` (string)
    UUID string uniquely identifying the hypervisor network resource.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

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

## Response 409 fields (application/json):

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

## Response 412 fields (application/json):

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


