---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/fix"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4fixprotectionpolicy.md"
scraped_at: "2026-06-07T06:14:35.342871+00:00Z"
---

# Fix protection policy configuration on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

Remedies issues caused in protection policy configuration on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/fix
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    ID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `protectionPolicyType` (string, required)
    Specifies Protection policy type. Synchronous replication/protection policy provides protection from array or site failures with zero RPO. Using this policy, you can also configure zero RTO policy like Active Peer Persistence. Asynchronous replication/protection policy provides protection from array or site failure with the user defined RPO.  Schedule snapshot policy takes snapshots of the member volumes of the protected volume set at periodic intervals defined by the user. You can setup the local snapshot schedule and also setup the co-ordinated synchronized snapshot schedule on the protected volume set configured with synchronous or asynchronous replication policy. You can do this by attaching a scheduled snapshot policy on the volume set having already a synchronous or asynchronous protecting policy.
    Enum: "schedule", "sync", "async"

  - `policy` (object)
    Protection policy details

  - `policy.remote` (object, required)
    Replication partner details for remote protection

  - `policy.remote.partnerName` (string, required)
    Remote partner name
    Example: "IP_target"

  - `policy.remote.partnerId` (string, required)
    Remote partner ID
    Example: "afb4961e47212e5bc88dd35db5be5c83"

  - `policy.remote.replicationType` (string, required)
    Replication type. Synchronous replication/protection policy provides protection from array or site failures with zero RPO. Using this policy, you can also configure zero RTO policy like Active Peer Persistence. Periodic replication (Asynchronous protection policy) provides protection from array or site failure with the user defined RPO.
    Enum: "sync", "periodic"

  - `policy.remote.replicationPartnerSnapshotCpg` (string,null)
    Replication Partner Snapshot CPG. Applicable only if the target system is Primera or Alletra 9K. Currently, not supported due to OS limitation. This field will be supported in future release.
    Example: "SSD_r6"

  - `policy.remote.replicationPartnerUserCpg` (string,null)
    User CPG in which the target volumes would get created in the replication partner system.
    Example: "SSD_r6"

  - `policy.autoRecover` (boolean)
    Specifies that if the protected volume set is stopped as a result of the Remote Copy links going down, the protected volume set is restarted automatically after the links come back up.  If this policy is enabled for a volume set while the volume set is stopped after link failures, it will only be started when the links come up for the failed target.  If the links are already up at the time the policy is set, then the protected volume set will not be restarted at that time.

  - `policy.autoSynchronize` (boolean)
    This property ensures that the Remote Copy system automatically recovers and synchronizes all volumes in the protected volume set after a system failover, for either automatic or manual failover scenarios.  Synchronization occurs after system recovery completes and the Remote Copy links recover. This policy also allows the failover command to be used when synchronous volume sets are started and are online.  It is no longer necessary to stop the synchronous volume sets before initiating a failover command to the secondary system.

  - `policy.noAutomaticSynchronization` (boolean,null)
    Enabling this option results in no synchronization happening between the source and target application sets. This is applicable only in case of periodic replication, and is disabled by default.

  - `policy.overPeriodAlert` (boolean)
    If synchronization of an asynchronous periodic protection takes longer to complete than its synchronization period, an alert is generated. This property is not valid and hence cannot be enabled in case of synchronous replication.

  - `policy.rpoSecs` (integer)
    Specifies recovery point objective in seconds for asynchronous periodic protection. Range: 30 - 63072000, and should be an even number. For Synchronous replication, the value defaults to zero even if it is specified. For Asynchronous replication, if rpoSecs is not specified then it would be considered under the no-automatic-synchronization option, and no synchronization happens.
    Example: 600

  - `policy.secondaryRemote` (object)
    Replication partner details for Async partner in Synchronous Long Distance mode and for 3DC Peer Persistence mode

  - `policy.secondaryRemote.replicationType` (string, required)
    Replication type. Supported type is periodic only. Periodic replication (Asynchronous protection policy) provides protection from array or site failure with the user defined RPO.
    Enum: "periodic"

  - `policy.zeroRtoConfig` (string)
    Zero RTO configuration to be used. Supported config is Active Peer Persistence. Classic Peer Persistence is not supported by HPE Alletra Storage MP B10000. If this is not specified, the configuration will be Plain Synchronous Configuration.
    Enum: "APP"

  - `schedules` (array)

  - `schedules.name` (string, required)
    Name of the Schedule
    Example: "Every_1_hour_on_sunday_monday"

  - `schedules.period` (integer, required)
    Time interval for snapshots. Possible values:
  - hours: 1,2,3,4,6,8,12
  - minutes: 15,20,30
  - days & months: 1
    Example: 1

  - `schedules.periodUnit` (string, required)
    Unit of time for the interval specified in period.
    Enum: "minutes", "hours", "days", "months"

  - `schedules.expireSecs` (integer, required)
    Number of seconds the snapshot has to be retained.
    Example: 3600

  - `schedules.isRemote` (boolean, required)
    Specifies that this schedule is remote protection schedule
    Example: true

  - `schedules.atTime` (integer)
    Time of the day when snapshot should be taken. Possible values: 0-23 If more than one snapshots in a day then untilTime specifies until what time snapshots should be taken.
    Example: 2

  - `schedules.dayOfMonth` (integer)
    Day of month on which snapshot has to be taken for Monthly schedule. Possible values: 1-28
    Example: 10

  - `schedules.days` (string)
    Days on which snapshots should be taken. comma separated. Possible values: sunday,monday,tuesday,wednesday,thursday,friday,saturday
    Example: "sunday,monday"

  - `schedules.readOnly` (boolean,null)
    Specifies that the snapshots created by schedule are read-only. Defaults to false in case of local schedules. Defaults to true in case of remote schedules. When local schedules are converted to remote schedules, ReadOnly mode will be considered by default.
    Example: true

  - `schedules.retainSecs` (integer,null)
    Specifies the amount of time in seconds, relative to the current time, that the snapshot will be retained. It is a positive integer value and in the range of 1 hour - 1825 days. If both expiration time and retention time are specified, then the retention time cannot be longer than the expiration time.
    Example: 3600

  - `schedules.untilTime` (integer)
    Time of the day to stop taking snapshots. Must be an incremental value by the factor specified in Period, starting from atTime. Applicable only when more than one snapshots should be taken in a day.
    Example: 7

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


