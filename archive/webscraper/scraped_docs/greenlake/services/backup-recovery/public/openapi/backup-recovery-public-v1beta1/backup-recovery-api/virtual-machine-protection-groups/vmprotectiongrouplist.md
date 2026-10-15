---
title: "GET /backup-recovery/v1beta1/virtual-machine-protection-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-protection-groups/vmprotectiongrouplist.md"
scraped_at: "2026-06-07T06:14:06.078304+00:00Z"
---

# Get all  virtual machine Protection Groups.

List all virtual machine Protection Groups.

Endpoint: GET /backup-recovery/v1beta1/virtual-machine-protection-groups
Version: 1.1.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to omit from the beginning of the result set. The offset and limit query parameters are used in conjunction with pagination. For example "offset=30&limit=10" indicates the fourth page of 10 items.

  - `limit` (integer)
    The maximum number of items to include in the response. The offset and limit query parameters are used in conjunction for pagination, for example "offset=30&limit=10" indicates the fourth page of 10 items.

  - `filter` (string)
    An expression by which to filter the results.

A comparison compares a property name to a literal. The following comparisons are supported:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties.
* “in” : Is a value in a property (that is an array of strings).
example: vmProtectionGroupType eq 'NATIVE'

Filters are supported on the following attributes:
* hypervisorManagerInfo/name
* hypervisorManagerInfo/id
* vmProtectionGroupType
* dataOrchestratorInfo/id
* createdAt
* name

  - `sort` (string)
    Comma separated list of properties defining the sort order. Each item in the “sort” query parameter is a property name optionally followed by a direction indicator. The direction indicator may only be either “asc” (ascending) or “desc” (descending). If no direction indicator is specified, the default order is ascending.

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client
formatted as an exclusive comma separated list of properties. If not specified, all properties are returned.

