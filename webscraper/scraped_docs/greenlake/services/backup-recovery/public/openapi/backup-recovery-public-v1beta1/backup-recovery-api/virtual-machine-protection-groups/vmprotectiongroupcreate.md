---
title: "POST /backup-recovery/v1beta1/virtual-machine-protection-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroupcreate.md"
scraped_at: "2026-06-07T06:14:06.217571+00:00Z"
---

# Create a new virtual machine Protection Group.

Create the virtual machine Protection Group for data management.

Endpoint: POST /backup-recovery/v1beta1/virtual-machine-protection-groups
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `name` (string, required)
    A user-friendly name to identify Virtual Machine protection group.

  - `vmProtectionGroupType` (string, required)
    The type of the Protection Group. This can be Native for storage system specific constructs like StorageReplicationGroup or application specific constructs such as VMware Folder or vVol container.  Custom if its just a collection of assets (Virtual Machine, Datastores etc).
    Enum: "NATIVE", "CUSTOM", "DYNAMIC"

  - `assetsCategory` (string, required)
    The type of the protected assets.
    Enum: "VVOL_VMS", "VMFS_DATASTORES", "VMFS_VMS"

  - `assets` (array)
    Captures the list of assets that would be part of the protection group.

  - `assets.id` (string)
    Asset identifier.

  - `assets.type` (string)
    type of the asset.
    Example: "virtualization/datastore"

  - `description` (string)
    A brief description of the Protection Group.

  - `dynamicMemberFilter` (object)

  - `dynamicMemberFilter.members` (array)
    Tags associated with the Protection Group.

  - `dynamicMemberFilter.members.name` (string)
    Name of the Tag.
    Example: "Tag name"

  - `dynamicMemberFilter.members.resourceUri` (string)
    Resource uri of the Tag.
    Example: "/virtualization/v1beta1/hypervisor-managers/17f83a4d-bfac-4a92-a009-ac3167fdd83b/tags/651de0d6-9b15-5dd0-b466-1fd4da410200"

  - `dynamicMemberFilter.members.type` (string)
    Type of the Tag.

  - `nativeAppInfo` (object)

  - `nativeAppInfo.id` (string)
    UUID string uniquely identifying the native group. For example in case of VMware folder it will be id of the folder.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `nativeAppInfo.type` (string)
    type of the native protection group.
    Enum: "VMWARE_FOLDER", "VMWARE_VVOL_CONTAINER", "STORAGE_REPLICATION_GROUP"

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


