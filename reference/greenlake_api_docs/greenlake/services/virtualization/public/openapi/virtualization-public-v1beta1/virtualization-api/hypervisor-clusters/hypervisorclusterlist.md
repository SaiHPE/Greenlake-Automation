---
title: "GET /virtualization/v1beta1/hypervisor-clusters"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/hypervisor-clusters/hypervisorclusterlist.md"
scraped_at: "2026-06-07T06:16:28.285085+00:00Z"
---

# Get all clusters across registered hypervisor managers.

List all the hypervisors clusters across registered hypervisor managers.

Endpoint: GET /virtualization/v1beta1/hypervisor-clusters
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
* GET /virtualization/v1beta1/hypervisor-clusters?filter="clusterType eq ESX_CLUSTER"
* GET /virtualization/v1beta1/hypervisor-clusters?filter="clusterType eq ESX_CLUSTER and status eq ERROR"

Filters are supported on the following attributes:
* clusterType
* id
* state
* hypervisorManagerInfo/name
* hypervisorManagerInfo/displayName
* hypervisorManagerInfo/id
* status
* createdAt
* hciClusterUuid
* name
* services
* displayName
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
    UUID string uniquely identifying the hypervisor cluster.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created.

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `items.appInfo` (object)
    Application specific information for this cluster.

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
    VMware provided moref for this cluster.
    Example: "domain-c8"

  - `items.clusterPerfMetricInfo` (object)
    Hypervisor cluster performance metrics.

  - `items.clusterPerfMetricInfo.cpuCapacityInMhz` (integer)
    CPU allocated in mega hertz.

  - `items.clusterPerfMetricInfo.cpuUsageInMhz` (integer)
    CPU used in mega hertz.

  - `items.clusterPerfMetricInfo.memorySizeInBytes` (integer)
    Memory allocated in bytes.

  - `items.clusterPerfMetricInfo.memoryUsageInMb` (integer)
    Memory used in mega bytes.

  - `items.clusterPerfMetricInfo.totalStorageInBytes` (integer)
    Storage allocated in bytes.

  - `items.clusterPerfMetricInfo.usedStorageInBytes` (integer)
    Storage used in bytes.

  - `items.clusterType` (string)
    The type of the hypervisor cluster.
    Enum: "ESX_CLUSTER"

  - `items.customerId` (string)
    The customer application identifier.

  - `items.displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.
    Example: "myesxcluster1"

  - `items.hciClusterUuid` (string)
    UUID string uniquely identifying the HCI cluster.

  - `items.hypervisorHosts` (array)
    Captures the list of all hosts of this cluster. In a VMWare cluster, this entity maps to ESXi hosts.

  - `items.hypervisorHosts.displayName` (string)
    A user-friendly name that identifies the hypervisor host. This will always be same as name since adding or updating hypervisor hosts is not supported when managed from a manager, such as the vCenter.

  - `items.hypervisorHosts.id` (string)
    UUID string uniquely identifying the hypervisor host.

  - `items.hypervisorHosts.name` (string)
    Name of the host as reported by the hypervisor manager.

  - `items.hypervisorHosts.resourceUri` (string)
    The URI reference for this resource.

  - `items.hypervisorManagerInfo` (object)

  - `items.hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `items.hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `items.hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `items.name` (string)
    Name of the cluster as reported by the hypervisor manager.
    Example: "myesxcluster1"

  - `items.networksInfo` (array)
    All the network names associated with this cluster.
    Example: ["network-2053","network-1005"]

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-clusters/{cluster-id}"

  - `items.services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `items.state` (string)
    The current state of the hypervisor cluster object.
    Enum: "OK", "ERROR", "REFRESHING"

  - `items.stateReason` (string)
    Brief reason for the current state of the hypervisor cluster.

  - `items.status` (string)
    The current status of the hypervisor cluster. Status is derived and abstracted to a 'standard status' based on the status reported by the hypervisor manager.
    Enum: "OK", "ERROR", "WARNING"

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


