---
title: "POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmpgrestore.md"
scraped_at: "2026-06-07T06:14:06.245391+00:00Z"
---

# Restore a virtual machine Protection Group from recovery points.

Restore a virtual machine Protection Group from recovery points.

Endpoint: POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `description` (string)
    A brief description about the new VM.

  - `namePostfix` (string)
    A postfix name given by user for the new VM.

  - `namePrefix` (string)
    A prefix name for the new VM.

  - `powerOnVmsAfterRestore` (boolean)
    True if all the resources in the Virtual Machine Protection Group needs to be poweredon after restore.
Required only in case of alternate datastore restore.

  - `recoveryInfo` (array)
    Recovery point information.

  - `recoveryInfo.recoveryPointId` (string)
    UUID string uniquely identifying the recovery point.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641yd"

  - `recoveryInfo.recoveryPointType` (string)
    The type of the recovery point.
    Enum: "SNAPSHOT", "BACKUP", "CLOUDBACKUP"

  - `recoveryInfo.resourceId` (string)
    UUID string uniquely identifying the individual asset in the protection group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `recoveryInfo.targetInfoOverrides` (object)
    Provides the details about target VM location, compute, etc.  These inputs are required only if the restore type is 'ALTERNATE' and if any properties provided in the targetInfo needs to be overwritten.

  - `recoveryInfo.targetInfoOverrides.appInfo` (object)
    Hypervisor specific information.

  - `recoveryInfo.targetInfoOverrides.appInfo.vmware` (object)
    VMware specific app info.

  - `recoveryInfo.targetInfoOverrides.appInfo.vmware.datastoreId` (string)
    Specifies the destination datastore in case of
alternate restore.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `recoveryInfo.targetInfoOverrides.appInfo.vmware.resourcePoolId` (string)
    To specify a destination resource pool.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `recoveryInfo.targetInfoOverrides.clusterId` (string)
    The target hypervisor cluster onto which the new virtual machine is hosted.
Either hostId or clusterId has to be provided as input.
Both can not be specified at the same time.

  - `recoveryInfo.targetInfoOverrides.folderId` (string)
    UUID string uniquely identifying the hypervisor folder.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `recoveryInfo.targetInfoOverrides.hostId` (string)
    UUID string uniquely identifying the hypervisor host.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `recoveryInfo.targetInfoOverrides.powerOn` (boolean)
    True if the new VM to be powered on after successful creation.

  - `recoveryInfo.targetInfoOverrides.storageInfo` (object)
    Target storage information required to provision the new storage,
required only in case of alternate datastore restore.

  - `recoveryInfo.targetInfoOverrides.storageInfo.storageSystemId` (string)
    Target storage system where the new volumes will be provisioned in case of alternate restore.

  - `restoreAllResources` (boolean)
    True if all the resources in the Virtual Machine Protection Group needs to be restored.

  - `restoreType` (string)
    Specifies the type of restore needs to be performed.
    Enum: "PARENT", "ALTERNATE"

  - `targetInfo` (object)
    Provides the details about target VM location, compute, etc. These inputs are required only if the restore type is 'ALTERNATE'.

  - `targetInfo.hypervisorManagerId` (string)
    UUID string uniquely identifying the hypervisor manager.
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


