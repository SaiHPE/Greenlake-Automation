---
title: "GET /virtualization/v1beta1/virtual-machines"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtual-machines/virtualmachineslist.md"
scraped_at: "2026-06-07T06:16:32.626587+00:00Z"
---

# Get all virtual machines across registered hypervisor managers.

List all the virtual machines across registered hypervisor managers.

Endpoint: GET /virtualization/v1beta1/virtual-machines
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
* GET /virtualization/v1beta1/virtual-machines?filter="appType eq VMWARE"
* GET /virtualization/v1beta1/virtual-machines?filter="appType eq VMWARE and status eq ERROR"

Filters are supported on the following attributes:
* status
* state
* appType
* hypervisorManagerInfo/name
* hypervisorManagerInfo/displayName
* hypervisorManagerInfo/id
* hostInfo/id
* hostInfo/name
* hostInfo/displayName
* clusterInfo/id
* clusterInfo/name
* clusterInfo/displayName
* protectionJobInfo/protectionPolicyInfo/id
* protectionJobInfo/protectionPolicyInfo/name
* vmProtectionGroupsInfo/id
* vmProtectionGroupsInfo/name
* appInfo/vmware/type
* appInfo/vmware/moref
* appInfo/vmware/datastoresInfo/id
* appInfo/vmware/datastoresInfo/name
* appInfo/vmware/datastoresInfo/displayName
* volumesInfo/id
* volumesInfo/storageSystemInfo/id
* volumesInfo/storageSystemInfo/serialNumber
* volumesInfo/storageSystemInfo/name
* volumesInfo/storageSystemInfo/vendorName
* volumesInfo/storageFolderInfo/id
* volumesInfo/storageFolderInfo/name
* volumesInfo/storagePoolInfo/id
* volumesInfo/storagePoolInfo/name
* powerState
* createdAt
* name
* services
* allowedOperations
* hciClusterUuid
* id
* type
* capacityInBytes
* computeInfo/numCpuCores
* computeInfo/memorySizeInMib
* vmPerfMetricInfo/cpuAllocatedInMhz
* vmPerfMetricInfo/cpuUsedInMhz
* vmPerfMetricInfo/storageAllocatedInKb
* vmPerfMetricInfo/storageUsedInBytes
* vmPerfMetricInfo/memoryAllocatedInMb
* vmPerfMetricInfo/memoryUsedInMb
* vmPerfMetricInfo/totalReadIops
* vmPerfMetricInfo/totalWriteIops
* vmPerfMetricInfo/averageReadLatency
* vmPerfMetricInfo/averageWriteLatency
* displayName
* protectionStatus
* recoveryPointsExist
* vclsVm

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
    UUID string uniquely identifying the virtual machine
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
    List of allowed operation on the virtual machine.
    Enum: "VIRTUAL_MACHINE_POWER_ON", "VIRTUAL_MACHINE_POWER_OFF", "VIRTUAL_MACHINE_RESET", "VIRTUAL_MACHINE_SHUTDOWN_GUEST_OS", "VIRTUAL_MACHINE_RESTART_GUEST_OS", "VIRTUAL_MACHINE_DELETE", "VIRTUAL_MACHINE_BACKUP_CREATE", "VIRTUAL_MACHINE_BACKUP_UPDATE", "VIRTUAL_MACHINE_BACKUP_DELETE", "VIRTUAL_MACHINE_SNAPSHOT_CREATE", "VIRTUAL_MACHINE_SNAPSHOT_UPDATE", "VIRTUAL_MACHINE_SNAPSHOT_DELETE", "VIRTUAL_MACHINE_RESTORE", "VIRTUAL_MACHINE_DISKS_RESTORE"

  - `items.appInfo` (object)
    Application specific information for this virtual machine.

  - `items.appInfo.vmware` (object)

  - `items.appInfo.vmware.datacenterInfo` (object)
    References to the datacenter that house this virtual machine.

  - `items.appInfo.vmware.datacenterInfo.id` (string)
    UUID string uniquely identifier of the datacenter.
    Example: "16245bf7-2b35-5580-86a6-620faa5b5403"

  - `items.appInfo.vmware.datacenterInfo.moref` (string)
    VMware provided moref for the datacenter.
    Example: "datacenter-2"

  - `items.appInfo.vmware.datacenterInfo.name` (string)
    VMware provided name for the datacenter.
    Example: "core-team-dc"

  - `items.appInfo.vmware.datastoresInfo` (array)
    References to all datastores that house virtual disks of this virtual machine.

  - `items.appInfo.vmware.datastoresInfo.displayName` (string)
    A user-friendly name that identifies the datastore.

  - `items.appInfo.vmware.datastoresInfo.id` (string)
    UUID string uniquely identifying the datastore

  - `items.appInfo.vmware.datastoresInfo.name` (string)
    Name of the datastore as reported by the hypervisor manager.

  - `items.appInfo.vmware.datastoresInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.appInfo.vmware.moref` (string)
    VMware provided moref for this virtual machine.
    Example: "vm-21"

  - `items.appInfo.vmware.resourcePoolInfo` (object)
    Information about the VMware's resource pool to which the VM belongs to.

  - `items.appInfo.vmware.resourcePoolInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor resource pool. This will always be same as name since adding or updating hypervisor resource pools is not supported when managed from a manager, such as the vCenter.

  - `items.appInfo.vmware.resourcePoolInfo.id` (string)
    UUID string uniquely identifying the hypervisor resource pool resource.

  - `items.appInfo.vmware.resourcePoolInfo.moref` (string)
    VMware provided moref for this resource pool.
    Example: "resourcepool-1"

  - `items.appInfo.vmware.resourcePoolInfo.name` (string)
    Name of the resource pool as reported by the hypervisor manager.

  - `items.appInfo.vmware.toolsInfo` (object)
    Information about the VMware tools installed in this virtual machine.

  - `items.appInfo.vmware.toolsInfo.status` (string)
    Status of VMware Tools running in the guest operating system. Values are inline with the vCenter provided values
    Enum: "NOT_INSTALLED", "NOT_RUNNING", "OK", "OLD"

  - `items.appInfo.vmware.toolsInfo.type` (string)
    Type of the VMware tool installed in this virtual machine.
    Example: "guestToolsTypeMSI"

  - `items.appInfo.vmware.toolsInfo.version` (string)
    Version of the VMware tool installed in this virtual machine.
    Example: "9349"

  - `items.appInfo.vmware.type` (string)
    Type of the virtual machine. - VMFS - virtual machine which is created from one or more VMFS datastores. - VVOL - virtual machine which is created from a VVOL datastores. - NFS  - virtual machine which is created from a NFS datastores. - VSAN - virtual machine which is created from a VSAN datastores.
    Enum: "VMFS", "VVOL", "NFS", "VSAN"

  - `items.appType` (string)
    Type of the application to which the VM belongs.
    Enum: "VMWARE"

  - `items.capacityInBytes` (integer)
    Size of the virtual machine in bytes.
    Example: 2407653459860

  - `items.clusterInfo` (object)

  - `items.clusterInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.

  - `items.clusterInfo.id` (string)
    UUID string uniquely identifying the hypervisor cluster.

  - `items.clusterInfo.name` (string)
    Name of the cluster as reported by the hypervisor manager.

  - `items.computeInfo` (object)
    Compute information of the virtual machine.

  - `items.computeInfo.memorySizeInMib` (string)
    Total memory provisioned.
    Example: "4096"

  - `items.computeInfo.numCpuCores` (integer)
    Number of CPU cores provisioned.
    Example: 8

  - `items.computeInfo.numCpuThreads` (integer)
    Number of CPU threads provisioned.
    Example: 16

  - `items.customerId` (string)
    The customer application identifier.

  - `items.displayName` (string)
    A user-friendly name that identifies the virtual machine.
    Example: "My-Test-VM"

  - `items.folderInfo` (object)
    The immediate parent folder on which this resource is hosted in the inventory of hypervisor-manager.

  - `items.folderInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor folder. This will always be same as name since adding or updating hypervisor folders is not supported when managed from a manager, such as the vCenter.

  - `items.folderInfo.id` (string)
    UUID string uniquely identifying the hypervisor folder.

  - `items.folderInfo.name` (string)
    Name of the folder as reported by the hypervisor manager.

  - `items.guestInfo` (object)
    Information of this guest OS running on the virtual machine.

  - `items.guestInfo.buildVersion` (string)
    Build version of the guest operating system on this virtual machine.
    Example: "6.7.0 build-9030300, NT 6.3, 3.8.13-44.1.1.el6uek.x86_64"

  - `items.guestInfo.name` (string)
    Name of the guest operating system on this virtual machine.
    Example: "Microsoft Windows Server 2008 R2 (64-bit)"

  - `items.guestInfo.releaseVersion` (string)
    Release version of the guest operating system on this virtual machine.
    Example: "6.7.0 build-9030300, R2, 7.2"

  - `items.guestInfo.type` (string)
    Operating system on this virtual machine.
    Enum: "WINDOWS", "LINUX", "OTHERS"

  - `items.hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.
    Example: "754f63f7-1016-40ec-9b8f-610f978b9aec"

  - `items.hostInfo` (object)

  - `items.hostInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.

  - `items.hostInfo.id` (string)
    UUID string uniquely identifying the hypervisor host.

  - `items.hostInfo.name` (string)
    Name of the host as reported by the hypervisor manager.

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `items.hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `items.name` (string)
    Name of the virtual machine as configured in the hypervisor manager.
    Example: "vm-1-windows"

  - `items.networkAdapters` (array)

  - `items.networkAdapters.macAddress` (string)
    MAC address of the network adapter.

  - `items.networkAdapters.macAddressType` (string)
    Specifies how the MAC address is provided for the adapter.
    Enum: "MANUAL", "AUTOMATIC"

  - `items.networkAdapters.name` (string)
    Name of the network adapter.

  - `items.networkAdapters.networkDetails` (object)

  - `items.networkAdapters.networkDetails.connectAtPowerOn` (boolean)
    Specifies if the network has to be connected at power on.

  - `items.networkAdapters.networkDetails.displayName` (string)
    A user-friendly name that identifies the hypervisor network. This will always be same as name since adding or updating hypervisor networks is not supported when managed from a manager, such as the vCenter.

  - `items.networkAdapters.networkDetails.id` (string)
    UUID string uniquely identifying the hypervisor network resource.

  - `items.networkAdapters.networkDetails.name` (string)
    Name of the network as reported by the hypervisor manager.

  - `items.networkAdapters.networkDetails.state` (string)
    Reflects if network is available or deleted from vCenter.
    Enum: "AVAILABLE", "DELETED"

  - `items.networkAddress` (string)
    IP address of the virtual machine.

  - `items.powerState` (string)
    This provides the information power state of the virtual machine.
    Enum: "POWERED_ON", "POWERED_OFF", "SUSPENDED", "UNKNOWN"

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

  - `items.recoveryPointsExist` (boolean)
    Indicates at least one valid recovery point exists for this resource.

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/virtual-machines/{vm-id}"

  - `items.services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `items.state` (string)
    The current state of the virtual machine
    Enum: "OK", "UNAVAILABLE", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "RESTORE_FAILED", "DELETED"

  - `items.stateReason` (string)
    Brief reason for the current state of the virtual machine

  - `items.status` (string)
    The current status of the virtual machine.
    Enum: "OK", "ERROR", "WARNING"

  - `items.uid` (string)
    Unique identifier of the virtual machine as reported by the hypervisor.

  - `items.vclsVm` (boolean)
    Indicates it is a vCLS virtual machine or not.

  - `items.virtualDisks` (array)
    A list of objects encapsulating information about the storage disks provisioned to a virtual machine

  - `items.virtualDisks.appInfo` (object)
    Hypervisor specific information.

  - `items.virtualDisks.appInfo.vmware` (object)
    VMware specific app info.

  - `items.virtualDisks.appInfo.vmware.datastoreInfo` (object)
    Information of the datastore where the virtual disk is residing.

  - `items.virtualDisks.appInfo.vmware.diskUuidEnabled` (boolean)
    True if the disk UUID is enabled for the virtual machine.
    Example: true

  - `items.virtualDisks.appInfo.vmware.type` (string)
    This gives information this virtual disk type. - VMFS - virtual machine flat disks. - VVOL - virtual volume - PRDM - physical raw disk mapping - VRDM - virtual raw disk mapping
    Enum: "VMFS", "VVOL", "PRDM", "VRDM"

  - `items.virtualDisks.capacityInBytes` (integer)
    Last known size of the virtual disk File path of the virtual disk

  - `items.virtualDisks.filePath` (string)
    File path of the virtual disk
    Example: "NEW_VCSA6.7/NEW_VCSA6.7.vmdk"

  - `items.virtualDisks.id` (string)
    UUID for the virtual disk.

  - `items.virtualDisks.name` (string)
    Name of the virtual disk.
    Example: "NEW_VM_20200605155010/NEW_VM_20200605155010.vmdk"

  - `items.virtualDisks.uid` (string)
    Unique identifier of the virtual disk as reported by the hypervisor.

  - `items.vmClassification` (string)
    Classification of different system/control VM types
    Enum: "DATA_ORCHESTRATOR", "PROTECTION_STORE_GATEWAY", "VCLS_VM", "TEMPLATE_VM", "OMNICUBE_VM", "DSC_VM"

  - `items.vmConfigPath` (string)
    VM configuration path of the virtual machine.
    Example: "NEW_VCSA6.7/NEW_VCSA6.7.vmx"

  - `items.vmPerfMetricInfo` (object)
    Virtual machine performance metrics.

  - `items.vmPerfMetricInfo.averageReadLatency` (integer)
    Average read latency.

  - `items.vmPerfMetricInfo.averageWriteLatency` (integer)
    Average write latency.

  - `items.vmPerfMetricInfo.cpuAllocatedInMhz` (integer)
    CPU allocated in mega hertz.

  - `items.vmPerfMetricInfo.cpuUsedInMhz` (integer)
    CPU used in mega hertz.

  - `items.vmPerfMetricInfo.memoryAllocatedInMb` (integer)
    Memory allocated in mega bytes.

  - `items.vmPerfMetricInfo.memoryUsedInMb` (integer)
    Memory used in mega bytes.

  - `items.vmPerfMetricInfo.storageAllocatedInKb` (integer)
    Storage allocated in kilo bytes.

  - `items.vmPerfMetricInfo.storageUsedInBytes` (integer)
    Storage used in bytes.

  - `items.vmPerfMetricInfo.totalReadIops` (integer)
    Total read IOPS.

  - `items.vmPerfMetricInfo.totalWriteIops` (integer)
    Total write IOPS.

  - `items.vmProtectionGroupsInfo` (array)
    Protection groups related to the virtual machine.

  - `items.vmProtectionGroupsInfo.id` (string)
    Unique identifier for the Protection Group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.vmProtectionGroupsInfo.name` (string)
    Name of the Protection Group.
    Example: "myProtectionGroup"

  - `items.volumesInfo` (array)
    Volumes associated with this virtual machine.

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
    The number of items to skip before starting to collect the result set.

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


