---
title: "GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongroup.md"
scraped_at: "2026-06-07T06:14:18.031708+00:00Z"
---

# Get a virtual machine Protection Group resource.

Get detailed information for a registered virtual machine Protection Group qualified by id.

Endpoint: GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.
    Example: "backup-recovery/virtual-machine-protection-group"

  - `appType` (string)
    Type of the application to which the vm-protection-group belongs.
    Enum: "VMWARE"

  - `assets` (array)
    Captures the list of assets that would be part of the protection group.

  - `assets.displayName` (string)
    Name provided for the asset.

  - `assets.id` (string)
    Asset identifier

  - `assets.name` (string)
    Name provided for the asset.

  - `assets.resourceUri` (string)
    self reference to resource.
    Example: "/backup-recovery/v1beta1/datastores/id"

  - `assets.type` (string)
    type of the asset.
    Example: "virtualization/datastore"

  - `assetsCategory` (string)
    The type of the protected assets.
    Enum: "VVOL_VMS", "VMFS_DATASTORES", "VMFS_VMS"

  - `consoleUri` (string)
    The URI for console screen that displays this object.

  - `createdAt` (string)
    Time in UTC at which the object was created.

  - `customerId` (string)
    The customer application identifier

  - `dataOrchestratorInfo` (array)

  - `dataOrchestratorInfo.id` (string)
    The id of the Data Orchestrator.

  - `dataOrchestratorInfo.resourceUri` (string)
    Example: "/backup-recovery/v1beta1/data-orchestrators/613a8115-00f4-4785-831f-f3b2183cdcb7"

  - `dataOrchestratorInfo.type` (string)
    Example: "backup-recovery/data-orchestrator"

  - `description` (string)
    A brief description of the Protection Group.

  - `displayName` (string)
    User-defined name given to the Protection Group.
    Example: "myProtectionGroup"

  - `dynamicMemberFilter` (object)

  - `dynamicMemberFilter.members` (array)
    Tags associated with the Protection Group.

  - `dynamicMemberFilter.members.categoryName` (string)
    The category name is unique to the currently selected hypervisor manager.

  - `dynamicMemberFilter.members.name` (string)
    Name of the Tag.
    Example: "Tag name"

  - `dynamicMemberFilter.members.resourceUri` (string)
    Resource uri of the Tag.
    Example: "/virtualization/v1beta1/hypervisor-managers/17f83a4d-bfac-4a92-a009-ac3167fdd83b/tags/651de0d6-9b15-5dd0-b466-1fd4da410200"

  - `dynamicMemberFilter.members.state` (string)
    Enum: "OK", "DELETED"

  - `dynamicMemberFilter.members.type` (string)
    Type of the Tag.
    Example: "virtualization/hypervisor-tag"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `hypervisorManagerInfo.name` (string)
    User defined name for the hypervisor manager.
    Example: "vcenter123.hpe.com"

  - `hypervisorManagerInfo.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/id/"

  - `hypervisorManagerInfo.type` (string)
    Type of the resource.
    Example: "virtualization/hypervisor-manager"

  - `name` (string)
    A user-friendly name to identify Virtual Machine protection group.
    Example: "myProtectionGroup"

  - `nativeAppInfo` (object)

  - `nativeAppInfo.id` (string)
    UUID string uniquely identifying the native group. For example in case of VMware folder it will be id of the folder.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `nativeAppInfo.name` (string)
    If the protection group is a folder or vVol Container then name as reported by the hypervisor manager.
    Example: "myVmFolder"

  - `nativeAppInfo.type` (string)
    type of the native protection group.
    Enum: "VMWARE_FOLDER", "VMWARE_VVOL_CONTAINER", "STORAGE_REPLICATION_GROUP"

  - `protectedResourcesInfo` (object)

  - `protectedResourcesInfo.virtualMachinesCount` (integer)
    Count of virtual machines which are protected with this group.
VM protection is considered incomplete when it has disks from
multiple datastores or has RDM and it is protected as part of a custom
group. This count gets updated after every snapshot creation.
    Example: 5

  - `protectionJobInfo` (object)
    Information about the assigned Protection Policy and the Protection Job.

  - `protectionJobInfo.id` (string)
    UUID string uniquely identifying the Protection Job.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `protectionJobInfo.name` (string)
    name of the Protection Job.

  - `protectionJobInfo.protectionPolicyInfo` (object)
    Information about the Protection Policy that was used to create the job.

  - `protectionJobInfo.protectionPolicyInfo.id` (string)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `protectionJobInfo.protectionPolicyInfo.name` (string)
    User defined name of the Protection Policy.
    Example: "Gold-Protection-Policy"

  - `protectionJobInfo.protectionPolicyInfo.resourceUri` (string)
    Reference to resource

  - `protectionJobInfo.resourceUri` (string)
    Reference to resource.

  - `replicationInfo` (object)
    Replication groups information containing details of all replication partners. Applicable only for Protection Group type 'STORAGE_REPLICATION_GROUP'

  - `replicationInfo.id` (string)
    Id of the replication group.

  - `replicationInfo.name` (string)
    Name of the replication group.

  - `replicationInfo.partnerDetails` (array)
    List of Volumes associated with vm protection group.

  - `replicationInfo.partnerDetails.id` (string)
    Id of the storage system, applicable only for Nimble storage systems

  - `replicationInfo.partnerDetails.mode` (string)
    Replication Mode
    Enum: "SYNCHRONOUS", "PERIODIC"

  - `replicationInfo.partnerDetails.name` (string)
    Name of the replication partner Array

  - `replicationInfo.partnerDetails.systemWwn` (string)
    storage system wwn in case of Primera

  - `replicationInfo.partnerDetails.vendorName` (string)
    Vendor name
    Enum: "NIMBLE", "PRIMERA"

  - `replicationInfo.resourceUri` (string)
    Uri representing replication group in Storage Fleet
    Example: "/storage-fleet/v1/storage-systems/{uuid}/volume-sets"

  - `replicationInfo.type` (string)
    type representing volume-set in Storage Fleet
    Example: "storage-fleet/volume-set"

  - `state` (string)
    Current state of the group.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING"

  - `stateReason` (string)
    Brief reason for the current state of the group.

  - `status` (string)
    Current status of the group.
    Enum: "OK", "ERROR", "WARNING"

  - `updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `vmProtectionGroupType` (string)
    The type of the Protection Group. This can be Native for storage system specific constructs like StorageReplicationGroup or application specific constructs such as VMware Folder or vVol container.  Custom if its just a collection of assets (Virtual Machine, Datastores etc).
    Enum: "NATIVE", "CUSTOM", "DYNAMIC"

  - `volumesInfo` (array)
    List of Volumes associated with vm protection group.

  - `volumesInfo.displayName` (string)
    A user-friendly name that identifies the volume.

  - `volumesInfo.id` (string)
    UUID string uniquely identifying the volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesInfo.name` (string)
    Name of the volume.
    Example: "Volume1"

  - `volumesInfo.resourceUri` (string)
    The URI reference for this resource.

  - `volumesInfo.scsiIdentifier` (string)
    SCSI identifier of the volume or snapshot .
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `volumesInfo.sizeInBytes` (integer)
    Size of the volume or snapshot in bytes.
    Example: 2407653459860

  - `volumesInfo.storageFolderInfo` (object)
    Information of storage folder.

  - `volumesInfo.storageFolderInfo.displayName` (string)
    A user-friendly name that identifies the storage folder.

  - `volumesInfo.storageFolderInfo.id` (string)
    UUID string uniquely identifying the storage folder.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesInfo.storageFolderInfo.name` (string)
    Name of the storage folder.

  - `volumesInfo.storageFolderInfo.type` (string)
    Type of storage folder.

  - `volumesInfo.storagePoolInfo` (object)
    Describes a storage pool.

  - `volumesInfo.storagePoolInfo.displayName` (string)
    A user-friendly name that identifies the storage pool.

  - `volumesInfo.storagePoolInfo.id` (string)
    UUID string uniquely identifying the storage pool.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesInfo.storagePoolInfo.name` (string)
    Name of the storage pool.

  - `volumesInfo.storagePoolInfo.type` (string)
    Type of storage pool.

  - `volumesInfo.storageSystemInfo` (object)
    Describes a storage system.

  - `volumesInfo.storageSystemInfo.displayName` (string)
    A user-friendly name that identifies the storage system.
    Example: "my-dev-3par1.ind.hpecorp.net"

  - `volumesInfo.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesInfo.storageSystemInfo.managed` (boolean)
    Specify if the storage system is registered.

  - `volumesInfo.storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `volumesInfo.storageSystemInfo.serialNumber` (string)
    Serial number of the storage system.
    Example: "AF-10122"

  - `volumesInfo.storageSystemInfo.type` (string)
    Type of storage system.
    Enum: "NIMBLE", "THREEPAR", "PRIMERA", "ALLETRA_6000", "ALLETRA_9000"

  - `volumesInfo.storageSystemInfo.vendorName` (string)
    Storage system provider name.
    Example: "hpe"

  - `volumesInfo.type` (string)
    Type of volume.

  - `volumesInfo.volumeSetInfo` (object)
    Describes a volume set.

  - `volumesInfo.volumeSetInfo.displayName` (string)
    A user-friendly name that identifies the volume set.

  - `volumesInfo.volumeSetInfo.id` (string)
    UUID string uniquely identifying the volume set.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesInfo.volumeSetInfo.name` (string)
    Name of the volume set.

  - `volumesInfo.volumeSetInfo.type` (string)
    Type of the volume set.

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


