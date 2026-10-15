---
title: "GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/hypervisor-managers/hypervisormanager.md"
scraped_at: "2026-06-07T06:16:31.876435+00:00Z"
---

# Get a hypervisor manager resource identified by {hypervisor-id}.

Get detailed information for a registered hypervisor manager qualified by hypervisor-id.

Endpoint: GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `hypervisor-id` (string, required)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the hypervisor manager.
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
    Hypervisor specific information.

  - `appInfo.vmware` (object)
    VMware specific app info.

  - `appInfo.vmware.datacenters` (array)
    Captures all the data center details of the hypervisor manager. VMware: A virtual data center is a container for all the inventory objects required to complete a fully functional environment for operating virtual machines. Microsoft VMM: Datacenter components include virtualization servers, networking components, and storage resources.

  - `appInfo.vmware.datacenters.id` (string)
    UUID string uniquely identifier of the datacenter.
    Example: "16245bf7-2b35-5580-86a6-620faa5b5403"

  - `appInfo.vmware.datacenters.moref` (string)
    VMware provided moref for the datacenter.
    Example: "datacenter-2"

  - `appInfo.vmware.datacenters.name` (string)
    VMware provided name for the datacenter.
    Example: "core-team-dc"

  - `buildVersion` (string)
    The hypervisor manager build details
    Example: "6.7.0 build-9030300, NT 6.3, 3.8.13-44.1.1.el6uek.x86_64"

  - `customerId` (string)
    The customer application identifier.

  - `dataOrchestratorInfo` (object)
    Data Orchestrator specific information.

  - `dataOrchestratorInfo.id` (string)
    Unique string identifying the data orchestrator.
    Example: "8b4c14a6-3cd5-4907-97c4-cf44c5b642e5"

  - `dataOrchestratorInfo.resourceUri` (string)
    The URI reference for this resource.

  - `dataServicesConnectorsInfo` (array)
    Data Services Connectors specific information.

  - `dataServicesConnectorsInfo.id` (string)
    Unique string identifying the Data Services Connector.

  - `description` (string)
    A brief description of the hypervisor manager.

  - `displayName` (string)
    User defined name for the hypervisor manager.
    Example: "myvcenter1"

  - `hypervisorManagerType` (string)
    The type of the hypervisor manager. Currently only vCenter is supported.
    Enum: "VMWARE_VCENTER"

  - `lastRefreshed` (string)
    Time in UTC at which the object was last refreshed.

  - `name` (string)
    Name as reported by the hypervisor manager.
    Example: "vcenter123.hpe.com"

  - `networkAddress` (string)
    An IP address or hostname or FQDN to address the hypervisor manager
    Example: "192.168.0.1"

  - `releaseVersion` (string)
    The hypervisor manager release version.
    Example: "6.7.0 build-9030300, R2, 7.2"

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}"

  - `services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `state` (string)
    The current state of the hypervisor manager object
    Enum: "OK", "ERROR", "INITIALIZING", "CREATING", "DELETING", "UPDATING", "REFRESHING", "CONFIGURED"

  - `stateReason` (string)
    Brief reason for the current state of the hypervisor manager

  - `status` (string)
    The current status of the hypervisor manager resource.
    Enum: "OK", "ERROR", "WARNING"

  - `uid` (string)
    A hypervisor manager provided durable UID. In case of VMware it will be instanceUUID of the vCenter

  - `username` (string)
    Name of the user used to access the hypervisor server. Mutually exclusive with credentialInfo.

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

## Response 503 fields (application/json):

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


