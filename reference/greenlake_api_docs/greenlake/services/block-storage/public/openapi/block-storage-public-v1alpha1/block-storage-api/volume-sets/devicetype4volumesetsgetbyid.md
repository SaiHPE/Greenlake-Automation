---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4volumesetsgetbyid.md"
scraped_at: "2026-06-07T06:14:34.751922+00:00Z"
---

# Get applicationset details for an applicationset identified by appsetUid

Get applicationset details for an applicationset identified by appsetUid

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    uid of the applicationset
    Example: "4c74ec5c-ecec-4483-9506-3fb5dc45b5d0"

  - `type` (string, required)
    type
    Example: "string"

  - `appSetBusinessUnit` (string,null)
    Appset BusinessUnit
    Example: "cssl"

  - `appSetComments` (string,null)
    Application set comments
    Example: "app set comments"

  - `appSetExcludeAiQoS` (string,null)
    Exclusion from AI QoS
    Example: "no"

  - `appSetId` (integer,null)
    ID
    Example: 5

  - `appSetImportance` (string,null)
    Importance Level
    Example: "NORMAL"

  - `appSetName` (string,null)
    Application set name
    Example: "KA_VEGA_APPSET1_186"

  - `appSetQosConfig` (object,null)

  - `appSetQosConfig.id` (string, required)
    id of the QoS Configuration
    Example: "59978"

  - `appSetQosConfig.bandwidthMaxLimit` (number,null)
    Bandwidth Maximum Limit in KB/s
    Example: 500

  - `appSetQosConfig.bwGuaranteeTb` (number,null)
    Bandwidth Guarantee Limit per Tb in KB/s
    Example: 500

  - `appSetQosConfig.bwLimitTb` (number,null)
    Bandwidth Maximum Limit per Tb in KB/s
    Example: 500

  - `appSetQosConfig.displayname` (string,null)
    QoS Config Display name

  - `appSetQosConfig.domain` (string,null)
    Domain Name

  - `appSetQosConfig.enable` (boolean)
    Enable of QoS Configuration
    Example: true

  - `appSetQosConfig.enableSrAlert` (boolean)
    Sets the SR alert with the criterion name as the vvset name based on the max limits being set on the QoS parameters. If provided true, the SR alert criterion will be created or updated based on updated parameters. If provided false, the SR Alert criterion will be deleted if present. If enableSrAlert is not specified and the SR Alert criterion is already present for the volume set, the SR Alert criterion will be retained based on the updated QoS parameters.
    Example: true

  - `appSetQosConfig.generation` (integer,null)
    generation
    Example: 1666788678

  - `appSetQosConfig.ioGuaranteeTb` (number,null)
    iops Maximum Guarantee per Tb
    Example: 500

  - `appSetQosConfig.ioLimitTb` (number,null)
    iops Maximum Limit per Tb
    Example: 500

  - `appSetQosConfig.iopsMaxLimit` (number,null)
    iops Maxmium Limit
    Example: 500

  - `appSetQosConfig.lastModifiedEpoch` (number,null)
    last modified Epoch
    Example: 1666788678

  - `appSetQosConfig.perTb` (boolean)
    Enable of perTb QoS Configuration (Applicable for storage systems with OS versions that are 10.4.0 or higher but below 10.5.0)
    Example: true

  - `appSetQosConfig.systemUid` (string)
    System Id
    Example: "756XNSKA"

  - `appSetQosConfig.systemWwn` (string)
    System WWN
    Example: "2FWWN2004134"

  - `appSetQosConfig.targetName` (string)
    Target Name of the QoS Config
    Example: "volumeset"

  - `appSetQosConfig.targetType` (string)
    Target Type of the QoS Config
    Example: "QOS_TGT_APPSET"

  - `appSetQosConfig.uid` (string)
    UID of the QoS Config resource
    Example: "12335546bgbgnbgnaq12"

  - `appSetQosConfig.volumes` (array)
    List of volumes
    Example: ["vol1","vol2"]

  - `appSetType` (string,null)
    Type of the application set
    Example: "Oracle Database"

  - `appSetTypeEnum` (string,null)
    Enum value of type of the application set
    Example: "ORACLE_DATA"

  - `associatedLinks` (array)
    Associated Links Details
    Example: [{"resourceUri":"/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC01F0FF","type":"systems"},{"resourceUri":"/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC01F0FF/volumes","type":"volumes"}]

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `comment` (string,null)
    Comments if any
    Example: "Comments"

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `displayName` (string,null)
    Display Name
    Example: "Application Set KA_VEGA_APPSET1_186 "

  - `domain` (string,null)
    Domain name
    Example: "Domain"

  - `drState` (string,null)
    Specifies replication disaster recovery state of a protected volume set.  Possible values: Normal, Failover, Recover, Unknown The disaster recovery state is Unknown for any intermediate state.
    Example: "Normal"

  - `exportStatus` (string,null)
    Export status
    Example: "PARTIALLY_EXPORTED"

  - `initiators` (array,null)
    Initiator details

  - `initiators.deviceDiscoveredName` (string,null)
    Host/HostGroup name on device.
    Example: "TEST11"

  - `initiators.id` (string)
    Resource id
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `initiators.resourceUri` (string,null)
    Resource URI
    Example: "/v1/host-initiators/6848ef683c27403e96caa51816ddc72c"

  - `isPrimary` (boolean,null)
    States if the Application set is Primary or not
    Example: true

  - `kvPairsPresent` (boolean)
    Represents KV pairs present or not
    Example: true

  - `members` (array,null)
    Volume Names
    Example: ["vol1","vol2"]

  - `name` (string,null)
    Name of the application set
    Example: "KA_VEGA_APPSET2_186"

  - `nonZeroRtoConfig` (string,null)
    Non-Zero RTO configuration. Supported config is Active-Sync
    Example: "ActiveSync"

  - `ransomware` (boolean,null)
    Indicates Whether ransomware detection has been enabled on this volume set (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and later).

  - `remoteRecoveryPoint` (object,null)
    Shows last data sync time

  - `remoteRecoveryPoint.ms` (integer,null)
    Epoch time in milliseconds
    Example: 1591601529000

  - `remoteRecoveryPoint.tz` (string,null)
    Time zone name
    Example: "Local"

  - `replicationPartner` (array,null)
    Shows the Replication Partner Systems and Replication Partners
    Example: [{"partnerSystem":"cs2-C630-2939-141","replicationPartner":"cs2-C630-2939_s1511"},{"partnerSystem":"s2940_208","replicationPartner":"s2940_1"}]

  - `replicationPartner.partnerSystem` (string,null)
    Replication Partner System

  - `replicationPartner.replicationPartner` (string,null)
    Replication Partner

  - `replicationState` (string,null)
    Shows the replication state of the application set. This is not applicable in case of a 3DC/SLD configuration.
    Example: "Started"

  - `replicationTraffic` (string,null)
    Shows the direction of flow of data. This is not applicable in case of a 3DC/SLD configuration.
    Example: "Sending"

  - `replicationType` (string,null)
    Mode of replication. Can be sync or periodic. This is not applicable in case of a 3DC/SLD configuration.
    Example: "periodic"

  - `role` (string,null)
    Specifies remote copy role for a protected volume set.  Possible values: Primary, Secondary, Primary-Rev, Secondary-Rev, Unknown The role status is Unknown for any intermediate remote copy role of a protected volume set.
    Example: "Primary"

  - `serialNumber` (string,null)
    Serial number.
    Example: "7CE738P06J"

  - `shortName` (string,null)
    Short name of the application set
    Example: "VegaApplications~886"

  - `sizeMiB` (number,null)
    Size in MB of appset
    Example: 153600

  - `snapSetParentId` (integer,null)
    ParentId of the snapSet
    Example: 5

  - `snapSetParentName` (string,null)
    Parent name of the snapSet
    Example: "HPE"

  - `systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `vvSetType` (string,null)
    Type of the volume-set
    Example: "VVSET"

  - `zeroRtoConfig` (string,null)
    Zero RTO configuration. Supported config is Active Peer Persistence. Classic Peer Persistence is not supported for HPE Alletra Storage MP B10000.
    Example: "PP"

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
