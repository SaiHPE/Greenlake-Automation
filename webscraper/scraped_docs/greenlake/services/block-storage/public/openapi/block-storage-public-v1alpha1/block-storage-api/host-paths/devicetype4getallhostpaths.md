---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-paths/devicetype4getallhostpaths.md"
scraped_at: "2026-06-07T06:14:32.354760+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Host Paths

Get details of HPE Alletra Storage MP B10000 Host Paths

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths
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
    Lucene query to filter host path by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004817"

  - `sort` (string)
    oData query to sort host path resource by Key.
    Example: "HostSpeed desc"

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
    HostPath Resource UID Filter
    Example: "1223f5s"

  - `items.type` (string, required)
    type

  - `items.address` (string,null)
    WWN Address of the Host Path Filter
    Example: "810009440c9ce5824"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the host-path resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `items.domain` (string,null)
    Domain name of the Host
    Example: "-"

  - `items.driverVersion` (string,null)
    Driver version
    Example: "v1.0.0"

  - `items.firmwareVersion` (string,null)
    Firmware version
    Example: "v1.0.0"

  - `items.generation` (integer)
    Generation Time of the Resource Filter, Sort
    Example: 1652172206

  - `items.hostId` (integer,null)
    ID of the Host resource
    Example: 101780

  - `items.hostName` (string,null)
    Host Name Filter, Sort
    Example: "test-host"

  - `items.hostSpeed` (integer,null)
    ID of the Host resource
    Example: 100

  - `items.ipAddr` (string,null)
    Ip Address
    Example: "1.1.1.1"

  - `items.model` (string,null)
    Host Model
    Example: "model_1"

  - `items.nvmeSubsystemNqn` (string,null)
    Subsystem NQN of NVMe/TCP hostpath
    Example: "nqn.2020-07.com.hpe:8ee43ce5-8264-4fcf-9990-a894f56386c7"

  - `items.pathType` (string,null)
    Path Type Filter
    Example: "FC"

  - `items.portPos` (object,null)

  - `items.portPos.node` (integer,null)
    Node Port
    Example: 1

  - `items.portPos.port` (integer,null)
    Port
    Example: 1

  - `items.portPos.slot` (integer,null)
    Slot
    Example: 1

  - `items.resourceUri` (string,null)
    resourceUri for detailed hostpath object
    Example: "/v1/storage-systems/host-paths/dbce79b2612cde02a6e0be8934c330ec"

  - `items.scHostInitiatorId` (string,null)
    Host Service Initiator Id Filter
    Example: "1223f5s"

  - `items.switchPortWwn` (string,null)
    Switch Port WWN
    Example: "5001438026e98a60"

  - `items.systemUid` (string)
    System Uid Filter
    Example: "7CE727P35M"

  - `items.systemWwn` (string)
    System serial Number Filter, Sort
    Example: "swK21"

  - `items.uri` (string,null)
    Uri
    Example: "/api/v3/hostpaths/dbce79b2612cde02a6e0be8934c330ec"

  - `items.vendor` (string,null)
    Vendor
    Example: "-"

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


