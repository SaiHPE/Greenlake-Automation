---
title: "GET /backup-recovery/v1beta1/mssql-databases/{db-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-databases/mssqldatabase.md"
scraped_at: "2026-06-07T06:14:03.924387+00:00Z"
---

# Get an MSSQL database resource identified by {db-id}.

Get detailed information for a discovered MSSQL database qualified by db-id.

Endpoint: GET /backup-recovery/v1beta1/mssql-databases/{db-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `db-id` (string, required)
    UUID string uniquely identifying the MSSQL Database
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the MSSQL Database
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `applicationHostInfo` (object)
    The application host on which the database exists. In case of cluster this will be the active host

  - `applicationHostInfo.displayName` (string)
    A user-friendly name to identify the application host

  - `applicationHostInfo.id` (string)
    UUID string uniquely identifying the application host

  - `applicationHostInfo.name` (string)
    The host name as reported by the host.

  - `applicationHostInfo.resourceUri` (string)
    The 'self' reference for this resource.

  - `availabilityGroupInfo` (object)
    Details of the availability group this resource is associated to.

  - `availabilityGroupInfo.name` (string)
    Name of the mssql availability group.

  - `availabilityGroupInfo.role` (string)
    Role of the parent instance in this availability group.
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `availabilityGroupInfo.uid` (string)
    Unique identifier of the mssql availability group as reported by SQL.
    Example: "7D0563C3-8627-4B33-96C7"

  - `clusterInfo` (object)
    Cluster related information for the database

  - `clusterInfo.clustered` (boolean)
    Indicates if the mssql database is part of a cluster

  - `clusterInfo.role` (string)
    The role of the database
    Enum: "PRIMARY", "SECONDARY", "UNKWOWN"

  - `createdAt` (string)
    Time in UTC at which the object was created.

  - `customerId` (string)
    The customer application identifier.

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `instanceInfo` (object)
    The mssql instance under which the database exists

  - `instanceInfo.id` (string)
    Unique identifier of the mssql instance
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `instanceInfo.name` (string)
    Name of the mssql instance.

  - `instanceInfo.resourceUri` (string)
    The uri of the mssql instance.
    Example: "/backup-recovery/v1beta1/mssql-instances/{instance-id}"

  - `mssqlDatabaseProtectionGroupInfo` (object)
    Information of the mssql database protection group.

  - `mssqlDatabaseProtectionGroupInfo.id` (string)
    Unique identifier for the mssql database protection group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `mssqlDatabaseProtectionGroupInfo.name` (string)
    Name of the mssql database protection group.
    Example: "my-protection-group"

  - `mssqlDatabaseProtectionGroupInfo.resourceUri` (string)
    The uri of the mssql database protection group.
    Example: "/backup-recovery/v1beta1/mssql-database-protection-groups/{protection-group-id}"

  - `name` (string)
    Name of the MSSQL Database as configured in the application host
    Example: "billing-db1"

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

  - `protectionStatus` (string)
    Provides the current protection status of this resource. - UNPROTECTED - No policy assigned, No recovery points exists - LAPSED      - No policy assigned, at least one recovery points exists - PENDING     - Policy assigned, No recovery points exists - PARTIAL     - Policy assigned, At least one recovery point exists - PROTECTED   - Policy assigned, most recent run of every configured schedule is successful - PAUSED      - Policy assigned, one or more of the schedules are paused - UNSUPPORTED - No policy can be assigned
    Enum: "UNPROTECTED", "LAPSED", "PENDING", "PARTIAL", "PROTECTED", "PAUSED", "UNSUPPORTED"

  - `recoveryPointsExist` (boolean)
    Indicates at least one valid recovery point exists for this resource.
    Example: true

  - `sizeInBytes` (integer)
    size of the database in bytes.
    Example: 2407653459860

  - `state` (string)
    The current state of the MSSQL Database
    Enum: "OK", "UNAVAILABLE", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "DELETED"

  - `stateReason` (string)
    Brief reason for the current state of the MSSQL Database

  - `status` (string)
    The current status of the MSSQL Database.
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


