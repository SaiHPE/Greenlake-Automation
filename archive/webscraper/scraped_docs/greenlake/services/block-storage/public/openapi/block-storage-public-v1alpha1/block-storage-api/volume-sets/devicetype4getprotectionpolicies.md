---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4getprotectionpolicies.md"
scraped_at: "2026-06-07T06:14:34.699179+00:00Z"
---

# Get details of protection policies configured on application set identified by {id} created on HPE Alletra Storage MP B10000 identified by {systemId}

Get details of protection policies configured on application set identified by {id} created on HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    ID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `filter` (string)
    Lucene query to filter application-sets by Key.
    Example: "uid eq 2a0df0fe6f7dc7bb16000000000000000000004817"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Protection Policy ID
    Example: "12ab132316dc4b05a4805dba13e495xy"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.associatedBackupDevice` (object,null)
    Contains protection store id and StoreOnce device id used to create backup.

  - `items.associatedBackupDevice.protectionStoreId` (string,null)
    Unique identifier of the protection store used to create backup of the application set.
    Example: "fa43500317062d6f025ec9ca54bab123"

  - `items.associatedBackupDevice.storeOnceId` (string,null)
    Unique identifier of the StoreOnce device used to create backup of the application set.
    Example: "fa43500317062d6f025ec9ca54bab123"

  - `items.associatedPolicy` (object,null)
    Policy created in Data Services Cloud Console that is associated with this application set.

  - `items.associatedPolicy.policyId` (string,null)
    Unique identifier of the policy created in Data Services Cloud Console.
    Example: "fa43500317062d6f025ec9ca54bab123"

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
    customerId
    Example: "string"

  - `items.generation` (integer,null)
    generation

  - `items.policy` (object,null)

  - `items.policy.autoRecover` (boolean)
    If the Remote Copy is stopped as a result of links going down, the Remote Copy group can be automatically restarted after the links come back up.
    Example: true

  - `items.policy.autoSynchronize` (boolean)
    Auto synchronization ensure that remote copy system automatically recovers and synchronizes all volumes in the group after automatic or manual failover scenarios. In addition, this policy allows failover even when remote copy synchronous groups are started and online
    Example: true

  - `items.policy.isProtectionPolicyConfigured` (boolean)
    Boolean value to indicate if protection policy is properly configured on the volume set. If it is set to false, user needs to either delete the policy or fix the policy configuration. All other operations will be blocked in this scenario.
    Example: true

  - `items.policy.noAutomaticSynchronization` (boolean,null)
    Specifies if the no-automatic-synchronization option is enabled in case of Asynchronous/Periodic replication. If this property is true, then no synchronization happens. Not applicable for Synchronous replication.

  - `items.policy.nonZeroRtoConfig` (string,null)
    Non Zero RTO configuration. Supported configuration is Active Sync.
    Example: "ActiveSync"

  - `items.policy.overPeriodAlert` (boolean,null)
    If synchronization of an asynchronous periodic Remote Copy group takes longer to complete than its synchronization period, an alert is generated. This property is not valid and hence cannot be enabled in case of synchronous replication.
    Example: true

  - `items.policy.remote` (object)
    Replication partner details

  - `items.policy.rpoSecs` (integer,null)
    Specifies recovery point objective in seconds for Asynchronous periodic protection. This is not applicable for Synchronous replication, and in case of Asynchronous replication, rpoSecs will not contain any value if the no-automatic-synchronization option is enabled.
    Example: 600

  - `items.policy.secondaryRemote` (object,null)
    Second replication partner details from Synchronous Long Distance configuration and for 3DC Peer Persistence mode

  - `items.policy.zeroRtoConfig` (string,null)
    Zero RTO configuration. Supported config is Active Peer Persistence. Classic Peer Persistence is not supported for HPE Alletra Storage MP.  This property is nil in case of Plain Synchronous Replication, which is of non-zero-RTO type.
    Example: "APP"

  - `items.protectionPolicyType` (string)
    Protection policy type: schedule, sync or async
    Example: "sync"

  - `items.schedules` (object,null)
    Schedules on application set

  - `items.schedules.total` (integer)
    Number of schedules on application set
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


