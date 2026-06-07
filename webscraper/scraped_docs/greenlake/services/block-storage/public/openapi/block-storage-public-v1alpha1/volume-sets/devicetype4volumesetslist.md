---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetslist.md"
scraped_at: "2026-06-07T06:14:25.277612+00:00Z"
---

# Get all applicationset details for HPE Alletra Storage MP B10000

Get all applicationset details for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    Lucene query to filter application-sets by Key.
    Example: "uid eq 2a0df0fe6f7dc7bb16000000000000000000004817"

  - `sort` (string)
    Lucene query to sort application-sets by Key.
    Example: "name desc"

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    uid of the applicationset Filter
    Example: "4c74ec5c-ecec-4483-9506-3fb5dc45b5d0"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.appSetBusinessUnit` (string,null)
    Appset BusinessUnit
    Example: "cssl"

  - `items.appSetComments` (string,null)
    Application set comments
    Example: "app set comments"

  - `items.appSetExcludeAiQoS` (string,null)
    Exclusion from AI QoS
    Example: "no"

  - `items.appSetId` (integer,null)
    ID
    Example: 5

  - `items.appSetImportance` (string,null)
    Importance Level
    Example: "MEDIUM"

  - `items.appSetName` (string,null)
    Application set name. Filter
    Example: "KA_VEGA_APPSET1_186"

  - `items.appSetType` (string,null)
    Name of the resource. Filter
    Example: "Oracle Database"

  - `items.appSetTypeEnum` (string,null)
    Enum value of type of the application set
    Example: "ORACLE_DATA"

  - `items.associatedLinks` (array)
    Associated Links Details
    Example: [{"resourceUri":"/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC01F0FF","type":"systems"},{"resourceUri":"/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC01F0FF/volumes","type":"volumes"}]

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.comment` (string,null)
    Comments if any
    Example: "Comments"

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

  - `items.displayName` (string,null)
    Display Name
    Example: "Application Set KA_VEGA_APPSET1_186 "

  - `items.domain` (string,null)
    Domain name. Filter
    Example: "Domain"

  - `items.drState` (string,null)
    Specifies replication disaster recovery state of a protected volume set.  Possible values: Normal, Failover, Recover, Unknown The disaster recovery state is Unknown for any intermediate state.
    Example: "Normal"

  - `items.exportStatus` (string,null)
    Export status
    Example: "PARTIALLY_EXPORTED"

  - `items.generation` (integer,null)
    generation. Filter, Sort

  - `items.initiators` (array,null)
    Initiator details

  - `items.initiators.deviceDiscoveredName` (string,null)
    Host/HostGroup name on device.
    Example: "TEST11"

  - `items.initiators.id` (string)
    Resource id
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.initiators.resourceUri` (string,null)
    Resource URI
    Example: "/v1/host-initiators/6848ef683c27403e96caa51816ddc72c"

  - `items.isPrimary` (boolean,null)
    States if the Application set is Primary or not
    Example: true

  - `items.kvPairsPresent` (boolean)
    Represents KV pairs present or not
    Example: true

  - `items.members` (array,null)
    Volume Names. Filter, Sort
    Example: ["vol1","vol2"]

  - `items.name` (string,null)
    Name of the resource. Filter, Sort
    Example: "volset_name"

  - `items.nonZeroRtoConfig` (string,null)
    Non-Zero RTO configuration. Supported config is Active-Sync
    Example: "ActiveSync"

  - `items.ransomware` (boolean,null)
    Indicates Whether ransomware detection has been enabled on this volume set (Applicable for the HPE Alletra Storage MP B10000 systems with version 10.5.0 OS and later).

  - `items.remoteRecoveryPoint` (object,null)
    Shows last data sync time

  - `items.remoteRecoveryPoint.ms` (integer,null)
    Epoch time in milliseconds
    Example: 1591601529000

  - `items.remoteRecoveryPoint.tz` (string,null)
    Time zone name
    Example: "Local"

  - `items.replicationPartner` (array,null)
    Shows the Replication Partner Systems and Replication Partners
    Example: [{"partnerSystem":"cs2-C630-2939-141","replicationPartner":"cs2-C630-2939_s1511"},{"partnerSystem":"s2940_208","replicationPartner":"s2940_1"}]

  - `items.replicationPartner.partnerSystem` (string,null)
    Replication Partner System

  - `items.replicationPartner.replicationPartner` (string,null)
    Replication Partner

  - `items.replicationState` (string,null)
    Shows the replication state of the application set. This is not applicable in case of a 3DC/SLD configuration.
    Example: "Started"

  - `items.replicationTraffic` (string,null)
    Shows the direction of flow of data. This is not applicable in case of a 3DC/SLD configuration.
    Example: "Sending"

  - `items.replicationType` (string,null)
    Mode of replication. Can be sync or periodic. This is not applicable in case of a 3DC/SLD configuration.
    Example: "periodic"

  - `items.role` (string,null)
    Specifies remote copy role for a protected volume set.  Possible values: Primary, Secondary, Primary-Rev, Secondary-Rev, Unknown The role status is Unknown for any intermediate remote copy role of a protected volume set.
    Example: "Primary"

  - `items.shortName` (string,null)
    Short name of the application set
    Example: "VegaApplications~886"

  - `items.sizeMiB` (number,null)
    Size in MB of appset
    Example: 153600

  - `items.snapSetParentId` (integer,null)
    ParentId of the snapSet. Filter
    Example: 5

  - `items.snapSetParentName` (string,null)
    Parent name of the snapSet. Filter
    Example: "HPE"

  - `items.systemId` (string,null)
    SystemUid/serialNumber of the array. Filter, Sort
    Example: "7CE751P312"

  - `items.vvSetType` (string,null)
    Type of the volume-set. Filter
    Example: "VVSET"

  - `items.zeroRtoConfig` (string,null)
    Zero RTO configuration. Supported config is Active Peer Persistence. Classic Peer Persistence is not supported for HPE Alletra Storage MP B10000.
    Example: "PP"

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
