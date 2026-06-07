---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4getreplicationpartners.md"
scraped_at: "2026-06-07T06:16:04.097540+00:00Z"
---

# Get details of replication partners on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Get details of replication partners on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners
Version: 1.2.0
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
    oData query to filter replication partners by key.
    Example: "systemId eq 7CE751P312"

  - `sort` (string)
    oData query to sort nodes resource by key.
    Example: "name desc"

  - `include-indirect-partners` (boolean)
    Include indirect partners. Indirect partners are excluded by default. This parameter cannot be used with other query parameters.
    Example: true

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
    Unique id of the replication partner. Filter
    Example: "5a5ce66d4814a5e5156de428abb0a589"

  - `items.type` (string, required)
    type
    Example: "replication-partner"

  - `items.name` (string)
    Name of the replication partner. Filter, Sort
    Example: "RCPartner12"

  - `items.replicationPartnerType` (string)
    Link protocol type. Filter, Sort
    Example: "FC"

  - `items.status` (string,null)
    Status of the partner. Possible values - New, Ready, Unsupported, Failing, Failed or Disabled. Filter, Sort
    Example: "Ready"

  - `items.associatedLinks` (array,null)
    Associated Links
    Example: [{"link":"/storage-fleet/v1alpha1/devtype4-storage-systems/SGH000XWEE","type":"systems"}]

  - `items.associatedLinks.resourceUri` (string,null)
    Resource URI

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.bufferSizeB` (integer,null)
    Socket buffer size to use.
    Example: 1024

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
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.displayName` (string,null)
    Replication partner displayname.
    Example: "RCPartner12"

  - `items.domain` (string,null)
    Domain that the resource belongs to.
    Example: "domain1"

  - `items.flags` (integer,null)
    Partner flags.
    Example: 1

  - `items.generation` (integer,null)
    generation

  - `items.health` (integer,null)
    Partner health status.
    Example: 1

  - `items.isRemoteArraySupportReplication` (boolean)
    Boolean value to indicate if remote array OS version supports replication
    Example: true

  - `items.minPeriodSecs` (integer,null)
    Minimum supported Async Periodic period for the partner. The field is omitted if unset or unavailable for the version of partner firmware.
    Example: 300

  - `items.nodeWwn` (string,null)
    Partner options, with FC partners this includes the partner system's node WWN. Omitted if unpopulated.
    Example: "2FF70002AC020DA1"

  - `items.numSockets` (integer,null)
    Number of sockets to use.
    Example: 2

  - `items.policies` (object,null)
    Any policies that are set for the partner.

  - `items.policies.mirrorConfig` (boolean,null)
    Duplication of all configurations involving the specified partner.
    Example: true

  - `items.quorumAtfTimeout` (integer,null)
    Automatic Transparent Failover quorum partner failure timeout.

  - `items.quorumIpAddress` (string,null)
    Quorum IP Address associated with the partner. Set to 'NA' if not available.
    Example: "10.10.10.11"

  - `items.quorumSslPort` (integer,null)
    Quorum SSL port number.

  - `items.quorumStatus` (string,null)
    Quorum status of the partner. Possible values - Uninitialized, Initializing, Standby, Active, Failsafe, Failover or Restarting. Null if unset.
    Example: "Initializing"

  - `items.quorumStatusQual` (string,null)
    Quorum status qualifier. Set to 'NA' if not available.
    Example: "NA"

  - `items.quorumVersion` (string,null)
    Quorum version.
    Example: "2.0"

  - `items.remoteId` (string,null)
    Unique id of the remote replication partner.
    Example: "6a5ce66d4814a5e5156de428abb0a580"

  - `items.remoteName` (string,null)
    Name of the remote replication partner.
    Example: "FC-02"

  - `items.remoteReplicationId` (integer,null)
    Replication ID of the remote replication partner.
    Example: 12

  - `items.remoteSystemId` (string,null)
    Unique ID or serial number of the remote system.
    Example: "SGH000XWEF"

  - `items.remoteSystemName` (string,null)
    Name of the remote system.
    Example: "System102"

  - `items.replicationId` (integer,null)
    Replication ID of the partner.
    Example: 1

  - `items.replicationSystemId` (integer,null)
    ID of the remote system.
    Example: 1

  - `items.resourceUri` (string,null)
    resourceUri for detailed replication partner object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/SGH000XWEE/system-settings/replication-partners/5a5ce66d4814a5e5156de428abb0a589"

  - `items.state` (string,null)
    State of the replication partner.
    Example: "UNKNOWN"

  - `items.systemId` (string,null)
    Unique ID or serial number of the system.
    Example: "SGH000XWEE"

  - `items.systemName` (string,null)
    Name of the system.
    Example: "System101"

  - `items.systemWwn` (string,null)
    WWN of the system.
    Example: "2FF70002AC020CEF"

  - `items.version` (integer,null)
    Partner version.
    Example: 41

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
