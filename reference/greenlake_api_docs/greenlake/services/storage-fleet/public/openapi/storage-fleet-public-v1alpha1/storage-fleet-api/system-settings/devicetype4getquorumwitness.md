---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4getquorumwitness.md"
scraped_at: "2026-06-07T06:16:17.024155+00:00Z"
---

# Get quorum witness configuration details from HPE Alletra Storage MP B10000 storage system identified by {systemId}

Get quorum witness configuration details from HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness
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
    oData query to filter witness by key.
    Example: "id eq afb4961e47212e5bc88dd35db5be5c83"

  - `sort` (string)
    oData query to sort witness resource by key.
    Example: "id desc"

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
    Id of the replication partner on which quorum witness is configured. Filter,Sort
    Example: "5a5ce66d4814a5e5156de428abb0a589"

  - `items.type` (string, required)
    type
    Example: "quorum-witness"

  - `items.associatedLinks` (array,null)
    Associated Links
    Example: [{"link":"/storage-fleet/v1alpha1/devtype4-storage-systems/SGH000XWEE","type":"systems"}]

  - `items.associatedLinks.resourceUri` (string,null)
    Resource URI

  - `items.associatedLinks.type` (string)
    Resource Name

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

  - `items.generation` (integer,null)
    generation

  - `items.isRemoteArraySupportReplication` (boolean)
    Boolean value to indicate if remote array OS version supports replication
    Example: true

  - `items.name` (string,null)
    Name of replication partner on which quorum witness is configured
    Example: "IPSource"

  - `items.quorumAtfTimeout` (integer,null)
    Automatic Transparent Failover quorum partner failure timeout.
    Example: 30

  - `items.quorumIpAddress` (string,null)
    Quorum IP Address associated with the partner. Set to 'NA' if not available.
    Example: "10.10.10.11"

  - `items.quorumSslPort` (integer,null)
    Quorum SSL port number.
    Example: 8843

  - `items.quorumStatus` (string,null)
    Quorum status of the partner. Possible values - Uninitialized, Initializing,Started, Not-started, Standby, Active, Failsafe, Failover or Restarting. Null if unset.
    Example: "Initializing"

  - `items.quorumStatusQual` (string,null)
    Quorum status qualifier. Set to 'NA' if not available.
    Example: "NA"

  - `items.quorumVersion` (string,null)
    Quorum version.
    Example: "2.0"

  - `items.remoteId` (string,null)
    Id of the remote replication partner on which quorum witness is configured
    Example: "6a5ce66d4814a5e5156de428abb0a580"

  - `items.remoteName` (string,null)
    Name of the remote replication partner on which quorum witness is configured
    Example: "IPTarget"

  - `items.remoteSystemId` (string,null)
    Unique ID or serial number of the remote system.
    Example: "SGH000XWEF"

  - `items.remoteSystemName` (string,null)
    Name of the remote system.
    Example: "System102"

  - `items.resourceUri` (string,null)
    resourceUri for quorum witness object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/SGH000XWEE/quorum-witness/5a5ce66d4814a5e5156de428abb0a589"

  - `items.systemId` (string,null)
    Unique ID or serial number of the system.
    Example: "SGH000XWEE"

  - `items.systemName` (string,null)
    Name of the source system.
    Example: "s1511"

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


