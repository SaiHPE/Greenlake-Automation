---
title: "GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/resource-pools/{pool-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/virtualization-api/resource-pools/hypervisorresourcepool.md"
scraped_at: "2026-06-07T06:16:29.501217+00:00Z"
---

# Get a hypervisor resource pool identified by {pool-id}.

Details of a hypervisors resource pool.

Endpoint: GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/resource-pools/{pool-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `hypervisor-id` (string, required)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `pool-id` (string, required)
    UUID string uniquely identifying the hypervisor resource pool resource.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the hypervisor resource pool resource.
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
    Application specific information for this resource pool.

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
    VMware provided moref for this resource pool.
    Example: "resgroup-21"

  - `childResourcePools` (array)
    Captures the list of all child resource pools.

  - `childResourcePools.displayName` (string)
    A user-friendly name that identifies the hypervisor resource pool. This will always be same as name since adding or updating hypervisor resource pools is not supported when managed from a manager, such as the vCenter.

  - `childResourcePools.name` (string)
    Name of the resource pool as reported by the hypervisor manager.

  - `childResourcePools.resourceUri` (string)
    The URI reference for this resource.

  - `clusterInfo` (object)
    Hypervisor cluster information.

  - `clusterInfo.displayName` (string)
    A user-friendly name that identifies the hypervisor cluster. This will always be same as name since adding or updating hypervisor clusters is not supported when managed from a manager, such as the vCenter.

  - `clusterInfo.id` (string)
    UUID string uniquely identifying the hypervisor cluster.

  - `clusterInfo.moref` (string)
    Moref of the hypervisor cluster.
    Example: "cluster-01"

  - `clusterInfo.name` (string)
    Name of the cluster as reported by the hypervisor manager.

  - `customerId` (string)
    The customer application identifier.

  - `hypervisorManagerInfo` (object)

  - `hypervisorManagerInfo.displayName` (string)
    User defined name for the hypervisor manager.

  - `hypervisorManagerInfo.id` (string)
    UUID string uniquely identifying the hypervisor manager.

  - `hypervisorManagerInfo.name` (string)
    Name as reported by the hypervisor manager.

  - `ownerInfo` (object)
    Owner of this resource pool.

  - `ownerInfo.id` (string)
    UUID of the owner of this resource pool.
    Example: "5ed25c1e-04b2-5636-82fa-61d080b76858"

  - `ownerInfo.name` (string)
    Name of the owner of this resource pool.
    Example: "Cluster1"

  - `ownerInfo.type` (string)
    Type of the owner of this resource pool.
    Example: "Cluster"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/resource-pools/{pool-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the hypervisor resource pool.
    Enum: "OK", "ERROR", "REFRESHING"

  - `stateReason` (string)
    Brief reason for the current state of the hypervisor resource pool.

  - `status` (string)
    The current status of the hypervisor resource pool. Status is derived and abstracted to a 'standard status' based on the status reported by the hypervisor manager.
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


