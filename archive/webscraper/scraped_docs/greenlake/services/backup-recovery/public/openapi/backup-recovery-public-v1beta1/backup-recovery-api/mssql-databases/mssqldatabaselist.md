---
title: "GET /backup-recovery/v1beta1/mssql-databases"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/mssql-databases/mssqldatabaselist.md"
scraped_at: "2026-06-07T06:14:03.853048+00:00Z"
---

# Get all discovered MSSQL databases.

List all the discovered MSSQL databases.

Endpoint: GET /backup-recovery/v1beta1/mssql-databases
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

A comparison compares a property name to a literal. The following comparisons are supported:
* “eq” : Is a property equal to value. Valid for number, boolean and string properties.
* “gt” : Is a property greater than a value. Valid for number or string timestamp properties.
* “lt” : Is a property less than a value. Valid for number or string timestamp properties
* “in” : Is a value in a property (that is an array of strings)

Examples:
* GET /backup-recovery/v1beta1/mssql-databases?filter="name eq billing-db-1"
* GET /backup-recovery/v1beta1/mssql-databases?filter="applicationHostInfo/name eq myhost1 and status eq Error"


Filters are supported on the following attributes:
* state
* status
* applicationHostInfo/id
* applicationHostInfo/name
* mssqlDatabaseProtectionGroupInfo/id
* mssqlDatabaseProtectionGroupInfo/name
* virtualizationInfo/hypervisorManagerInfo/id
* createdAt
* name

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
    UUID string uniquely identifying the MSSQL Database
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.applicationHostInfo` (object)
    The application host on which the database exists. In case of cluster this will be the active host

  - `items.applicationHostInfo.displayName` (string)
    A user-friendly name to identify the application host

  - `items.applicationHostInfo.id` (string)
    UUID string uniquely identifying the application host

  - `items.applicationHostInfo.name` (string)
    The host name as reported by the host.

  - `items.applicationHostInfo.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.availabilityGroupInfo` (object)
    Details of the availability group this resource is associated to.

  - `items.availabilityGroupInfo.name` (string)
    Name of the mssql availability group.

  - `items.availabilityGroupInfo.role` (string)
    Role of the parent instance in this availability group.
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `items.availabilityGroupInfo.uid` (string)
    Unique identifier of the mssql availability group as reported by SQL.
    Example: "7D0563C3-8627-4B33-96C7"

  - `items.clusterInfo` (object)
    Cluster related information for the database

  - `items.clusterInfo.clustered` (boolean)
    Indicates if the mssql database is part of a cluster

  - `items.clusterInfo.role` (string)
    The role of the database
    Enum: "PRIMARY", "SECONDARY", "UNKWOWN"

  - `items.createdAt` (string)
    Time in UTC at which the object was created.

  - `items.customerId` (string)
    The customer application identifier.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.instanceInfo` (object)
    The mssql instance under which the database exists

  - `items.instanceInfo.id` (string)
    Unique identifier of the mssql instance
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.instanceInfo.name` (string)
    Name of the mssql instance.

  - `items.instanceInfo.resourceUri` (string)
    The uri of the mssql instance.
    Example: "/backup-recovery/v1beta1/mssql-instances/{instance-id}"

  - `items.mssqlDatabaseProtectionGroupInfo` (object)
    Information of the mssql database protection group.

  - `items.mssqlDatabaseProtectionGroupInfo.id` (string)
    Unique identifier for the mssql database protection group.
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.mssqlDatabaseProtectionGroupInfo.name` (string)
    Name of the mssql database protection group.
    Example: "my-protection-group"

  - `items.mssqlDatabaseProtectionGroupInfo.resourceUri` (string)
    The uri of the mssql database protection group.
    Example: "/backup-recovery/v1beta1/mssql-database-protection-groups/{protection-group-id}"

  - `items.name` (string)
    Name of the MSSQL Database as configured in the application host
    Example: "billing-db1"

  - `items.protectionJobInfo` (object)
    Information about the assigned Protection Policy and the Protection Job.

  - `items.protectionJobInfo.id` (string)
    UUID string uniquely identifying the Protection Job.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.protectionJobInfo.name` (string)
    name of the Protection Job.

  - `items.protectionJobInfo.protectionPolicyInfo` (object)
    Information about the Protection Policy that was used to create the job.

  - `items.protectionJobInfo.protectionPolicyInfo.id` (string)
    UUID string uniquely identifying the Protection Policy.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.protectionJobInfo.protectionPolicyInfo.name` (string)
    User defined name of the Protection Policy.
    Example: "Gold-Protection-Policy"

  - `items.protectionJobInfo.protectionPolicyInfo.resourceUri` (string)
    Reference to resource

  - `items.protectionJobInfo.resourceUri` (string)
    Reference to resource.

  - `items.protectionStatus` (string)
    Provides the current protection status of this resource. - UNPROTECTED - No policy assigned, No recovery points exists - LAPSED      - No policy assigned, at least one recovery points exists - PENDING     - Policy assigned, No recovery points exists - PARTIAL     - Policy assigned, At least one recovery point exists - PROTECTED   - Policy assigned, most recent run of every configured schedule is successful - PAUSED      - Policy assigned, one or more of the schedules are paused - UNSUPPORTED - No policy can be assigned
    Enum: "UNPROTECTED", "LAPSED", "PENDING", "PARTIAL", "PROTECTED", "PAUSED", "UNSUPPORTED"

  - `items.recoveryPointsExist` (boolean)
    Indicates at least one valid recovery point exists for this resource.
    Example: true

  - `items.sizeInBytes` (integer)
    size of the database in bytes.
    Example: 2407653459860

  - `items.state` (string)
    The current state of the MSSQL Database
    Enum: "OK", "UNAVAILABLE", "ERROR", "CREATING", "DELETING", "UPDATING", "REFRESHING", "RESTORING", "DELETED"

  - `items.stateReason` (string)
    Brief reason for the current state of the MSSQL Database

  - `items.status` (string)
    The current status of the MSSQL Database.
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