## Response 200 fields (application/json):

  - `count` (integer, required)
    The number of resources in the items array.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the Virtual Machine Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.
    Example: "backup-recovery/virtual-machine-protection-group"

  - `items.appType` (string)
    Type of the application to which the vm-protection-group belongs.
    Enum: "VMWARE"

  - `items.assets` (array)
    Captures the list of assets that would be part of the protection group.

  - `items.assets.displayName` (string)
    Name provided for the asset.

  - `items.assets.id` (string)
    Asset identifier

  - `items.assets.name` (string)
    Name provided for the asset.

  - `items.assets.resourceUri` (string)
    self reference to resource.
    Example: "/backup-recovery/v1beta1/datastores/id"

  - `items.assets.type` (string)
    type of the asset.
    Example: "virtualization/datastore"

  - `items.assetsCategory` (string)
    The type of the protected assets.
    Enum: "VVOL_VMS", "VMFS_DATASTORES", "VMFS_VMS"

  - `items.consoleUri` (string)
    The URI for console screen that displays this object.

  - `items.createdAt` (string)
    Time in UTC at which the object was created.

  - `items.customerId` (string)
    The customer application identifier

  - `items.dataOrchestratorInfo` (array)

  - `items.dataOrchestratorInfo.id` (string)
    The id of the Data Orchestrator.

  - `items.dataOrchestratorInfo.resourceUri` (string)
    Example: "/backup-recovery/v1beta1/data-orchestrators/613a8115-00f4-4785-831f-f3b2183cdcb7"

  - `items.dataOrchestratorInfo.type` (string)
    Example: "backup-recovery/data-orchestrator"

  - `items.description` (string)
    A brief description of the Protection Group.

  - `items.displayName` (string)
    User-defined name given to the Protection Group.
    Example: "myProtectionGroup"

  - `items.dynamicMemberFilter` (object)

  - `items.dynamicMemberFilter.members` (array)
    Tags associated with the Protection Group.

  - `items.dynamicMemberFilter.members.categoryName` (string)
    The category name is unique to the currently selected hypervisor manager.

  - `items.dynamicMemberFilter.members.name` (string)
    Name of the Tag.
    Example: "Tag name"

  - `items.dynamicMemberFilter.members.resourceUri` (string)
    Resource uri of the Tag.
    Example: "/virtualization/v1beta1/hypervisor-managers/17f83a4d-bfac-4a92-a009-ac3167fdd83b/tags/651de0d6-9b15-5dd0-b466-1fd4da410200"

  - `items.dynamicMemberFilter.members.state` (string)
    Enum: "OK", "DELETED"

  - `items.dynamicMemberFilter.members.type` (string)
    Type of the Tag.
    Example: "virtualization/hypervisor-tag"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.hypervisorManagerInfo.name` (string)
    User defined name for the hypervisor manager.
    Example: "vcenter123.hpe.com"

  - `items.hypervisorManagerInfo.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/id/"

  - `items.hypervisorManagerInfo.type` (string)
    Type of the resource.
    Example: "virtualization/hypervisor-manager"

  - `items.name` (string)
    A user-friendly name to identify Virtual Machine protection group.
    Example: "myProtectionGroup"

  - `items.nativeAppInfo` (object)

  - `items.nativeAppInfo.id` (string)
    UUID string uniquely identifying the native group. For example in case of VMware folder it will be id of the folder.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.nativeAppInfo.name` (string)
    If the protection group is a folder or vVol Container then name as reported by the hypervisor manager.
    Example: "myVmFolder"

  - `items.nativeAppInfo.type` (string)
    type of the native protection group.
    Enum: "VMWARE_FOLDER", "VMWARE_VVOL_CONTAINER", "STORAGE_REPLICATION_GROUP"

  - `items.protectedResourcesInfo` (object)

  - `items.protectedResourcesInfo.virtualMachinesCount` (integer)
    Count of virtual machines which are protected with this group.
VM protection is considered incomplete when it has disks from
multiple datastores or has RDM and it is protected as part of a custom
group. This count gets updated after every snapshot creation.
    Example: 5

  - `items.protectionJobInfo` (object)
    Information about the assigned Protection Policy and the Protection Job.

  - `items.protectionJobInfo.id` (string)
    UUID string uniquely identifying the Protection Job.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.protectionJobInfo.name` (string)
    name of the Protection Job.

  - `items.protectionJobInfo.protectionPolicyInfo` (object)
    Information about the Protection Policy that was used to create the job.

  - `items.protectionJobInfo.protectionPolicyInfo.id` (string)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.protectionJobInfo.protectionPolicyInfo.name` (string)
    User defined name of the Protection Policy.
    Example: "Gold-Protection-Policy"

  - `items.protectionJobInfo.protectionPolicyInfo.resourceUri` (string)
    Reference to resource

  - `items.protectionJobInfo.resourceUri` (string)
    Reference to resource.

  - `items.replicationInfo` (object)
    Replication groups information containing details of all replication partners. Applicable only for Protection Group type 'STORAGE_REPLICATION_GROUP'

  - `items.replicationInfo.id` (string)
    Id of the replication group.

  - `items.replicationInfo.name` (string)
    Name of the replication group.

  - `items.replicationInfo.partnerDetails` (array)
    List of Volumes associated with vm protection group.

  - `items.replicationInfo.partnerDetails.id` (string)
    Id of the storage system, applicable only for Nimble storage systems

  - `items.replicationInfo.partnerDetails.mode` (string)
    Replication Mode
    Enum: "SYNCHRONOUS", "PERIODIC"

  - `items.replicationInfo.partnerDetails.name` (string)
    Name of the replication partner Array

  - `items.replicationInfo.partnerDetails.systemWwn` (string)
    storage system wwn in case of Primera

  - `items.replicationInfo.partnerDetails.vendorName` (string)
    Vendor name
    Enum: "NIMBLE", "PRIMERA"

  - `items.replicationInfo.resourceUri` (string)
    Uri representing replication group in Storage Fleet
    Example: "/storage-fleet/v1/storage-systems/{uuid}/volume-sets"

  - `items.replicationInfo.type` (string)
    type representing volume-set in Storage Fleet
    Example: "storage-fleet/volume-set"

  - `items.state` (string)
    Current state of the group.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING"

  - `items.stateReason` (string)
    Brief reason for the current state of the group.

  - `items.status` (string)
    Current status of the group.
    Enum: "OK", "ERROR", "WARNING"

  - `items.updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `items.vmProtectionGroupType` (string)
    The type of the Protection Group. This can be Native for storage system specific constructs like StorageReplicationGroup or application specific constructs such as VMware Folder or vVol container.  Custom if its just a collection of assets (Virtual Machine, Datastores etc).
    Enum: "NATIVE", "CUSTOM", "DYNAMIC"

  - `items.volumesInfo` (array)
    List of Volumes associated with vm protection group.

  - `items.volumesInfo.displayName` (string)
    A user-friendly name that identifies the volume.

  - `items.volumesInfo.id` (string)
    UUID string uniquely identifying the volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesInfo.name` (string)
    Name of the volume.
    Example: "Volume1"

  - `items.volumesInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.volumesInfo.scsiIdentifier` (string)
    SCSI identifier of the volume or snapshot .
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.volumesInfo.sizeInBytes` (integer)
    Size of the volume or snapshot in bytes.
    Example: 2407653459860

  - `items.volumesInfo.storageFolderInfo` (object)
    Information of storage folder.

  - `items.volumesInfo.storageFolderInfo.displayName` (string)
    A user-friendly name that identifies the storage folder.

  - `items.volumesInfo.storageFolderInfo.id` (string)
    UUID string uniquely identifying the storage folder.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesInfo.storageFolderInfo.name` (string)
    Name of the storage folder.

  - `items.volumesInfo.storageFolderInfo.type` (string)
    Type of storage folder.

  - `items.volumesInfo.storagePoolInfo` (object)
    Describes a storage pool.

  - `items.volumesInfo.storagePoolInfo.displayName` (string)
    A user-friendly name that identifies the storage pool.

  - `items.volumesInfo.storagePoolInfo.id` (string)
    UUID string uniquely identifying the storage pool.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesInfo.storagePoolInfo.name` (string)
    Name of the storage pool.

  - `items.volumesInfo.storagePoolInfo.type` (string)
    Type of storage pool.

  - `items.volumesInfo.storageSystemInfo` (object)
    Describes a storage system.

  - `items.volumesInfo.storageSystemInfo.displayName` (string)
    A user-friendly name that identifies the storage system.
    Example: "my-dev-3par1.ind.hpecorp.net"

  - `items.volumesInfo.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesInfo.storageSystemInfo.managed` (boolean)
    Specify if the storage system is registered.

  - `items.volumesInfo.storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `items.volumesInfo.storageSystemInfo.serialNumber` (string)
    Serial number of the storage system.
    Example: "AF-10122"

  - `items.volumesInfo.storageSystemInfo.type` (string)
    Type of storage system.
    Enum: "NIMBLE", "THREEPAR", "PRIMERA", "ALLETRA_6000", "ALLETRA_9000"

  - `items.volumesInfo.storageSystemInfo.vendorName` (string)
    Storage system provider name.
    Example: "hpe"

  - `items.volumesInfo.type` (string)
    Type of volume.

  - `items.volumesInfo.volumeSetInfo` (object)
    Describes a volume set.

  - `items.volumesInfo.volumeSetInfo.displayName` (string)
    A user-friendly name that identifies the volume set.

  - `items.volumesInfo.volumeSetInfo.id` (string)
    UUID string uniquely identifying the volume set.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesInfo.volumeSetInfo.name` (string)
    Name of the volume set.

  - `items.volumesInfo.volumeSetInfo.type` (string)
    Type of the volume set.

  - `offset` (integer, required)
    The offset specified in the offset query parameter.

  - `total` (integer)
    The total count of objects in the result set.

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


