---
title: "GET /virtualization/v1beta1/hypervisor-clusters/{cluster-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/hypervisor-clusters/hypervisorcluster.md"
scraped_at: "2026-06-07T06:16:31.590423+00:00Z"
---

# Get a hypervisor cluster resource identified by {cluster-id}

Details of a hypervisors cluster.

Endpoint: GET /virtualization/v1beta1/hypervisor-clusters/{cluster-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `cluster-id` (string, required)
    UUID string uniquely identifying the hypervisor cluster.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the hypervisor cluster.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created.

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `appInfo` (object)
    Application specific information for this cluster.

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
    VMware provided moref for this cluster.
    Example: "domain-c8"

  - `clusterPerfMetricInfo` (object)
    Hypervisor cluster performance metrics.

  - `clusterPerfMetricInfo.cpuCapacityInMhz` (integer)
    CPU allocated in mega hertz.

  - `clusterPerfMetricInfo.cpuUsageInMhz` (integer)
    CPU used in mega hertz.

  - `clusterPerfMetricInfo.memorySizeInBytes` (integer)
    Memory allocated in bytes.

  - `clusterPerfMetricInfo.memoryUsageInMb` (integer)
    Memory used in mega bytes.

  - `clusterPerfMetricInfo.totalStorageInBytes` (integer)
    Storage allocated in bytes.

  - `clusterPerfMetricInfo.usedStorageInBytes` (integer)
    Storage used in bytes.

  - `clusterType` (string)
    The type of the hypervisor cluster.
    Enum: "ESX_CLUSTER"

  - `customerId` (string)
    The customer application identifier.

  - `displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.
    Example: "myesxcluster1"

  - `hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.

  - `hypervisorHosts` (array)
    Captures the list of all hosts of this cluster. In a VMWare cluster, this entity maps to ESXi hosts.

  - `hypervisorHosts.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.

  - `hypervisorHosts.id` (string)
    UUID string uniquely identifying the hypervisor host.

  - `hypervisorHosts.name` (string)
    Name of the host as reported by the hypervisor manager.

  - `hypervisorHosts.resourceUri` (string)
    The URI reference for this resource.

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `name` (string)
    Name of the cluster as reported by the hypervisor manager.
    Example: "myesxcluster1"

  - `networksInfo` (array)
    All the network names associated with this cluster.
    Example: ["network-2053","network-1005"]

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-clusters/{cluster-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the hypervisor cluster object.
    Enum: "OK", "ERROR", "REFRESHING"

  - `stateReason` (string)
    Brief reason for the current state of the hypervisor cluster.

  - `status` (string)
    The current status of the hypervisor cluster. Status is derived and abstracted to a 'standard status' based on the status reported by the hypervisor manager.
    Enum: "OK", "ERROR", "WARNING"

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


