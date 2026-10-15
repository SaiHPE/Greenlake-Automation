---
title: "GET /backup-recovery/v1beta1/mssql-database-protection-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongrouplist.md"
scraped_at: "2026-06-07T06:14:15.000237+00:00Z"
---

# Get all MSSQL database protection groups.

List all the MSSQL database protection groups.

Endpoint: GET /backup-recovery/v1beta1/mssql-database-protection-groups
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
* GET /backup-recovery/v1beta1/mssql-database-protection-groups?filter="name eq my-mssql-pg1"

Filters are supported on the following attributes:
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
    UUID string uniquely identifying the MSSQL databse protection group
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.createdAt` (string)
    Time in UTC at which the object was created.

  - `items.customerId` (string)
    The customer application identifier.

  - `items.description` (string)
    A brief description of the MSSQL database protection group.

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.members` (array)
    Captures the list of databases that are part of the protection group.

  - `items.members.id` (string)
    The id of member database

  - `items.members.instanceInfo` (object)
    The mssql instance under which the database exists

  - `items.members.instanceInfo.id` (string)
    Unique identifier of the mssql instance
    Example: "1b738651-da9f-4c85-88c1-70dbfe1976681"

  - `items.members.instanceInfo.name` (string)
    Name of the mssql instance.

  - `items.members.instanceInfo.resourceUri` (string)
    The uri of the mssql instance.
    Example: "/backup-recovery/v1beta1/mssql-instances/{instance-id}"

  - `items.members.name` (string)
    Name of the member database

  - `items.members.resourceUri` (string)
    The uri of member database

  - `items.name` (string)
    A user-friendly name to identify the MSSQL database protection group.
    Example: "My-Test-PG"

  - `items.nativeAppInfo` (object)

  - `items.nativeAppInfo.availabilityGroupReplicas` (array)
    The list of instances that are member of the availability group

  - `items.nativeAppInfo.availabilityGroupReplicas.id` (string)
    UUID string uniquely identifying the MSSQL Instance

  - `items.nativeAppInfo.availabilityGroupReplicas.name` (string)
    Name of the MSSQL instance as configured in the application host

  - `items.nativeAppInfo.availabilityGroupReplicas.resourceUri` (string)
    The 'self' reference for this resource.

  - `items.nativeAppInfo.availabilityGroupReplicas.role` (string)
    Role of the replica instance in this availability group.
    Enum: "PRIMARY", "SECONDARY", "UNAVAILABLE"

  - `items.nativeAppInfo.excludeSystemDatabases` (boolean)
    True if system databases are to be excluded from native protection group of type instance

  - `items.nativeAppInfo.id` (string)
    Unique identifier of the mssql native group when type is MSSQL_INSTANCE
    Example: "9ce540e3-b552-4ca6-a407-eb0dd3d263b1"

  - `items.nativeAppInfo.name` (string)
    Name of the mssql native group.

  - `items.nativeAppInfo.type` (string)
    Type of the native protection group.
    Enum: "AVAILABILITY_GROUP", "MSSQL_INSTANCE"

  - `items.nativeAppInfo.uid` (string)
    Unique identifier of the mssql native group when type is AVAILABILITY_GROUP
    Example: "7D0563C3-8627-4B33-96C7"

  - `items.protectionGroupType` (string)
    The type of the protection group. This can be 'NATIVE' for MSSQL application specific constructs such as an Availability Group, or 'CUSTOM' if its just a user provided collection of databases.
    Enum: "NATIVE", "CUSTOM"

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

  - `items.state` (string)
    The current state of the MSSQL databse protection group
    Enum: "OK", "ERROR", "CREATING", "DELETING", "UPDATING", "DELETED"

  - `items.stateReason` (string)
    Brief reason for the current state of the MSSQL databse protection group

  - `items.status` (string)
    The current status of the MSSQL databse protection group.
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


