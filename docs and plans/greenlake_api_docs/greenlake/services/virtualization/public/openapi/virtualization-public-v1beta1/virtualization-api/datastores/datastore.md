---
title: "GET /virtualization/v1beta1/datastores/{datastore-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/datastores/datastore.md"
scraped_at: "2026-06-07T06:16:28.270620+00:00Z"
---

# Get a datastore identified by {datastore-id}

Details of a datastore

Endpoint: GET /virtualization/v1beta1/datastores/{datastore-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `datastore-id` (string, required)
    UUID string uniquely identifying the datastore
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the datastore
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created.

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `allowedOperations` (array)
    List of allowed operation on the datastore.
    Enum: "DATASTORE_CREATE", "DATASTORE_DELETE", "DATASTORE_BACKUP_CREATE", "DATASTORE_BACKUP_UPDATE", "DATASTORE_BACKUP_DELETE", "DATASTORE_SNAPSHOT_CREATE", "DATASTORE_SNAPSHOT_UPDATE", "DATASTORE_SNAPSHOT_DELETE", "DATASTORE_RESTORE"

  - `appType` (string)
    Application type of this asset
    Enum: "VMWARE"

  - `capacityFree` (integer)
    Unused storage of the datastore in bytes.
    Example: 76534

  - `capacityInBytes` (integer)
    Size of the datastore in bytes.
    Example: 2407653459860

  - `capacityUncommitted` (integer)
    Uncommitted storage of the datastore in bytes.
    Example: 653422

  - `clusterInfo` (object)

  - `clusterInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.

  - `clusterInfo.id` (string)
    UUID string uniquely identifying the hypervisor cluster.

  - `clusterInfo.name` (string)
    Name of the cluster as reported by the hypervisor manager.

  - `clusterInfo.resourceUri` (string)
    The URI reference for this resource.

  - `customerId` (string)
    The customer application identifier.

  - `datacentersInfo` (array)
    List of datacenters to which the datastore is presented to.

  - `datacentersInfo.id` (string)
    UUID string uniquely identifier of the datacenter.
    Example: "16245bf7-2b35-5580-86a6-620faa5b5403"

  - `datacentersInfo.moref` (string)
    VMware provided moref for the datacenter.
    Example: "datacenter-2"

  - `datacentersInfo.name` (string)
    VMware provided name for the datacenter.
    Example: "core-team-dc"

  - `datastoreClassification` (string)
    Classification of datastore types for which protection will be disabled
    Enum: "PROTECTION_STORE_GATEWAY"

  - `datastoreType` (string)
    Type of the datastore.
    Enum: "VMFS", "VVOL", "NFS", "VSAN"

  - `displayName` (string)
    A user-friendly name that identifies the datastore.
    Example: "Nimble-DS1"

  - `folderInfo` (object)
    The immediate parent folder on which this resource is hosted in the inventory of hypervisor-manager.

  - `folderInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor folder. This will always be same as name since adding or updating hypervisor folders is not supported when managed from a manager, such as the vCenter.

  - `folderInfo.id` (string)
    UUID string uniquely identifying the hypervisor folder.

  - `folderInfo.name` (string)
    Name of the folder as reported by the hypervisor manager.

  - `hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.
    Example: "754f63f7-1016-40ec-9b8f-610f978b9aec"

  - `hostsInfo` (array)
    List of hypervisor hosts to which the datastore is presented to.

  - `hostsInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.

  - `hostsInfo.id` (string)
    UUID string uniquely identifying the hypervisor host.

  - `hostsInfo.name` (string)
    Name of the host as reported by the hypervisor manager.

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `moref` (string)
    VMware provided moref of the data store
    Example: "datastore-1234"

  - `name` (string)
    Name of the datastore as reported by the hypervisor manager.
    Example: "Nimble-DS2"

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

  - `protectionPolicyAppliedAtInfo` (object)
    Describes applied protection policy information.

  - `protectionPolicyAppliedAtInfo.id` (string)
    UUID string uniquely identifying the protection policy.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `protectionPolicyAppliedAtInfo.name` (string)
    Name of the protection policy.
    Example: "ProtectionPolicy1"

  - `protectionPolicyAppliedAtInfo.type` (string)
    Type of the protection policy.
    Enum: "DATASTORE", "VIRTUAL_MACHINE", "VM_PROTECTION_GROUP"

  - `protectionStatus` (string)
    Provides the current protection status of this resource. - UNPROTECTED - No policy assigned, No recovery points exists - LAPSED      - No policy assigned, at least one recovery points exists - PENDING     - Policy assigned, No recovery points exists - PARTIAL     - Policy assigned, At least one recovery point exists - PROTECTED   - Policy assigned, most recent run of every configured schedule is successful - PAUSED      - Policy assigned, one or more of the schedules are paused - UNSUPPORTED - No policy can be assigned
    Enum: "UNPROTECTED", "LAPSED", "PENDING", "PARTIAL", "PROTECTED", "PAUSED", "UNSUPPORTED"

  - `provisioningPolicyInfo` (object)
    Describes provisioning policy information.

  - `provisioningPolicyInfo.id` (string)
    UUID string uniquely identifying the provisioning policy.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `provisioningPolicyInfo.name` (string)
    Name of the provisioning policy.
    Example: "ProvisioningPolicy1"

  - `provisioningPolicyInfo.type` (string)
    The type of the resource

  - `recoveryPointsExist` (boolean)
    Indicates at least one valid recovery point exists for this resource.

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

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/datastores/{datastore-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the datastore
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "MOUNTED", "DELETED"

  - `stateReason` (string)
    Brief reason for the current state of the datastore

  - `status` (string)
    The current status of the datastore.
    Enum: "OK", "ERROR", "WARNING"

  - `uid` (string)
    VMware provided uuid of the datastore.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `vmCount` (integer)
    Number of virtual machines associated with the datastore.
    Example: 120

  - `vmProtectionGroupsInfo` (array)
    List of virtual machine protection groups.

  - `vmProtectionGroupsInfo.id` (string)
    Unique identifier for the Protection Group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `vmProtectionGroupsInfo.name` (string)
    Name of the Protection Group.
    Example: "myProtectionGroup"

  - `volumesInfo` (array)
    Volumes associated with datastore.

  - `volumesInfo.displayName` (string)
    A user-friendly name that identifies the volume.

  - `volumesInfo.id` (string)
    UUID string uniquely identifying the volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumesInfo.name` (string)
    Name of the volume.
    Example: "Volume1"

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


