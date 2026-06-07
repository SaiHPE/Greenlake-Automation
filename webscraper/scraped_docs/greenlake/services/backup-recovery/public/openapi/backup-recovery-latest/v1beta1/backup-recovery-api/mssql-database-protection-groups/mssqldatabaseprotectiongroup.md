---
title: "GET /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongroup.md"
scraped_at: "2026-06-07T06:14:15.073458+00:00Z"
---

# Get an MSSQL database protection group resource identified by {group-id}.

Get detailed information for an MSSQL database protection group qualified by group-id.

Endpoint: GET /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `group-id` (string, required)
    UUID string uniquely identifying the MSSQL databse protection group
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the MSSQL databse protection group
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `createdAt` (string)
    Time in UTC at which the object was created.

  - `customerId` (string)
    The customer application identifier.

  - `description` (string)
    A brief description of the MSSQL database protection group.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `members` (array)
    Captures the list of databases that are part of the protection group.

  - `members.id` (string)
    The id of member database

  - `members.instanceInfo` (object)
    The mssql instance under which the database exists

  - `members.instanceInfo.id` (string)
    Unique identifier of the mssql instance
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `members.instanceInfo.name` (string)
    Name of the mssql instance.

  - `members.instanceInfo.resourceUri` (string)
    The uri of the mssql instance.
    Example: "/backup-recovery/v1beta1/mssql-instances/{instance-id}"

  - `members.name` (string)
    Name of the member database

  - `members.resourceUri` (string)
    The uri of member database

  - `name` (string)
    A user-friendly name to identify the MSSQL database protection group.
    Example: "My-Test-PG"

  - `nativeAppInfo` (object)

  - `nativeAppInfo.availabilityGroupReplicas` (array)
    The list of instances that are member of the availability group

  - `nativeAppInfo.availabilityGroupReplicas.id` (string)
    UUID string uniquely identifying the MSSQL Instance

  - `nativeAppInfo.availabilityGroupReplicas.name` (string)
    Name of the MSSQL instance as configured in the application host

  - `nativeAppInfo.availabilityGroupReplicas.resourceUri` (string)
    The 'self' reference for this resource.

  - `nativeAppInfo.availabilityGroupReplicas.role` (string)
    Role of the replica instance in this availability group.
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `nativeAppInfo.excludeSystemDatabases` (boolean)
    True if system databases are to be excluded from native protection group of type instance

  - `nativeAppInfo.id` (string)
    Unique identifier of the mssql native group when type is MSSQL_INSTANCE
    Example: "9ce540e3-b552-4ca6-a407-eb0dd3d263b1"

  - `nativeAppInfo.name` (string)
    Name of the mssql native group.

  - `nativeAppInfo.type` (string)
    Type of the native protection group.
    Enum: "AVAILABILITY_GROUP", "MSSQL_INSTANCE"

  - `nativeAppInfo.uid` (string)
    Unique identifier of the mssql native group when type is AVAILABILITY_GROUP
    Example: "7D0563C3-8627-4B33-96C7"

  - `protectionGroupType` (string)
    The type of the protection group. This can be 'NATIVE' for MSSQL application specific constructs such as an Availability Group, or 'CUSTOM' if its just a user provided collection of databases.
    Enum: "NATIVE", "CUSTOM"

  - `protectionJobInfo` (object)
    Information about the assigned Protection Policy and the Protection Job.

  - `protectionJobInfo.id` (string)
    UUID string uniquely identifying the Protection Job.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `protectionJobInfo.name` (string)
    name of the Protection Job.

  - `protectionJobInfo.protectionPolicyInfo` (object)
    Information about the Protection Policy that was used to create the job.

  - `protectionJobInfo.protectionPolicyInfo.id` (string)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `protectionJobInfo.protectionPolicyInfo.name` (string)
    User defined name of the Protection Policy.
    Example: "Gold-Protection-Policy"

  - `protectionJobInfo.protectionPolicyInfo.resourceUri` (string)
    Reference to resource

  - `protectionJobInfo.resourceUri` (string)
    Reference to resource.

  - `state` (string)
    The current state of the MSSQL databse protection group
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "DELETED"

  - `stateReason` (string)
    Brief reason for the current state of the MSSQL databse protection group

  - `status` (string)
    The current status of the MSSQL databse protection group.
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


