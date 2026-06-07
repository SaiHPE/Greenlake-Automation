---
title: "GET /virtualization/v1beta1/datastores"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/datastores/datastoreslist.md"
scraped_at: "2026-06-07T06:16:28.041328+00:00Z"
---

# Get all datastores across registered hypervisor managers.

List all the datastores across registered hypervisor managers.

Endpoint: GET /virtualization/v1beta1/datastores
Version: 1.2.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set

  - `limit` (integer)
    The numbers of items to return

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.
The returned set of resources must match the criteria in the filter query parameter.

A comparison compares a property name to a literal. The following comparisons are supported:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “ne” : Is a property not equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /virtualization/v1beta1/datastores?filter="datastoreType eq VMFS"
* GET /virtualization/v1beta1/datastores?filter="datastoreType eq VMFS and status eq ERROR"

Filters are supported on the following attributes:
* status
* state
* appType
* hypervisorManagerInfo/name
* hypervisorManagerInfo/displayName
* hypervisorManagerInfo/id
* hostsInfo/id
* hostsInfo/name
* hostsInfo/displayName
* clusterInfo/id
* clusterInfo/name
* clusterInfo/displayName
* protectionJobInfo/protectionPolicyInfo/id
* protectionJobInfo/protectionPolicyInfo/name
* vmProtectionGroupsInfo/id
* vmProtectionGroupsInfo/name
* volumesInfo/id
* volumesInfo/storageSystemInfo/id
* volumesInfo/storageSystemInfo/serialNumber
* volumesInfo/storageSystemInfo/name
* volumesInfo/storageSystemInfo/vendorName
* volumesInfo/storageFolderInfo/id
* volumesInfo/storageFolderInfo/name
* volumesInfo/storagePoolInfo/id
* volumesInfo/storagePoolInfo/name
* datastoreType
* createdAt
* name
* services
* allowedOperations
* capacityInBytes
* capacityFree
* displayName
* replicationInfo/name
* replicationInfo/id
* hciClusterUuid

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified, the
default order is ascending.

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the datastore
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created.

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `items.allowedOperations` (array)
    List of allowed operation on the datastore.
    Enum: "DATASTORE_CREATE", "DATASTORE_DELETE", "DATASTORE_BACKUP_CREATE", "DATASTORE_BACKUP_UPDATE", "DATASTORE_BACKUP_DELETE", "DATASTORE_SNAPSHOT_CREATE", "DATASTORE_SNAPSHOT_UPDATE", "DATASTORE_SNAPSHOT_DELETE", "DATASTORE_RESTORE"

  - `items.appType` (string)
    Application type of this asset
    Enum: "VMWARE"

  - `items.capacityFree` (integer)
    Unused storage of the datastore in bytes.
    Example: 76534

  - `items.capacityInBytes` (integer)
    Size of the datastore in bytes.
    Example: 2407653459860

  - `items.capacityUncommitted` (integer)
    Uncommitted storage of the datastore in bytes.
    Example: 653422

  - `items.clusterInfo` (object)

  - `items.clusterInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.

  - `items.clusterInfo.id` (string)
    UUID string uniquely identifying the hypervisor cluster.

  - `items.clusterInfo.name` (string)
    Name of the cluster as reported by the hypervisor manager.

  - `items.clusterInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.customerId` (string)
    The customer application identifier.

  - `items.datacentersInfo` (array)
    List of datacenters to which the datastore is presented to.

  - `items.datacentersInfo.id` (string)
    UUID string uniquely identifier of the datacenter.
    Example: "16245bf7-2b35-5580-86a6-620faa5b5403"

  - `items.datacentersInfo.moref` (string)
    VMware provided moref for the datacenter.
    Example: "datacenter-2"

  - `items.datacentersInfo.name` (string)
    VMware provided name for the datacenter.
    Example: "core-team-dc"

  - `items.datastoreClassification` (string)
    Classification of datastore types for which protection will be disabled
    Enum: "PROTECTION_STORE_GATEWAY"

  - `items.datastoreType` (string)
    Type of the datastore.
    Enum: "VMFS", "VVOL", "NFS", "VSAN"

  - `items.displayName` (string)
    A user-friendly name that identifies the datastore.
    Example: "Nimble-DS1"

  - `items.folderInfo` (object)
    The immediate parent folder on which this resource is hosted in the inventory of hypervisor-manager.

  - `items.folderInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor folder. This will always be same as name since adding or updating hypervisor folders is not supported when managed from a manager, such as the vCenter.

  - `items.folderInfo.id` (string)
    UUID string uniquely identifying the hypervisor folder.

  - `items.folderInfo.name` (string)
    Name of the folder as reported by the hypervisor manager.

  - `items.hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.
    Example: "754f63f7-1016-40ec-9b8f-610f978b9aec"

  - `items.hostsInfo` (array)
    List of hypervisor hosts to which the datastore is presented to.

  - `items.hostsInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.

  - `items.hostsInfo.id` (string)
    UUID string uniquely identifying the hypervisor host.

  - `items.hostsInfo.name` (string)
    Name of the host as reported by the hypervisor manager.

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `items.hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `items.moref` (string)
    VMware provided moref of the data store
    Example: "datastore-1234"

  - `items.name` (string)
    Name of the datastore as reported by the hypervisor manager.
    Example: "Nimble-DS2"

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

  - `items.protectionPolicyAppliedAtInfo` (object)
    Describes applied protection policy information.

  - `items.protectionPolicyAppliedAtInfo.id` (string)
    UUID string uniquely identifying the protection policy.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.protectionPolicyAppliedAtInfo.name` (string)
    Name of the protection policy.
    Example: "ProtectionPolicy1"

  - `items.protectionPolicyAppliedAtInfo.type` (string)
    Type of the protection policy.
    Enum: "DATASTORE", "VIRTUAL_MACHINE", "VM_PROTECTION_GROUP"

  - `items.protectionStatus` (string)
    Provides the current protection status of this resource. - UNPROTECTED - No policy assigned, No recovery points exists - LAPSED      - No policy assigned, at least one recovery points exists - PENDING     - Policy assigned, No recovery points exists - PARTIAL     - Policy assigned, At least one recovery point exists - PROTECTED   - Policy assigned, most recent run of every configured schedule is successful - PAUSED      - Policy assigned, one or more of the schedules are paused - UNSUPPORTED - No policy can be assigned
    Enum: "UNPROTECTED", "LAPSED", "PENDING", "PARTIAL", "PROTECTED", "PAUSED", "UNSUPPORTED"

  - `items.provisioningPolicyInfo` (object)
    Describes provisioning policy information.

  - `items.provisioningPolicyInfo.id` (string)
    UUID string uniquely identifying the provisioning policy.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.provisioningPolicyInfo.name` (string)
    Name of the provisioning policy.
    Example: "ProvisioningPolicy1"

  - `items.provisioningPolicyInfo.type` (string)
    The type of the resource

  - `items.recoveryPointsExist` (boolean)
    Indicates at least one valid recovery point exists for this resource.

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

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/datastores/{datastore-id}"

  - `items.services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `items.state` (string)
    The current state of the datastore
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "MOUNTED", "DELETED"

  - `items.stateReason` (string)
    Brief reason for the current state of the datastore

  - `items.status` (string)
    The current status of the datastore.
    Enum: "OK", "ERROR", "WARNING"

  - `items.uid` (string)
    VMware provided uuid of the datastore.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.vmCount` (integer)
    Number of virtual machines associated with the datastore.
    Example: 120

  - `items.vmProtectionGroupsInfo` (array)
    List of virtual machine protection groups.

  - `items.vmProtectionGroupsInfo.id` (string)
    Unique identifier for the Protection Group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.vmProtectionGroupsInfo.name` (string)
    Name of the Protection Group.
    Example: "myProtectionGroup"

  - `items.volumesInfo` (array)
    Volumes associated with datastore.

  - `items.volumesInfo.displayName` (string)
    A user-friendly name that identifies the volume.

  - `items.volumesInfo.id` (string)
    UUID string uniquely identifying the volume.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.volumesInfo.name` (string)
    Name of the volume.
    Example: "Volume1"

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
    The number of items to skip before starting to collect the result set

  - `total` (integer)
    Total number of documents matching filter criteria.

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


