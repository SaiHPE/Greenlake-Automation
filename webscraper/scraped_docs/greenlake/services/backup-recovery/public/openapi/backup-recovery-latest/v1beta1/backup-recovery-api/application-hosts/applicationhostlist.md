---
title: "GET /backup-recovery/v1beta1/application-hosts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhostlist.md"
scraped_at: "2026-06-07T06:14:13.421193+00:00Z"
---

# Get all registered Application Hosts.

List all the registered Application Hosts.

Endpoint: GET /backup-recovery/v1beta1/application-hosts
Version: 1.1.0
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
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /backup-recovery/v1beta1/application-hosts?filter="osInfo/name eq Windows+Server+2012"
* GET /backup-recovery/v1beta1/application-hosts?filter="osInfo/name eq Windows+Server+2012 and status eq Error"


Filters are supported on the following attributes:
* osInfo/name
* state
* status
* osInfo/releaseVersion
* createdAt
* name
* dataOrchestratorInfo/id

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc"). If no direction indicator is specified, the
default order is ascending.

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the application host
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.clusterInfo` (object)
    Information about the cluster that the host is part of.

  - `items.clusterInfo.clusterIp` (string)
    IP address of the cluster
    Example: "192.168.0.1"

  - `items.clusterInfo.members` (array)
    Apllication host members of the cluster

  - `items.clusterInfo.members.displayName` (string)
    A user-friendly name to identify the application host

  - `items.clusterInfo.members.name` (string)
    The host name as reported by the host.

  - `items.clusterInfo.members.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.clusterInfo.name` (string)
    Name of the cluster
    Example: "cluster-1"

  - `items.computeInfo` (object)
    Compute info about the host

  - `items.computeInfo.memorySizeInMiB` (integer)
    Memory size in MiB
    Example: 4096

  - `items.computeInfo.numCpuCores` (integer)
    Number of CPU cores
    Example: 8

  - `items.computeInfo.numCpuThreads` (integer)
    Number of CPU threads
    Example: 16

  - `items.createdAt` (string)
    Time in UTC at which the object was created

  - `items.customerId` (string)
    The customer application identifier.

  - `items.dataOrchestratorInfo` (object)
    Data Orchestrator specific information.

  - `items.dataOrchestratorInfo.id` (string)
    Unique string identifying the data orchestrator.
    Example: "8b4c14a6-3cd5-4907-97c4-cf44c5b642e5"

  - `items.dataOrchestratorInfo.resourceUri` (string)
    The URI reference for this data orchestrator.

  - `items.description` (string)
    A brief description of the application host as provided by the user during registration.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.manufacturer` (string)
    The virtual or physical hardware manufacturer
    Example: "VMware, Inc."

  - `items.networkAddress` (string)
    An IP address or hostname or FQDN to address the host
    Example: "192.168.0.1"

  - `items.networkInterfaces` (array)
    Information of all network interfaces of the application host

  - `items.networkInterfaces.address` (string)
    An IP address or hostname or FQDN to address the host
    Example: "192.168.0.1"

  - `items.networkInterfaces.name` (string)
    Name of the network interface
    Example: "eth0"

  - `items.osInfo` (object)
    Operating system info of the application host

  - `items.osInfo.buildVersion` (string)
    Build version of the operating system
    Example: "6.7.0 build-9030300 NT 6.3, 3.8.13-44.1.1.el6uek.x86_6"

  - `items.osInfo.name` (string)
    Name of the operating system
    Example: "Windows Server 2012, Oracle Enterprise Linux"

  - `items.osInfo.releaseVersion` (string)
    Version of the operating system
    Example: "6.7.0 build-9030300, R2, 7.2"

  - `items.state` (string)
    The current state of the application host resource
    Enum: "OK", "ERROR", "INITIALIZING", "CREATING", "DELETING", "UPDATING", "REFRESHING"

  - `items.stateReason` (string)
    Brief reason for the current state of the application host

  - `items.status` (string)
    The current status of the application host resource.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageInitiators` (object)
    Details of the application host's storage initiators

  - `items.storageInitiators.fcHba` (array)
    Details for the FC HBAs

  - `items.storageInitiators.fcHba.portWwpn` (string)
    WWPN of the FC HBA
    Example: "2100000e1ec95100"

  - `items.storageInitiators.fcHba.vendor` (string)
    FC HBA vendor
    Example: "QLogic"

  - `items.storageInitiators.iscsi` (array)
    iSCSI initiator detials
    Example: ["iqn.290120.hpe.com:atlas-ui-kk:7838631cc2c"]

  - `items.updatedAt` (string)
    Time in UTC at which the object was last updated

  - `items.username` (string)
    The name of the user to be used to connect to the host
    Example: "Administrator"

  - `items.virtual` (boolean)
    This is set to true for hosts on virtual machines and set to false for physical hosts
    Example: true

  - `items.virtualizationInfo` (object)

  - `items.virtualizationInfo.hypervisorManagerInfo` (object)

  - `items.virtualizationInfo.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.virtualizationInfo.hypervisorManagerInfo.name` (string)
    User defined name for the hypervisor manager.
    Example: "vcenter123.hpe.com"

  - `items.virtualizationInfo.hypervisorManagerInfo.type` (string)
    Type of the resource.
    Example: "virtualization/hypervisor-manager"

  - `items.virtualizationInfo.virtualMachineInfo` (object)

  - `items.virtualizationInfo.virtualMachineInfo.name` (string)
    Name of the parent virtual machine
    Example: "mssql-vm"

  - `items.virtualizationInfo.virtualMachineInfo.resourceUri` (string)
    The resource uri of the parent virtual machine
    Example: "/backup-recovery/v1beta1/virtual-machines/{vm-id}"

  - `count` (integer, required)
    Number of items in this response.

  - `pageLimit` (integer)
    The numbers of items to return

  - `pageOffset` (integer)
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


