---
title: "GET /backup-recovery/v1beta1/volume-protection-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongrouplist.md"
scraped_at: "2026-06-07T06:14:07.730364+00:00Z"
---

# Get all Volume Protection Groups.

List all Volume Protection Groups.

Endpoint: GET /backup-recovery/v1beta1/volume-protection-groups
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
“eq” : Is a property equal to value. Valid for number, boolean and string properties.
“gt” : Is a property greater than a value. Valid for number or string timestamp properties.
“lt” : Is a property less than a value. Valid for number or string timestamp properties
“in” : Is a value in a property (that is an array of strings)
Examples:
GET /backup-recovery/v1beta1/volume-protection-groups?filter=volumeProtectionGroupType eq NATIVE
          
Filters are supported on following attributes:
* volumeProtectionGroupType
* createdAt
* name

  - `sort` (string)
    Comma separated list of properties defining the sort order

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)
    Time in UTC at which the object was created.

  - `items.updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `items.assets` (array)
    Captures the list of volumes that would be part of the Protection Group.

  - `items.assets.displayName` (string)
    Name provided for the asset

  - `items.assets.id` (string)
    Volume identifier

  - `items.assets.protectionStatus` (string)
    Provides the current protection status of this resource. - UNPROTECTED - No policy assigned, No recovery points exists - LAPSED      - No policy assigned, at least one recovery points exists - PENDING     - Policy assigned, No recovery points exists - PARTIAL     - Policy assigned, At least one recovery point exists - PROTECTED   - Policy assigned, most recent run of every configured schedule is successful - PAUSED      - Policy assigned, one or more of the schedules are paused
    Enum: "UNPROTECTED", "LAPSED", "PENDING", "PARTIAL", "PROTECTED", "PAUSED"

  - `items.assets.resourceUri` (string)
    Reference to resource.

  - `items.consoleUri` (string)
    The URI for console screen that displays this object.

  - `items.description` (string)
    A brief description of the Protection Group.

  - `items.name` (string)
    A user-friendly name to identify Volume Protection Group.
    Example: "myProtectionGroup"

  - `items.nativeGroupInfo` (object)

  - `items.nativeGroupInfo.id` (string)
    UUID string uniquely identifying the native group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.nativeGroupInfo.name` (string)
    Name of the native group.
    Example: "volume protection native group."

  - `items.nativeGroupInfo.type` (string)
    type of the native Protection Group.
    Enum: "VOLUME_COLLECTION", "APPLICATION_SET"

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

  - `items.resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/volume-protection-groups/9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.state` (string)
    Current state of the group
    Enum: "OK", "ERROR", "CREATING", "ATTACHED", "DETACHING", "DETACHED", "DISCOVERING", "DISCOVERED", "CLEANING_UP", "CLEANED_UP", "RESTORING_BACKUP", "RESTORING_SNAPSHOT", "RESTORE_FAILED", "DELETED", "DELETING", "PARTIAL_RESTORE", "UPDATING", "REFRESHING"

  - `items.stateReason` (string)
    Brief reason for the current state of the group

  - `items.status` (string)
    Current status of the group
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageSystemInfo` (object)
    Describes a storage system.

  - `items.storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `items.storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `items.storageSystemInfo.productFamily` (string)
    Product Family
    Example: "deviceType1"

  - `items.storageSystemInfo.resourceUri` (string)
    The URI reference for this resource.

  - `items.storageSystemInfo.type` (string)
    Type of storage system.

  - `items.volumeProtectionGroupType` (string)
    The type of the Protection Group. This can be Native for storage system specific constructs and Custom if its just a collection of assets (Volume).
    Enum: "NATIVE", "CUSTOM"

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


