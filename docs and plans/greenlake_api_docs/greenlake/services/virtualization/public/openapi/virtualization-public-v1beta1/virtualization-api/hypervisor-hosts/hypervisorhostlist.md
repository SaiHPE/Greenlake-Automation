---
title: "GET /virtualization/v1beta1/hypervisor-hosts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-hosts/hypervisorhostlist.md"
scraped_at: "2026-06-07T06:16:28.840542+00:00Z"
---

# Get all hosts across registered hypervisor managers.

List all the hosts across registered hypervisor managers.

Endpoint: GET /virtualization/v1beta1/hypervisor-hosts
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
* GET /virtualization/v1beta1/hypervisor-hosts?filter="hostType eq ESXI"
* GET /virtualization/v1beta1/hypervisor-hosts?filter="hostType eq ESXI and status eq ERROR"

Filters are supported on the following attributes:
* hostType
* state
* status
* hypervisorManagerInfo/name
* hypervisorManagerInfo/displayName
* hypervisorManagerInfo/id
* version
* createdAt
* hciClusterUuid
* hciServerUuid
* name
* services
* displayName
* cpuInfo/processorSpeedHz
* cpuInfo/processorSockets
* cpuInfo/processorCores
* cpuInfo/logicalProcessors
* cpuInfo/hyperthreadingActive
* cpuSockets/vendor
* cpuSockets/cpuBusSpeedHz
* cpuSockets/cpuCoreSpeedHz
* appInfo/vmware/moref

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
    UUID string uniquely identifying the hypervisor host.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated

  - `items.appInfo` (object)
    Application specific information for this host.

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

  - `items.appInfo.vmware.moref` (string)
    VMware provided moref for this host.
    Example: "host-21"

  - `items.cpuInfo` (object)
    CPU information.

  - `items.cpuInfo.hyperthreadingActive` (boolean)
    Indicate whether hyperthreading is active or not.
    Example: true

  - `items.cpuInfo.logicalProcessors` (integer)
    Number of logical processors.
    Example: 2

  - `items.cpuInfo.processorCores` (integer)
    Number of processor cores.
    Example: 2

  - `items.cpuInfo.processorSockets` (integer)
    Number of processor sockets.
    Example: 2

  - `items.cpuInfo.processorSpeedHz` (integer)
    Processor speed in Hz.
    Example: 2299999000

  - `items.cpuSockets` (array)
    CPU sockets information.

  - `items.cpuSockets.cpuBusSpeedHz` (integer)
    CPU bus speed in Hz.
    Example: 91999960

  - `items.cpuSockets.cpuCoreSpeedHz` (integer)
    CPU core speed in Hz.
    Example: 2299999000

  - `items.cpuSockets.description` (string)
    Description of CPU socket.
    Example: "Intel(R) Xeon(R) Gold 5118 CPU @ 2.30GHz"

  - `items.cpuSockets.vendor` (string)
    Vendor of CPU socket.
    Example: "intel"

  - `items.customerId` (string)
    The customer application identifier.

  - `items.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.
    Example: "myESXi"

  - `items.hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.

  - `items.hciServerUuid` (string)
    UUID string uniquely identifying the HCI server.

  - `items.hostNetworkSystem` (object)
    Host network system information.

  - `items.hostNetworkSystem.portGroups` (array)
    List of port group information.

  - `items.hostNetworkSystem.portGroups.key` (string)
    The linkable identifier for the port group.

  - `items.hostNetworkSystem.portGroups.name` (string)
    Name of the port group.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy` (object)
    The network adapter teaming policy information.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy.activeNics` (array)
    List of active network adapter information.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy.activeNics.device` (string)
    Device name of the network adapter.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy.notifySwitches` (boolean)
    Flag to specify whether or not to notify the switch if a link fails.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy.policyName` (string)
    Name of the network adapter teaming policy.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy.rollingOrder` (boolean)
    Flag to specify whether or not to use a rolling policy when restoring links.

  - `items.hostNetworkSystem.portGroups.nicTeamingPolicy.useBeaconProbing` (boolean)
    Flag to specify whether or not to use beacon probing.

  - `items.hostNetworkSystem.portGroups.vlanId` (integer)
    VLAN ID associated with the port group.

  - `items.hostNetworkSystem.portGroups.vswitch` (string)
    Virtual switch that contains the port group.

  - `items.hostNetworkSystem.portGroups.vswitchName` (string)
    Virtual switch name.

  - `items.hostPerfMetricInfo` (object)
    Hypervisor host performance metrics.

  - `items.hostPerfMetricInfo.cpuCapacityInHz` (integer)
    CPU allocated in hertz.

  - `items.hostPerfMetricInfo.cpuUsageInMhz` (integer)
    CPU used in mega hertz.

  - `items.hostPerfMetricInfo.memorySizeInBytes` (integer)
    Memory allocated in bytes.

  - `items.hostPerfMetricInfo.memoryUsageInMb` (integer)
    Memory used in mega bytes.

  - `items.hostPerfMetricInfo.totalStorageInBytes` (integer)
    Storage allocated in bytes.

  - `items.hostPerfMetricInfo.usedStorageInBytes` (integer)
    Storage used in bytes.

  - `items.hostType` (string)
    The type of the hypervisor host.
    Enum: "ESXI"

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `items.hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `items.hypervisorManagerInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.name` (string)
    Name of the host as reported by the hypervisor manager.
    Example: "myESXi"

  - `items.networkAddress` (string)
    An IP address or hostname or FQDN to address the hypervisor host.
    Example: "192.168.0.1"

  - `items.networksInfo` (array)
    All the network names associated with this host.
    Example: ["network-2053","network-1005"]

  - `items.parentInfo` (object)
    Parent of this host. It could be a cluster or folder in case of a VMware ESXi Host. For a Hyper-V host it will be cluster or host group.

  - `items.parentInfo.displayName` (string)
    A user-friendly name that identifies the parent of this host.

  - `items.parentInfo.id` (string)
    UUID uniquely identifying the parent of this host.

  - `items.parentInfo.name` (string)
    Name of the parent of this host.
    Example: "xyz_cluster"

  - `items.parentInfo.type` (string)
    The type of the parent.
    Enum: "CLUSTER", "FOLDER"

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-hosts/{host-id}"

  - `items.services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `items.state` (string)
    The current state of the hypervisor host object
    Enum: "OK", "ERROR", "REFRESHING"

  - `items.stateReason` (string)
    Brief reason for the current state of the hypervisor host

  - `items.status` (string)
    The current status of the hypervisor host. Status is derived and abstracted to a 'standard status' based on the status reported by the hypervisor manager.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageAdaptersInfo` (array)
    List of storage adapters associated with this host.

  - `items.storageAdaptersInfo.model` (string)
    Model of the adapter
    Example: "QLogic FastLinQ QL41xxx Series 10/25 GbE Controller (FCoE)"

  - `items.storageAdaptersInfo.name` (string)
    Name of the adapter
    Example: "vmhba0"

  - `items.storageAdaptersInfo.status` (string)
    Status of the adapter
    Enum: "OFFLINE", "ONLINE", "UNKNOWN"

  - `items.storageAdaptersInfo.type` (string)
    Type of the adapter
    Example: "FC"

  - `items.storageAdaptersInfo.wwn` (string)
    WWN of the adapter
    Example: "20009440c95b835c"

  - `items.uid` (string)
    A hypervisor host provided durable UID.

  - `items.version` (string)
    The hypervisor host version.
    Example: "6.7.0 build-9030300, R2, 7.2"

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


