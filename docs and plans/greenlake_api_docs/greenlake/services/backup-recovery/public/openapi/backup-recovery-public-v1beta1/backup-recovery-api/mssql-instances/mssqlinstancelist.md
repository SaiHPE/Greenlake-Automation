---
title: "GET /backup-recovery/v1beta1/mssql-instances"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-instances/mssqlinstancelist.md"
scraped_at: "2026-06-07T06:14:04.079638+00:00Z"
---

# Get all discovered MSSQL instances.

List all the discovered MSSQL instances.

Endpoint: GET /backup-recovery/v1beta1/mssql-instances
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

A comparison compares a property name to a literal. The comparisons supported are the following:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /backup-recovery/v1beta1/mssql-instances?filter="productName eq Microsoft+SQL+Server+2012+R2"
* GET /backup-recovery/v1beta1/mssql-instances?filter="applicationHostInfo/name eq my-host-1 and status eq Error"


Filters are supported on the following attributes:
* state
* status
* createdAt
* name
* productName
* productVersion
* applicationHostInfo/id
* applicationHostInfo/name

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
    UUID string uniquely identifying the MSSQL Instance
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.applicationHostInfo` (object)
    The application host on which the instance exists.

  - `items.applicationHostInfo.displayName` (string)
    A user-friendly name to identify the application host

  - `items.applicationHostInfo.id` (string)
    UUID string uniquely identifying the application host

  - `items.applicationHostInfo.name` (string)
    The host name as reported by the host.

  - `items.applicationHostInfo.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.availabilityGroupsInfo` (array)
    The list of availability groups that are part of the instance.

  - `items.availabilityGroupsInfo.name` (string)
    Name of the mssql availability group.

  - `items.availabilityGroupsInfo.replicas` (array)
    The list of instances that are member of the availability group

  - `items.availabilityGroupsInfo.replicas.name` (string)
    Name of the MSSQL instance as configured in the application host

  - `items.availabilityGroupsInfo.replicas.role` (string)
    Role of the replica instance in this availability group.
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `items.availabilityGroupsInfo.role` (string)
    Role of the parent instance in this availability group
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `items.availabilityGroupsInfo.uid` (string)
    Unique identifier of the mssql availability group as reported by SQL
    Example: "7D0563C3-8627-4B33-96C7"

  - `items.clustered` (boolean)
    Indicates if the mssql instance is part of a cluster

  - `items.createdAt` (string)
    Time in UTC at which the object was created.

  - `items.credentials` (object)
    MSSQL instance credentials info

  - `items.credentials.mode` (string)
    Mode of accessing MSSQL Instance
    Enum: "WINDOWS", "SQL"

  - `items.credentials.username` (string)
    Name of the user used to access the MSSQL Instance

  - `items.customerId` (string)
    The customer application identifier.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.productName` (string)
    A name identifying the MSSQL database software product.
    Example: "Microsoft SQL Server 2012 R2"

  - `items.productVersion` (string)
    Version of the MSSQL databse software.
    Example: "10.3.2"

  - `items.state` (string)
    The current state of the MSSQL instance
    Enum: "OK", "UNAVAILABLE", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "DELETED"

  - `items.stateReason` (string)
    Brief reason for the current state of the MSSQL instance

  - `items.status` (string)
    The current status of the MSSQL instance.
    Enum: "OK", "ERROR", "WARNING"

  - `items.updatedAt` (string)
    Time in UTC at which the object was last updated.

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


