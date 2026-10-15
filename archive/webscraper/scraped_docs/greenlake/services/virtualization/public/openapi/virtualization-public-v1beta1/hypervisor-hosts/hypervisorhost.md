---
title: "GET /virtualization/v1beta1/hypervisor-hosts/{host-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/hypervisor-hosts/hypervisorhost.md"
scraped_at: "2026-06-07T06:16:31.775753+00:00Z"
---

# Get a hypervisor host resource identified by {host-id}

Details of a hypervisors host.

Endpoint: GET /virtualization/v1beta1/hypervisor-hosts/{host-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `host-id` (string, required)
    UUID string uniquely identifying the hypervisor host.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the hypervisor host.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated

  - `appInfo` (object)
    Application specific information for this host.

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

  - `appInfo.vmware.moref` (string)
    VMware provided moref for this host.
    Example: "host-21"

  - `cpuInfo` (object)
    CPU information.

  - `cpuInfo.hyperthreadingActive` (boolean)
    Indicate whether hyperthreading is active or not.
    Example: true

  - `cpuInfo.logicalProcessors` (integer)
    Number of logical processors.
    Example: 2

  - `cpuInfo.processorCores` (integer)
    Number of processor cores.
    Example: 2

  - `cpuInfo.processorSockets` (integer)
    Number of processor sockets.
    Example: 2

  - `cpuInfo.processorSpeedHz` (integer)
    Processor speed in Hz.
    Example: 2299999000

  - `cpuSockets` (array)
    CPU sockets information.

  - `cpuSockets.cpuBusSpeedHz` (integer)
    CPU bus speed in Hz.
    Example: 91999960

  - `cpuSockets.cpuCoreSpeedHz` (integer)
    CPU core speed in Hz.
    Example: 2299999000

  - `cpuSockets.description` (string)
    Description of CPU socket.
    Example: "Intel(R) Xeon(R) Gold 5118 CPU @ 2.30GHz"

  - `cpuSockets.vendor` (string)
    Vendor of CPU socket.
    Example: "intel"

  - `customerId` (string)
    The customer application identifier.

  - `displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.
    Example: "myESXi"

  - `hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.

  - `hciServerUuid` (string)
    UUID string uniquely identifying the HCI server.

  - `hostNetworkSystem` (object)
    Host network system information.

  - `hostNetworkSystem.portGroups` (array)
    List of port group information.

  - `hostNetworkSystem.portGroups.key` (string)
    The linkable identifier for the port group.

  - `hostNetworkSystem.portGroups.name` (string)
    Name of the port group.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy` (object)
    The network adapter teaming policy information.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy.activeNics` (array)
    List of active network adapter information.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy.activeNics.device` (string)
    Device name of the network adapter.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy.notifySwitches` (boolean)
    Flag to specify whether or not to notify the switch if a link fails.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy.policyName` (string)
    Name of the network adapter teaming policy.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy.rollingOrder` (boolean)
    Flag to specify whether or not to use a rolling policy when restoring links.

  - `hostNetworkSystem.portGroups.nicTeamingPolicy.useBeaconProbing` (boolean)
    Flag to specify whether or not to use beacon probing.

  - `hostNetworkSystem.portGroups.vlanId` (integer)
    VLAN ID associated with the port group.

  - `hostNetworkSystem.portGroups.vswitch` (string)
    Virtual switch that contains the port group.

  - `hostNetworkSystem.portGroups.vswitchName` (string)
    Virtual switch name.

  - `hostPerfMetricInfo` (object)
    Hypervisor host performance metrics.

  - `hostPerfMetricInfo.cpuCapacityInHz` (integer)
    CPU allocated in hertz.

  - `hostPerfMetricInfo.cpuUsageInMhz` (integer)
    CPU used in mega hertz.

  - `hostPerfMetricInfo.memorySizeInBytes` (integer)
    Memory allocated in bytes.

  - `hostPerfMetricInfo.memoryUsageInMb` (integer)
    Memory used in mega bytes.

  - `hostPerfMetricInfo.totalStorageInBytes` (integer)
    Storage allocated in bytes.

  - `hostPerfMetricInfo.usedStorageInBytes` (integer)
    Storage used in bytes.

  - `hostType` (string)
    The type of the hypervisor host.
    Enum: "ESXI"

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `hypervisorManagerInfo.resourceUri` (string)
    The URI reference for this resource.

  - `name` (string)
    Name of the host as reported by the hypervisor manager.
    Example: "myESXi"

  - `networkAddress` (string)
    An IP address or hostname or FQDN to address the hypervisor host.
    Example: "192.168.0.1"

  - `networksInfo` (array)
    All the network names associated with this host.
    Example: ["network-2053","network-1005"]

  - `parentInfo` (object)
    Parent of this host. It could be a cluster or folder in case of a VMware ESXi Host. For a Hyper-V host it will be cluster or host group.

  - `parentInfo.displayName` (string)
    A user-friendly name that identifies the parent of this host.

  - `parentInfo.id` (string)
    UUID uniquely identifying the parent of this host.

  - `parentInfo.name` (string)
    Name of the parent of this host.
    Example: "xyz_cluster"

  - `parentInfo.type` (string)
    The type of the parent.
    Enum: "CLUSTER", "FOLDER"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-hosts/{host-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the hypervisor host object
    Enum: "OK", "ERROR", "REFRESHING"

  - `stateReason` (string)
    Brief reason for the current state of the hypervisor host

  - `status` (string)
    The current status of the hypervisor host. Status is derived and abstracted to a 'standard status' based on the status reported by the hypervisor manager.
    Enum: "OK", "ERROR", "WARNING"

  - `storageAdaptersInfo` (array)
    List of storage adapters associated with this host.

  - `storageAdaptersInfo.model` (string)
    Model of the adapter
    Example: "QLogic FastLinQ QL41xxx Series 10/25 GbE Controller (FCoE)"

  - `storageAdaptersInfo.name` (string)
    Name of the adapter
    Example: "vmhba0"

  - `storageAdaptersInfo.status` (string)
    Status of the adapter
    Enum: "OFFLINE", "ONLINE", "UNKNOWN"

  - `storageAdaptersInfo.type` (string)
    Type of the adapter
    Example: "FC"

  - `storageAdaptersInfo.wwn` (string)
    WWN of the adapter
    Example: "20009440c95b835c"

  - `uid` (string)
    A hypervisor host provided durable UID.

  - `version` (string)
    The hypervisor host version.
    Example: "6.7.0 build-9030300, R2, 7.2"

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


