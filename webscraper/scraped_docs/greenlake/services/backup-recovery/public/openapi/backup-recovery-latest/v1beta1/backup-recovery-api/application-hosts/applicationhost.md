---
title: "GET /backup-recovery/v1beta1/application-hosts/{host-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhost.md"
scraped_at: "2026-06-07T06:14:13.390666+00:00Z"
---

# Get an Application Host resource identified by {host-id}.

Get detailed information for a registered Application Host qualified by host-id.

Endpoint: GET /backup-recovery/v1beta1/application-hosts/{host-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `host-id` (string, required)
    UUID string uniquely identifying the application host
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the application host
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `clusterInfo` (object)
    Information about the cluster that the host is part of.

  - `clusterInfo.clusterIp` (string)
    IP address of the cluster
    Example: "192.168.0.1"

  - `clusterInfo.members` (array)
    Apllication host members of the cluster

  - `clusterInfo.members.displayName` (string)
    A user-friendly name to identify the application host

  - `clusterInfo.members.name` (string)
    The host name as reported by the host.

  - `clusterInfo.members.resourceUri` (string)
    The 'self' reference for this resource.

  - `clusterInfo.name` (string)
    Name of the cluster
    Example: "cluster-1"

  - `computeInfo` (object)
    Compute info about the host

  - `computeInfo.memorySizeInMiB` (integer)
    Memory size in MiB
    Example: 4096

  - `computeInfo.numCpuCores` (integer)
    Number of CPU cores
    Example: 8

  - `computeInfo.numCpuThreads` (integer)
    Number of CPU threads
    Example: 16

  - `createdAt` (string)
    Time in UTC at which the object was created

  - `customerId` (string)
    The customer application identifier.

  - `dataOrchestratorInfo` (object)
    Data Orchestrator specific information.

  - `dataOrchestratorInfo.id` (string)
    Unique string identifying the data orchestrator.
    Example: "8b4c14a6-3cd5-4907-97c4-cf44c5b642e5"

  - `dataOrchestratorInfo.resourceUri` (string)
    The URI reference for this data orchestrator.

  - `description` (string)
    A brief description of the application host as provided by the user during registration.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `manufacturer` (string)
    The virtual or physical hardware manufacturer
    Example: "VMware, Inc."

  - `networkAddress` (string)
    An IP address or hostname or FQDN to address the host
    Example: "192.168.0.1"

  - `networkInterfaces` (array)
    Information of all network interfaces of the application host

  - `networkInterfaces.address` (string)
    An IP address or hostname or FQDN to address the host
    Example: "192.168.0.1"

  - `networkInterfaces.name` (string)
    Name of the network interface
    Example: "eth0"

  - `osInfo` (object)
    Operating system info of the application host

  - `osInfo.buildVersion` (string)
    Build version of the operating system
    Example: "6.7.0 build-9030300 NT 6.3, 3.8.13-44.1.1.el6uek.x86_6"

  - `osInfo.name` (string)
    Name of the operating system
    Example: "Windows Server 2012, Oracle Enterprise Linux"

  - `osInfo.releaseVersion` (string)
    Version of the operating system
    Example: "6.7.0 build-9030300, R2, 7.2"

  - `state` (string)
    The current state of the application host resource
    Enum: "OK", "ERROR", "INITIALIZING", "CREATING", "DELETING", "UPDATING", "REFRESHING"

  - `stateReason` (string)
    Brief reason for the current state of the application host

  - `status` (string)
    The current status of the application host resource.
    Enum: "OK", "ERROR", "WARNING"

  - `storageInitiators` (object)
    Details of the application host's storage initiators

  - `storageInitiators.fcHba` (array)
    Details for the FC HBAs

  - `storageInitiators.fcHba.portWwpn` (string)
    WWPN of the FC HBA
    Example: "2100000e1ec95100"

  - `storageInitiators.fcHba.vendor` (string)
    FC HBA vendor
    Example: "QLogic"

  - `storageInitiators.iscsi` (array)
    iSCSI initiator detials
    Example: ["iqn.290120.hpe.com:atlas-ui-kk:7838631cc2c"]

  - `updatedAt` (string)
    Time in UTC at which the object was last updated

  - `username` (string)
    The name of the user to be used to connect to the host
    Example: "Administrator"

  - `virtual` (boolean)
    This is set to true for hosts on virtual machines and set to false for physical hosts
    Example: true

  - `virtualizationInfo` (object)

  - `virtualizationInfo.hypervisorManagerInfo` (object)

  - `virtualizationInfo.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `virtualizationInfo.hypervisorManagerInfo.name` (string)
    User defined name for the hypervisor manager.
    Example: "vcenter123.hpe.com"

  - `virtualizationInfo.hypervisorManagerInfo.type` (string)
    Type of the resource.
    Example: "virtualization/hypervisor-manager"

  - `virtualizationInfo.virtualMachineInfo` (object)

  - `virtualizationInfo.virtualMachineInfo.name` (string)
    Name of the parent virtual machine
    Example: "mssql-vm"

  - `virtualizationInfo.virtualMachineInfo.resourceUri` (string)
    The resource uri of the parent virtual machine
    Example: "/backup-recovery/v1beta1/virtual-machines/{vm-id}"

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


