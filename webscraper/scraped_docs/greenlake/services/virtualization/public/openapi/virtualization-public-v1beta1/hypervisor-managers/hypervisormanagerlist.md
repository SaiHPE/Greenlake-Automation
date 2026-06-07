---
title: "GET /virtualization/v1beta1/hypervisor-managers"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/hypervisor-managers/hypervisormanagerlist.md"
scraped_at: "2026-06-07T06:16:31.874476+00:00Z"
---

# Get all registered hypervisor managers.

List all the registered hypervisor managers.

Endpoint: GET /virtualization/v1beta1/hypervisor-managers
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

A comparison compares a property name to a literal. The comparisons supported are the following:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “ne” : Is a property not equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /virtualization/v1beta1/hypervisor-managers?filter="hypervisorManagerType eq VMWARE_VCENTER"
* GET /virtualization/v1beta1/hypervisor-managers?filter="hypervisorManagerType eq VMWARE_VCENTER and status eq ERROR"

Filters are supported on the following attributes:
* hypervisorManagerType
* state
* status
* releaseVersion
* createdAt
* name
* services
* dataOrchestratorInfo/id
* username
* networkAddress
* displayName

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
    UUID string uniquely identifying the hypervisor manager.
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
    Hypervisor specific information.

  - `items.appInfo.vmware` (object)
    VMware specific app info.

  - `items.appInfo.vmware.datacenters` (array)
    Captures all the data center details of the hypervisor manager. VMware: A virtual data center is a container for all the inventory objects required to complete a fully functional environment for operating virtual machines. Microsoft VMM: Datacenter components include virtualization servers, networking components, and storage resources.

  - `items.appInfo.vmware.datacenters.id` (string)
    UUID string uniquely identifier of the datacenter.
    Example: "16245bf7-2b35-5580-86a6-620faa5b5403"

  - `items.appInfo.vmware.datacenters.moref` (string)
    VMware provided moref for the datacenter.
    Example: "datacenter-2"

  - `items.appInfo.vmware.datacenters.name` (string)
    VMware provided name for the datacenter.
    Example: "core-team-dc"

  - `items.buildVersion` (string)
    The hypervisor manager build details
    Example: "6.7.0 build-9030300, NT 6.3, 3.8.13-44.1.1.el6uek.x86_64"

  - `items.customerId` (string)
    The customer application identifier.

  - `items.dataOrchestratorInfo` (object)
    Data Orchestrator specific information.

  - `items.dataOrchestratorInfo.id` (string)
    Unique string identifying the data orchestrator.
    Example: "8b4c14a6-3cd5-4907-97c4-cf44c5b642e5"

  - `items.dataOrchestratorInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.dataServicesConnectorsInfo` (array)
    Data Services Connectors specific information.

  - `items.dataServicesConnectorsInfo.id` (string)
    Unique string identifying the Data Services Connector.

  - `items.description` (string)
    A brief description of the hypervisor manager.

  - `items.displayName` (string)
    User defined name for the hypervisor manager.
    Example: "myvcenter1"

  - `items.hypervisorManagerType` (string)
    The type of the hypervisor manager. Currently only vCenter is supported.
    Enum: "VMWARE_VCENTER"

  - `items.lastRefreshed` (string)
    Time in UTC at which the object was last refreshed.

  - `items.name` (string)
    Name as reported by the hypervisor manager.
    Example: "vcenter123.hpe.com"

  - `items.networkAddress` (string)
    An IP address or hostname or FQDN to address the hypervisor manager
    Example: "192.168.0.1"

  - `items.releaseVersion` (string)
    The hypervisor manager release version.
    Example: "6.7.0 build-9030300, R2, 7.2"

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/virtualization/v1beta1/hypervisor-managers/{hypervisor-id}"

  - `items.services` (array)
    List of services this object belongs to.  This list can be used to filter specific services in the UI.

  - `items.state` (string)
    The current state of the hypervisor manager object
    Enum: "OK", "ERROR", "INITIALIZING", "CREATING", "DELETING", "UPDATING", "REFRESHING", "CONFIGURED"

  - `items.stateReason` (string)
    Brief reason for the current state of the hypervisor manager

  - `items.status` (string)
    The current status of the hypervisor manager resource.
    Enum: "OK", "ERROR", "WARNING"

  - `items.uid` (string)
    A hypervisor manager provided durable UID. In case of VMware it will be instanceUUID of the vCenter

  - `items.username` (string)
    Name of the user used to access the hypervisor server. Mutually exclusive with credentialInfo.

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


