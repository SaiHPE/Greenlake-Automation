---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-sets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-sets/devicetype4getallhostsets.md"
scraped_at: "2026-06-07T06:14:32.312756+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Host Sets

Get details of HPE Alletra Storage MP B10000 Host Sets

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-sets
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
    Lucene query to filter host set by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004817"

  - `sort` (string)
    oData query to sort host set resource by Key.
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
    HostSet Resource UID Filter
    Example: "1223f5s"

  - `items.type` (string, required)
    Type of the resource

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.comment` (string,null)
    Comment on the Host Set
    Example: "hostset comment"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the host-set resource belongs
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
    Domain name of the Host Set
    Example: "slt"

  - `items.generation` (integer)
    Generation Time of the Resource Filter, Sort
    Example: 101780

  - `items.hostSetId` (integer,null)
    Numeric ID of the resource
    Example: 101780

  - `items.members` (array,null)
    system ntp addresses Filter, Sort

  - `items.name` (string,null)
    Host Set Name Filter, Sort
    Example: "test-host-set"

  - `items.resourceUri` (string,null)
    resourceUri for detailed hostset object
    Example: "/v1/storage-systems/host-setss/dbce79b2612cde02a6e0be8934c330ec"

  - `items.scHostGroupId` (string,null)
    Host Service HostGroup Id Filter
    Example: "1223f5s"

  - `items.systemUid` (string)
    Serail Number of the system Filter
    Example: "swK21"

  - `items.systemWwn` (string)
    System wwn Filter, Sort
    Example: "swK21"

  - `items.uri` (string,null)
    Uri
    Example: "/api/v3/hostsets/dbce79b2612cde02a6e0be8934c330ec"

  - `items.uuid` (string)
    HostSet Resource UUID
    Example: "1223f5s"

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


