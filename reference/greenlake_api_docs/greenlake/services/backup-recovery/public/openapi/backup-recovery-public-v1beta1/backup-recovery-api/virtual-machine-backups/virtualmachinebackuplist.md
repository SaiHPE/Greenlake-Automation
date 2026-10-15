---
title: "GET /backup-recovery/v1beta1/virtual-machines/{id}/backups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-backups/virtualmachinebackuplist.md"
scraped_at: "2026-06-07T06:14:09.596819+00:00Z"
---

# Get information about all virtual machine backups.

Get information about all virtual machine backups.

Endpoint: GET /backup-recovery/v1beta1/virtual-machines/{id}/backups
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the virtual machine
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Query parameters:

  - `offset` (integer)
    The number of items to omit from the beginning of the result set. The offset and limit query parameters are used in conjunction with pagination. For example "offset=30&limit=10" indicates the fourth page of 10 items.

  - `limit` (integer)
    The maximum number of items to include in the response. The offset and limit query parameters are used in conjunction with pagination. For example "offset=30&limit=10" indicates the fourth page of 10 items.

  - `filter` (string)
    An expression that enables you to filter the results.

A comparison compares a property name to a literal. The following comparisons are supported:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties.
* “in” : Is a value in a property (that is an array of strings).

Filters are supported on the following attributes:
* backupType
* state
* status
* createdByInfo/id
* createdByInfo/name
* storageSystemInfo/id
* storageSystemInfo/type
* storageSystemInfo/name
* sourceCopyInfo/id
* pointInTime
* verified
* protectionStoreInfo/id
* protectionStoreInfo/name
* dataOrchestratorInfo/id
* expiresAt
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
    UUID string uniquely identifying the backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.
    Example: "backup-recovery/virtual-machine-backup"

  - `items.appType` (string)
    Type of the application to which the backup belongs.
    Enum: "VMWARE"

  - `items.backupGranularity` (string)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `items.backupSetsInfo` (array)
    Information about the associated backupSetInfo. This is an array to handle application backups spanning multiple objects in the device.

  - `items.backupSetsInfo.backups` (array)
    Details of the individual backup objects.

  - `items.backupSetsInfo.backups.id` (string)
    The UUID of backup object.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.backupSetsInfo.backups.objectCount` (integer)
    Number of objects on the backup.

  - `items.backupSetsInfo.backups.sizeInMib` (integer)
    Size of the backup in mega bytes.
    Example: 614400

  - `items.backupSetsInfo.backups.sourceCopyInfo` (array)

  - `items.backupSetsInfo.backups.sourceCopyInfo.copyType` (string)
    Specifies type of copy from where this copy was created.
    Enum: "SNAPSHOT", "BACKUP"

  - `items.backupSetsInfo.backups.sourceCopyInfo.name` (string)
    Name of the copy.
    Example: "SnapshotVM-1"

  - `items.backupSetsInfo.backups.sourceCopyInfo.resourceUri` (string)
    Reference to resource.

  - `items.backupSetsInfo.backups.sourceCopyInfo.scsiIdentifier` (string)
    SCSI identifier of the volumes. Applicable only for snapshots.

  - `items.backupSetsInfo.backups.sourceVolumeInfo` (object)

  - `items.backupSetsInfo.backups.sourceVolumeInfo.id` (string)
    The UUID of the volume.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `items.backupSetsInfo.backups.sourceVolumeInfo.name` (string)
    Name of the volume.
    Example: "volume-1"

  - `items.backupSetsInfo.backups.sourceVolumeInfo.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.backupSetsInfo.backups.sourceVolumeInfo.scsiIdentifier` (string)
    SCSI identifier of the volume

  - `items.backupSetsInfo.sourceStorageSystemInfo` (object)
    Information about storage system where application was hosted.

  - `items.backupSetsInfo.sourceStorageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.backupSetsInfo.sourceStorageSystemInfo.name` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `items.backupSetsInfo.sourceStorageSystemInfo.storageSystemType` (string)
    Type of storage system.
    Enum: "HPE_NIMBLE", "HPE_PRIMERA", "HPE_ALLETRA_STORAGE_MP"

  - `items.backupSetsInfo.sourceStorageSystemInfo.type` (string)
    Type of storage system.

  - `items.backupType` (string)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `items.consistency` (string)
    Specifies whether to create crash consistent or application consistent snapshot.
CrashConsistentOnFailure: If an application consistent snapshot fails for any reason,
with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `items.consoleUri` (string)
    The URI for console screen that displays this object.

  - `items.containsRdmDisks` (boolean)
    Indicates if the recovery point has RDM disk or not.

  - `items.createdAt` (string)
    Time in UTC at which the object was created.

  - `items.createdByInfo` (object)
    Information about the user who initiated the workflow that
created this backup.

  - `items.createdByInfo.id` (string)
    UUID of the user.

  - `items.createdByInfo.name` (string)
    Name of the user.

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
    Brief description about the application backup.

  - `items.expiresAt` (string)
    Absolute value of time in UTC when the application backup expires.

  - `items.fullBackup` (boolean)

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.indexed` (string)
    The index state of the backup.
    Enum: "INDEXED", "PARTIALLY_INDEXED", "NOT_INDEXED"

  - `items.lockedUntil` (string)
    Absolute value of time in UTC until which the application backup remains locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `items.name` (string)
    Name of the application backup.
    Example: "Nimble-VM1-snap"

  - `items.partialBackup` (boolean)
    Indicates if the backup contains specific disk backup only.

  - `items.pointInTime` (string)
    Time in UTC at which the application backup was created on the device.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.protectionStoreInfo` (object)
    Information about the protection store where the copy is created.

  - `items.protectionStoreInfo.id` (string)
    UUID string uniquely identifying the protection store.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.protectionStoreInfo.name` (string)
    Name of the protection store.

  - `items.protectionStoreInfo.protectionStoreType` (string)
    Type of protection store.
    Enum: "ON_PREMISES", "CLOUD"

  - `items.protectionStoreInfo.type` (string)
    The type of resource
    Example: "backup-recovery/protection-store"

  - `items.scheduleInfo` (object)
    Details about the schedule that created this snapshot.

  - `items.scheduleInfo.name` (string)
    User provided name for this schedule
    Example: "Hourly snapshot schedule"

  - `items.scheduleInfo.recurrence` (string)
    Specifies the recurrence.
    Enum: "BY_MINUTES", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"

  - `items.scheduleInfo.scheduleId` (integer)
    Client provided id for this schedule.

  - `items.state` (string)
    The current state of the application backup.
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "DELETE_PENDING", "IN_USE_FOR_RESTORE", "MOUNTED", "IN_USE", "PENDING_DELETE_APPROVAL", "INDEXING"

  - `items.stateReason` (string)
    Brief reason for the current state of the application backup.

  - `items.status` (string)
    Current status of the application backup.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageSystemInfo` (object)
    Information about storage system where backup is created.

  - `items.storageSystemInfo.displayName` (string)
    Name of the storage system.
    Example: "atlas-dev-3par1.ind.hpecorp.net"

  - `items.updatedAt` (string)
    Time in UTC at which the object was last updated.

  - `items.verificationInfo` (object)
    Backup verification status details. Block level verification of backup with snapshot.

  - `items.verificationInfo.state` (string)
    Enum: "VERIFIED", "NOT_VERIFIED", "VERIFYING", "VERIFY_ERROR"

  - `items.verificationInfo.stateReason` (string)
    Brief reason for the verification state of backup.
    Example: "Successfully completed."

  - `items.verificationInfo.status` (string)
    Backup verification state.
    Enum: "OK", "ERROR", "WARNING"

  - `items.verificationInfo.verifiedAt` (string)
    Time in UTC at which the backup was verified.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.verified` (boolean)
    Flag indicating whether the backup-set was verified or not.

  - `items.virtualDisks` (array)
    A list of objects encapsulating information about the storage disks provisioned to a virtual machine.

  - `items.virtualDisks.capacityInBytes` (integer)
    Last known size of the virtual disk File path of the virtual disk.

  - `items.virtualDisks.datastoreId` (string)
    UUID string uniquely identifying the datastore

  - `items.virtualDisks.filePath` (string)
    File path of the virtual disk.
    Example: "NEW_VCSA6.7/NEW_VCSA6.7.vmdk"

  - `items.virtualDisks.id` (string)
    UUID for the virtual disk.

  - `items.virtualDisks.name` (string)
    Name of the virtual disk.
    Example: "NEW_VM_20200605155010/NEW_VM_20200605155010.vmdk"

  - `items.virtualDisks.type` (string)
    This gives information this virtual disk type. - VMFS - virtual machine flat disks. - VVOL - virtual volume - PRDM - physical raw disk mapping - VRDM - virtual raw disk mapping
    Enum: "VMFS", "VVOL", "PRDM", "VRDM"

  - `items.virtualDisks.vmId` (string)
    UUID string uniquely identifying the virtual machine.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.vmConfigInfo` (object)
    Information about the virtual machine configuration at the time snapshot was created.

  - `items.vmConfigInfo.computeInfo` (object)
    Compute information of the virtual machine.

  - `items.vmConfigInfo.computeInfo.memorySizeInMib` (string)
    Total memory provisioned.
    Example: "4096"

  - `items.vmConfigInfo.computeInfo.numCpuCores` (integer)
    Number of CPU cores provisioned.
    Example: 8

  - `items.vmConfigInfo.computeInfo.numCpuThreads` (integer)
    Number of CPU threads provisioned.
    Example: 16

  - `items.vmConfigInfo.networkAdapters` (array)

  - `items.vmConfigInfo.networkAdapters.macAddress` (string)
    MAC address of the network adapter.

  - `items.vmConfigInfo.networkAdapters.macAddressType` (string)
    Specifies how the MAC address is provided for the adapter.
    Enum: "MANUAL", "AUTOMATIC"

  - `items.vmConfigInfo.networkAdapters.name` (string)
    Name of the network adapter.

  - `items.vmConfigInfo.networkAdapters.networkDetails` (object)

  - `items.vmConfigInfo.networkAdapters.networkDetails.connectAtPowerOn` (boolean)
    Specifies if the network has to be connected at power on.

  - `items.vmConfigInfo.networkAdapters.networkDetails.displayName` (string)
    A user-friendly name that identifies the hypervisor network. This will always be same as name since adding or updating hypervisor networks is not supported when managed from a manager, such as the vCenter.

  - `items.vmConfigInfo.networkAdapters.networkDetails.id` (string)
    UUID string uniquely identifying the hypervisor network resource.

  - `items.vmConfigInfo.networkAdapters.networkDetails.name` (string)
    Name of the network as reported by the hypervisor manager.

  - `items.vmConfigInfo.networkAdapters.networkDetails.resourceUri` (string)
    The URI reference for this resource.

  - `items.vmConfigInfo.networkAdapters.networkDetails.state` (string)
    Reflects if network is available or deleted from vCenter.
    Enum: "AVAILABLE", "DELETED"

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


