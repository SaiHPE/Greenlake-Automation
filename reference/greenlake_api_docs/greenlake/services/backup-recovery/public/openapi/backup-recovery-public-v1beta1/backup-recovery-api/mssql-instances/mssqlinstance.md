---
title: "GET /backup-recovery/v1beta1/mssql-instances/{instance-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-instances/mssqlinstance.md"
scraped_at: "2026-06-07T06:14:04.158994+00:00Z"
---

# Get an MSSQL instance resource identified by {instance-id}.

Get detailed information for a discovered MSSQL instance qualified by instance-id.

Endpoint: GET /backup-recovery/v1beta1/mssql-instances/{instance-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `instance-id` (string, required)
    UUID string uniquely identifying the MSSQL Instance
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the MSSQL Instance
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `applicationHostInfo` (object)
    The application host on which the instance exists.

  - `applicationHostInfo.displayName` (string)
    A user-friendly name to identify the application host

  - `applicationHostInfo.id` (string)
    UUID string uniquely identifying the application host

  - `applicationHostInfo.name` (string)
    The host name as reported by the host.

  - `applicationHostInfo.resourceUri` (string)
    The 'self' reference for this resource.

  - `availabilityGroupsInfo` (array)
    The list of availability groups that are part of the instance.

  - `availabilityGroupsInfo.name` (string)
    Name of the mssql availability group.

  - `availabilityGroupsInfo.replicas` (array)
    The list of instances that are member of the availability group

  - `availabilityGroupsInfo.replicas.name` (string)
    Name of the MSSQL instance as configured in the application host

  - `availabilityGroupsInfo.replicas.role` (string)
    Role of the replica instance in this availability group.
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `availabilityGroupsInfo.role` (string)
    Role of the parent instance in this availability group
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `availabilityGroupsInfo.uid` (string)
    Unique identifier of the mssql availability group as reported by SQL
    Example: "7D0563C3-8627-4B33-96C7"

  - `clustered` (boolean)
    Indicates if the mssql instance is part of a cluster

  - `createdAt` (string)
    Time in UTC at which the object was created.

  - `credentials` (object)
    MSSQL instance credentials info

  - `credentials.mode` (string)
    Mode of accessing MSSQL Instance
    Enum: "WINDOWS", "SQL"

  - `credentials.username` (string)
    Name of the user used to access the MSSQL Instance

  - `customerId` (string)
    The customer application identifier.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `productName` (string)
    A name identifying the MSSQL database software product.
    Example: "Microsoft SQL Server 2012 R2"

  - `productVersion` (string)
    Version of the MSSQL databse software.
    Example: "10.3.2"

  - `state` (string)
    The current state of the MSSQL instance
    Enum: "OK", "UNAVAILABLE", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "DELETED"

  - `stateReason` (string)
    Brief reason for the current state of the MSSQL instance

  - `status` (string)
    The current status of the MSSQL instance.
    Enum: "OK", "ERROR", "WARNING"

  - `updatedAt` (string)
    Time in UTC at which the object was last updated.

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


