---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getreplicationpartnersbyappsetid.md"
scraped_at: "2026-06-07T06:14:25.542302+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 replication partners identified by {systemId} and {appsetId}

Get details of HPE Alletra Storage MP B10000 replication partners identified by {systemId} and {appsetId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `appsetId` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique Identifier of the replication partner.
    Example: "0af26e4430548dd5c37bea1757107caf"

  - `items.type` (string, required)
    type
    Example: "replication-partner"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    customer ID
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.displayName` (string,null)
    Replication partner display name.
    Example: "RCPartner1"

  - `items.domain` (string,null)
    Domain that the resource belongs to.
    Example: "Domain1"

  - `items.drState` (string,null)
    Specifies replication disaster recovery state of a protected volume set.  Possible values: Normal, Failover, Recover, Unknown The disaster recovery state is Unknown for any intermediate state.
    Example: "Normal"

  - `items.generation` (integer,null)
    generation

  - `items.groupId` (string,null)
    Unique id of replication partner remote group
    Example: "0af26e4430948dd5c37bea1757107caf"

  - `items.groupLastSyncTime` (object,null)
    Last synchronization time in milliseconds since epoch.

  - `items.groupLastSyncTime.ms` (integer,null)
    Epoch time in milliseconds.
    Example: 1552301131100

  - `items.groupLastSyncTime.tz` (string,null)
    Time zone name
    Example: "UTC"

  - `items.groupName` (string,null)
    Replication partner remote group name.
    Example: "testGroup"

  - `items.groupObjectId` (integer,null)
    Replication partner group ID.
    Example: 11

  - `items.isProtectionPolicyConfigured` (boolean)
    Boolean value to indicate if protection policy is properly configured on the volume set. If it is set to false, user needs to either delete the policy or fix the policy configuration. All other operations will be blocked in this scenario.
    Example: true

  - `items.isRemoteArraySupportReplication` (boolean)
    Boolean value to indicate if remote array OS version supports replication
    Example: true

  - `items.isSourceArraySupportReplication` (boolean)
    Boolean value to indicate if source array OS version supports replication
    Example: true

  - `items.mode` (string,null)
    Replication partner group mode.
    Example: "Periodic"

  - `items.policies` (object,null)
    The policy assigned to the replication partner remote group.

  - `items.policies.activeActive` (boolean,null)
    Specifies active active policy of the group.
    Example: true

  - `items.policies.autoFailover` (boolean,null)
    Automatic failover on a group.
    Example: true

  - `items.policies.autoRecover` (boolean,null)
    If the group is stopped as a result of links going down, the group can be automatically restarted after the links come back up.
    Example: true

  - `items.policies.autoSynchronize` (boolean,null)
    Specifies auto synchronization of the group.
    Example: true

  - `items.policies.multiTargetPeerPersistence` (boolean,null)
    Specifies that the group is participating in a Multi-target Peer Persistence configuration. The group must have two targets, one of which must be synchronous.The synchronous group target also requires pathManagement and auto Fail over policy settings.
    Example: true

  - `items.policies.overPeriodAlert` (boolean,null)
    If synchronization of an asynchronous periodic group takes longer to complete than its synchronization period, an alert is generated.
    Example: true

  - `items.policies.pathManagement` (boolean,null)
    Path management on a group.
    Example: true

  - `items.protectionType` (string,null)
    Type of protection
    Example: "Remote"

  - `items.remoteProductFamily` (string,null)
    Target volume set product family where remote protection is enabled
    Example: "deviceType4"

  - `items.remoteRole` (string,null)
    Specifies remote copy role for a restore point of a protected volume set. In case of synchronous and asynchronous protection polices, restore point is the volume set on the replication partner/target array. Possible values: Primary, Secondary, Primary-Rev, Secondary-Rev, Unknown The role status is Unknown for any intermediate remote copy role for a restore point of a protected volume set.
    Example: "Primary"

  - `items.remoteSystemId` (string,null)
    Target volume set system ID where remote protection is enabled
    Example: "systemID"

  - `items.remoteUsrCpg` (string,null)
    Name for which the user space is allocated on the remote target.
    Example: "FC_r1"

  - `items.remoteVolumeSetId` (string,null)
    Target volume set ID where remote protection is enabled
    Example: "volumeSetID"

  - `items.remoteVolumeSetName` (string,null)
    Target volume set name where remote protection is enabled
    Example: "volumeSet2"

  - `items.replicationTraffic` (string,null)
    Specifies the direction of data replication for the current target.
    Example: "Sending"

  - `items.resourceUri` (string)
    resourceUri for replication partner list where volume set is remote protected
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/applicationsets/9c3c4f29a82fd8d632ff379116fa0b8f/replication-partners/0af26e4430548dd5c37bea1757107caf"

  - `items.role` (string,null)
    Specifies remote copy role for a protected volume set.  Possible values: Primary, Secondary, Primary-Rev, Secondary-Rev, Unknown The role status is Unknown for any intermediate remote copy role of a protected volume set.
    Example: "Primary"

  - `items.roleReversed` (boolean,null)
    Remote group role switched due to a fail over.
    Example: true

  - `items.snapFrequencySecs` (integer,null)
    Specifies the interval in seconds at which remote group takes coordinated snapshots. This field applies only to Async mode: it is set to -1 otherwise.
    Example: -1

  - `items.state` (string,null)
    Status of the Remote group for the replication partner. Can be New, Starting, Started, Restart, Stopped, Backup, Failsafe or Logging. Null if unset.
    Example: "Started"

  - `items.syncPeriod` (integer)
    Time period in seconds for automatic resynchronization. The value must be at least five minutes and not more than one year. Defaults to 0.

  - `items.systemId` (string,null)
    Unique ID or serial number of the system.
    Example: "7CE816P0SR"

  - `items.systemName` (string,null)
    Name of the system.
    Example: "sp2bh"

  - `items.systemWwn` (string,null)
    WWN of the system.
    Example: "2FF70002AC020DA1"

  - `items.targetName` (string,null)
    Target to which the volume group is mirrored. This is the same as replication partner.
    Example: "sp2bh"

  - `items.volumeCount` (integer,null)
    Number of volumes in the group for a replication partner.
    Example: 1

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

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


## Response 304 fields
