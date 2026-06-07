---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/remote-protection/actions"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4actiononvolumesets.md"
scraped_at: "2026-06-07T06:14:26.777120+00:00Z"
---

# Actions on volume set identified by {id} and {systemId} from HPE Alletra Storage MP B10000

Actions on volume set identified by {id} and {systemId} from HPE Alletra Storage MP B10000

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/remote-protection/actions
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    ID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Request fields (application/json):

  - `action` (string)
    Actions on the volume set where remote protection is enabled.
    Enum: "FAILOVER", "SYNC", "OVERRIDE", "START", "STOP", "RECOVER", "RESTORE", "SWITCHOVER", "REVERSE"

  - `parameters` (object)

  - `parameters.failoverActionParams` (object)

  - `parameters.failoverActionParams.forcePpFailover` (boolean,null)
    Specifies that the Peer Persistence failover operation is forced overriding data inconsistency warnings. All I/O to the existing primary volumes should be quiesced when using this option.
    Example: true

  - `parameters.failoverActionParams.noSnapshot` (boolean,null)
    Specifies that snapshots are not taken of application sets that are switched from secondary to primary. Additionally, existing snapshots are deleted if application sets are switched from primary to secondary. The use of this option may result in a full synchronization of the secondary volumes.
    Example: true

  - `parameters.failoverActionParams.skipPromote` (boolean,null)
    Specifies that the synchronized snapshots of the protected volume set that are switched from primary to secondary should not be promoted to the base volume. The incorrect use of this option can lead to the primary and secondary volumes not being consistent.
    Example: true

  - `parameters.failoverActionParams.targetName` (string,null)
    Replication partner name on which to failover.
    Example: "s1511"

  - `parameters.overrideActionParams` (object)

  - `parameters.overrideActionParams.targetName` (string,null)
    Replication partner name (target name) on which the override action is to be performed.
    Example: "s1511"

  - `parameters.recoverActionParams` (object)

  - `parameters.recoverActionParams.skipStart` (boolean,null)
    Specifies that protection is not started after recover action is completed.
    Example: true

  - `parameters.recoverActionParams.skipSync` (boolean,null)
    Specifies that protection is not synced after recover action is completed.
    Example: true

  - `parameters.recoverActionParams.targetName` (string,null)
    Replication partner name (target name) on which the recover action to be performed.
    Example: "s1511"

  - `parameters.restoreActionParams` (object)

  - `parameters.restoreActionParams.skipStart` (boolean,null)
    Specifies that protection is not started after restore action is completed.
    Example: true

  - `parameters.restoreActionParams.skipSync` (boolean,null)
    Specifies that protection is not synced after restore action is completed.
    Example: true

  - `parameters.restoreActionParams.targetName` (string,null)
    Replication partner name (target name) on which the restore action to be performed.
    Example: "s1511"

  - `parameters.reverseActionParams` (object)

  - `parameters.reverseActionParams.current` (boolean,null)
    Changes both the role and the direction of data flow between the protected volume sets. For example, if the roles of the protected volume sets are "primary" and "secondary", issuing the -current option to the reverse operation will result in the roles of the protected volume set becoming "secondary-rev" and "primary-rev" respectively, and the direction data flows between the groups is reversed. Since the -current option actually reverses the direction of data replication, it requires the protected volume set be stopped.This option must be used with care to ensure the protected volume sets do not end up in a non-deterministic state (like "secondary", "secondary-rev" for example) and to ensure data loss does not occur by inadvertently changing the direction of data flow and resyncing old data on top of newer data.
    Example: true

  - `parameters.reverseActionParams.localGroupDirection` (boolean,null)
    This option only applies to the reverse operation, and only when the -natural or -current options to the reverse operation are specified. Specifying this option with the reverse operation and an associated -natural or -current option will only affect the system where the reverse command is issued, and will not be mirrored to any other arrays in the Remote Copy configuration.
    Example: true

  - `parameters.reverseActionParams.natural` (boolean,null)
    Changes the role of the protected volume sets but not the direction of data flow between the groups on the arrays. For example, if the role of the protected volume sets are "primary" and "secondary", issuing the -natural option with the reverse operation will result in the role of the groups becoming "primary-rev" and "secondary-rev" respectively. The direction of data flow between the protected volume sets is not affected, only the roles. Since the -natural option does not change the direction of data flow between the protected volume sets, it does not require the protected volume sets be stopped. This option must be used with care to ensure the protected volume sets do not end up in a non-deterministic state (like "secondary", "secondary-rev" for example) and to ensure data loss does not occur by inadvertently changing the direction of data flow and resyncing old data on top of newer data.
    Example: true

  - `parameters.reverseActionParams.noSnapshot` (boolean,null)
    Specifies that snapshots are not taken of the protected volume sets that are switched from secondary to primary. Additionally, existing snapshots are deleted if the protected volume sets are switched from primary to secondary. The use of this option may result in a full synchronization of the secondary volumes.
    Example: true

  - `parameters.reverseActionParams.stopGroups` (boolean,null)
    Specifies that the system stops the replication before performing the reverse action.
    Example: true

  - `parameters.reverseActionParams.targetName` (string,null)
    Replication partner name (target name) on which the reverse action to be performed.
    Example: "s1511"

  - `parameters.startActionParams` (object)

  - `parameters.startActionParams.targetName` (string,null)
    Target name on which the protection has to be started.
    Example: "s1511"

  - `parameters.stopActionParams` (object)

  - `parameters.stopActionParams.targetName` (string,null)
    Target name on which the protection has to be stopped.
    Example: "s1511"

  - `parameters.switchoverActionParams` (object)

  - `parameters.switchoverActionParams.targetName` (string,null)
    Replication partner name (target name) on which the switchover action is to be performed.
    Example: "s1511"

  - `parameters.syncActionParams` (object)

  - `parameters.syncActionParams.forceFullSync` (boolean,null)
    Forces full synchronization, even if volumes are already synchronized. This option is only applicable for volume sets with synchronous replication.

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

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

## Response default fields (application/json):

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


