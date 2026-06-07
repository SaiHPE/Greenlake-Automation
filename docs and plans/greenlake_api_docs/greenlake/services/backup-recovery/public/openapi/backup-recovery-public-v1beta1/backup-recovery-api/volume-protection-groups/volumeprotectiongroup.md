---
title: "GET /backup-recovery/v1beta1/volume-protection-groups/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongroup.md"
scraped_at: "2026-06-07T06:14:07.954401+00:00Z"
---

# Get a Volume Protection Group resource identified by {id}.

Get detailed information for a registered Volume Protection Group qualified by id.

Endpoint: GET /backup-recovery/v1beta1/volume-protection-groups/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `type` (string, required)
    The type of resource.

  - `generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `createdAt` (string, required)
    Time in UTC at which the object was created.

  - `updatedAt` (string, required)
    Time in UTC at which the object was last updated.

  - `assets` (array)
    Captures the list of volumes that would be part of the Protection Group.

  - `assets.displayName` (string)
    Name provided for the asset

  - `assets.id` (string)
    Volume identifier

  - `assets.protectionStatus` (string)
    Provides the current protection status of this resource. - UNPROTECTED - No policy assigned, No recovery points exists - LAPSED      - No policy assigned, at least one recovery points exists - PENDING     - Policy assigned, No recovery points exists - PARTIAL     - Policy assigned, At least one recovery point exists - PROTECTED   - Policy assigned, most recent run of every configured schedule is successful - PAUSED      - Policy assigned, one or more of the schedules are paused
    Enum: "UNPROTECTED", "LAPSED", "PENDING", "PARTIAL", "PROTECTED", "PAUSED"

  - `assets.resourceUri` (string)
    Reference to resource.

  - `consoleUri` (string)
    The URI for console screen that displays this object.

  - `description` (string)
    A brief description of the Protection Group.

  - `name` (string)
    A user-friendly name to identify Volume Protection Group.
    Example: "myProtectionGroup"

  - `nativeGroupInfo` (object)

  - `nativeGroupInfo.id` (string)
    UUID string uniquely identifying the native group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `nativeGroupInfo.name` (string)
    Name of the native group.
    Example: "volume protection native group."

  - `nativeGroupInfo.type` (string)
    type of the native Protection Group.
    Enum: "VOLUME_COLLECTION", "APPLICATION_SET"

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

  - `resourceUri` (string)
    The 'self' reference for this resource.
    Example: "/backup-recovery/v1beta1/volume-protection-groups/9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `state` (string)
    Current state of the group
    Enum: "OK", "ERROR", "CREATING", "ATTACHED", "DETACHING", "DETACHED", "DISCOVERING", "DISCOVERED", "CLEANING_UP", "CLEANED_UP", "RESTORING_BACKUP", "RESTORING_SNAPSHOT", "RESTORE_FAILED", "DELETED", "DELETING", "PARTIAL_RESTORE", "UPDATING", "REFRESHING"

  - `stateReason` (string)
    Brief reason for the current state of the group

  - `status` (string)
    Current status of the group
    Enum: "OK", "ERROR", "WARNING"

  - `storageSystemInfo` (object)
    Describes a storage system.

  - `storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `storageSystemInfo.name` (string)
    Name of the storage system.
    Example: "alletra9000.domain.net"

  - `storageSystemInfo.productFamily` (string)
    Product Family
    Example: "deviceType1"

  - `storageSystemInfo.resourceUri` (string)
    The URI reference for this resource.

  - `storageSystemInfo.type` (string)
    Type of storage system.

  - `volumeProtectionGroupType` (string)
    The type of the Protection Group. This can be Native for storage system specific constructs and Custom if its just a collection of assets (Volume).
    Enum: "NATIVE", "CUSTOM"

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


