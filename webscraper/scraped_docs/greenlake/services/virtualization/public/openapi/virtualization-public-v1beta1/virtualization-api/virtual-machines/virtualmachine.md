---
title: "GET /virtualization/v1beta1/virtual-machines/{vm-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/virtual-machines/virtualmachine.md"
scraped_at: "2026-06-07T06:16:29.925739+00:00Z"
---

# Get a virtual machine identified by {vm-id}

Details of a virtual machine

Endpoint: GET /virtualization/v1beta1/virtual-machines/{vm-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `vm-id` (string, required)
    UUID string uniquely identifying the virtual machine
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the virtual machine
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
    List of allowed operation on the virtual machine.
    Enum: "VIRTUAL_MACHINE_POWER_ON", "VIRTUAL_MACHINE_POWER_OFF", "VIRTUAL_MACHINE_RESET", "VIRTUAL_MACHINE_SHUTDOWN_GUEST_OS", "VIRTUAL_MACHINE_RESTART_GUEST_OS", "VIRTUAL_MACHINE_DELETE", "VIRTUAL_MACHINE_BACKUP_CREATE", "VIRTUAL_MACHINE_BACKUP_UPDATE", "VIRTUAL_MACHINE_BACKUP_DELETE", "VIRTUAL_MACHINE_SNAPSHOT_CREATE", "VIRTUAL_MACHINE_SNAPSHOT_UPDATE", "VIRTUAL_MACHINE_SNAPSHOT_DELETE", "VIRTUAL_MACHINE_RESTORE", "VIRTUAL_MACHINE_DISKS_RESTORE"

  - `appInfo` (object)
    Application specific information for this virtual machine.

  - `appInfo.vmware` (object)

  - `appInfo.vmware.datacenterInfo` (object)
    References to the datacenter that house this virtual machine.

  - `appInfo.vmware.datacenterInfo.id` (string)
    UUID string uniquely identifier of the datacenter.
    Example: "16245bf7-2b35-5580-86a6-620faa5b5403"

  - `appInfo.vmware.datacenterInfo.moref` (string)
    VMware provided moref for the datacenter.
    Example: "datacenter-2"

  - `appInfo.vmware.datacenterInfo.name` (string)
    VMware provided name for the datacenter.
    Example: "core-team-dc"

  - `appInfo.vmware.datastoresInfo` (array)
    References to all datastores that house virtual disks of this virtual machine.

  - `appInfo.vmware.datastoresInfo.displayName` (string)
    A user-friendly name that identifies the datastore.

  - `appInfo.vmware.datastoresInfo.id` (string)
    UUID string uniquely identifying the datastore

  - `appInfo.vmware.datastoresInfo.name` (string)
    Name of the datastore as reported by the hypervisor manager.

  - `appInfo.vmware.datastoresInfo.resourceUri` (string)
    The URI reference for this resource.

  - `appInfo.vmware.moref` (string)
    VMware provided moref for this virtual machine.
    Example: "vm-21"

  - `appInfo.vmware.resourcePoolInfo` (object)
    Information about the VMware's resource pool to which the VM belongs to.

  - `appInfo.vmware.resourcePoolInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor resource pool. This will always be same as name since adding or updating hypervisor resource pools is not supported when managed from a manager, such as the vCenter.

  - `appInfo.vmware.resourcePoolInfo.id` (string)
    UUID string uniquely identifying the hypervisor resource pool resource.

  - `appInfo.vmware.resourcePoolInfo.moref` (string)
    VMware provided moref for this resource pool.
    Example: "resourcepool-1"

  - `appInfo.vmware.resourcePoolInfo.name` (string)
    Name of the resource pool as reported by the hypervisor manager.

  - `appInfo.vmware.toolsInfo` (object)
    Information about the VMware tools installed in this virtual machine.

  - `appInfo.vmware.toolsInfo.status` (string)
    Status of VMware Tools running in the guest operating system. Values are inline with the vCenter provided values
    Enum: "NOT_INSTALLED", "NOT_RUNNING", "OK", "OLD"

  - `appInfo.vmware.toolsInfo.type` (string)
    Type of the VMware tool installed in this virtual machine.
    Example: "guestToolsTypeMSI"

  - `appInfo.vmware.toolsInfo.version` (string)
    Version of the VMware tool installed in this virtual machine.
    Example: "9349"

  - `appInfo.vmware.type` (string)
    Type of the virtual machine. - VMFS - virtual machine which is created from one or more VMFS datastores. - VVOL - virtual machine which is created from a VVOL datastores. - NFS  - virtual machine which is created from a NFS datastores. - VSAN - virtual machine which is created from a VSAN datastores.
    Enum: "VMFS", "VVOL", "NFS", "VSAN"

  - `appType` (string)
    Type of the application to which the VM belongs.
    Enum: "VMWARE"

  - `capacityInBytes` (integer)
    Size of the virtual machine in bytes.
    Example: 2407653459860

  - `clusterInfo` (object)

  - `clusterInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.

  - `clusterInfo.id` (string)
    UUID string uniquely identifying the hypervisor cluster.

  - `clusterInfo.name` (string)
    Name of the cluster as reported by the hypervisor manager.

  - `computeInfo` (object)
    Compute information of the virtual machine.

  - `computeInfo.memorySizeInMib` (string)
    Total memory provisioned.
    Example: "4096"

  - `computeInfo.numCpuCores` (integer)
    Number of CPU cores provisioned.
    Example: 8

  - `computeInfo.numCpuThreads` (integer)
    Number of CPU threads provisioned.
    Example: 16

  - `customerId` (string)
    The customer application identifier.

  - `displayName` (string)
    A user-friendly name that identifies the virtual machine.
    Example: "My-Test-VM"

  - `folderInfo` (object)
    The immediate parent folder on which this resource is hosted in the inventory of hypervisor-manager.

  - `folderInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor folder. This will always be same as name since adding or updating hypervisor folders is not supported when managed from a manager, such as the vCenter.

  - `folderInfo.id` (string)
    UUID string uniquely identifying the hypervisor folder.

  - `folderInfo.name` (string)
    Name of the folder as reported by the hypervisor manager.

  - `guestInfo` (object)
    Information of this guest OS running on the virtual machine.

  - `guestInfo.buildVersion` (string)
    Build version of the guest operating system on this virtual machine.
    Example: "6.7.0 build-9030300, NT 6.3, 3.8.13-44.1.1.el6uek.x86_64"

  - `guestInfo.name` (string)
    Name of the guest operating system on this virtual machine.
    Example: "Microsoft Windows Server 2008 R2 (64-bit)"

  - `guestInfo.releaseVersion` (string)
    Release version of the guest operating system on this virtual machine.
    Example: "6.7.0 build-9030300, R2, 7.2"

  - `guestInfo.type` (string)
    Operating system on this virtual machine.
    Enum: "WINDOWS", "LINUX", "OTHERS"

  - `hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.
    Example: "754f63f7-1016-40ec-9b8f-610f978b9aec"

  - `hostInfo` (object)

  - `hostInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.

  - `hostInfo.id` (string)
    UUID string uniquely identifying the hypervisor host.

  - `hostInfo.name` (string)
    Name of the host as reported by the hypervisor manager.

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `name` (string)
    Name of the virtual machine as configured in the hypervisor manager.
    Example: "vm-1-windows"

  - `networkAdapters` (array)

  - `networkAdapters.macAddress` (string)
    MAC address of the network adapter.

  - `networkAdapters.macAddressType` (string)
    Specifies how the MAC address is provided for the adapter.
    Enum: "MANUAL", "AUTOMATIC"

  - `networkAdapters.name` (string)
    Name of the network adapter.

  - `networkAdapters.networkDetails` (object)

  - `networkAdapters.networkDetails.connectAtPowerOn` (boolean)
    Specifies if the network has to be connected at power on.

  - `networkAdapters.networkDetails.displayName` (string)
    A user-friendly name that identifies the hypervisor network. This will always be same as name since adding or updating hypervisor networks is not supported when managed from a manager, such as the vCenter.

  - `networkAdapters.networkDetails.id` (string)
    UUID string uniquely identifying the hypervisor network resource.

  - `networkAdapters.networkDetails.name` (string)
    Name of the network as reported by the hypervisor manager.

  - `networkAdapters.networkDetails.state` (string)
    Reflects if network is available or deleted from vCenter.
    Enum: "AVAILABLE", "DELETED"

  - `networkAddress` (string)
    IP address of the virtual machine.

  - `powerState` (string)
    This provides the information power state of the virtual machine.
    Enum: "POWERED_ON", "POWERED_OFF", "SUSPENDED", "UNKNOWN"

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

  - `recoveryPointsExist` (boolean)
    Indicates at least one valid recovery point exists for this resource.

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/virtual-machines/{vm-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the virtual machine
    Enum: "OK", "UNAVAILABLE", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "RESTORE_FAILED", "DELETED"

  - `stateReason` (string)
    Brief reason for the current state of the virtual machine

  - `status` (string)
    The current status of the virtual machine.
    Enum: "OK", "ERROR", "WARNING"

  - `uid` (string)
    Unique identifier of the virtual machine as reported by the hypervisor.

  - `vclsVm` (boolean)
    Indicates it is a vCLS virtual machine or not.

  - `virtualDisks` (array)
    A list of objects encapsulating information about the storage disks provisioned to a virtual machine

  - `virtualDisks.appInfo` (object)
    Hypervisor specific information.

  - `virtualDisks.appInfo.vmware` (object)
    VMware specific app info.

  - `virtualDisks.appInfo.vmware.datastoreInfo` (object)
    Information of the datastore where the virtual disk is residing.

  - `virtualDisks.appInfo.vmware.diskUuidEnabled` (boolean)
    True if the disk UUID is enabled for the virtual machine.
    Example: true

  - `virtualDisks.appInfo.vmware.type` (string)
    This gives information this virtual disk type. - VMFS - virtual machine flat disks. - VVOL - virtual volume - PRDM - physical raw disk mapping - VRDM - virtual raw disk mapping
    Enum: "VMFS", "VVOL", "PRDM", "VRDM"

  - `virtualDisks.capacityInBytes` (integer)
    Last known size of the virtual disk File path of the virtual disk

  - `virtualDisks.filePath` (string)
    File path of the virtual disk
    Example: "NEW_VCSA6.7/NEW_VCSA6.7.vmdk"

  - `virtualDisks.id` (string)
    UUID for the virtual disk.

  - `virtualDisks.name` (string)
    Name of the virtual disk.
    Example: "NEW_VM_20200605155010/NEW_VM_20200605155010.vmdk"

  - `virtualDisks.uid` (string)
    Unique identifier of the virtual disk as reported by the hypervisor.

  - `vmClassification` (string)
    Classification of different system/control VM types
    Enum: "DATA_ORCHESTRATOR", "PROTECTION_STORE_GATEWAY", "VCLS_VM", "TEMPLATE_VM", "OMNICUBE_VM", "DSC_VM"

  - `vmConfigPath` (string)
    VM configuration path of the virtual machine.
    Example: "NEW_VCSA6.7/NEW_VCSA6.7.vmx"

  - `vmPerfMetricInfo` (object)
    Virtual machine performance metrics.

  - `vmPerfMetricInfo.averageReadLatency` (integer)
    Average read latency.

  - `vmPerfMetricInfo.averageWriteLatency` (integer)
    Average write latency.

  - `vmPerfMetricInfo.cpuAllocatedInMhz` (integer)
    CPU allocated in mega hertz.

  - `vmPerfMetricInfo.cpuUsedInMhz` (integer)
    CPU used in mega hertz.

  - `vmPerfMetricInfo.memoryAllocatedInMb` (integer)
    Memory allocated in mega bytes.

  - `vmPerfMetricInfo.memoryUsedInMb` (integer)
    Memory used in mega bytes.

  - `vmPerfMetricInfo.storageAllocatedInKb` (integer)
    Storage allocated in kilo bytes.

  - `vmPerfMetricInfo.storageUsedInBytes` (integer)
    Storage used in bytes.

  - `vmPerfMetricInfo.totalReadIops` (integer)
    Total read IOPS.

  - `vmPerfMetricInfo.totalWriteIops` (integer)
    Total write IOPS.

  - `vmProtectionGroupsInfo` (array)
    Protection groups related to the virtual machine.

  - `vmProtectionGroupsInfo.id` (string)
    Unique identifier for the Protection Group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `vmProtectionGroupsInfo.name` (string)
    Name of the Protection Group.
    Example: "myProtectionGroup"

  - `volumesInfo` (array)
    Volumes associated with this virtual machine.

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


