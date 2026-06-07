---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-sets/{hostSetId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/host-sets/devicetype4gethostsetsbyid.md"
scraped_at: "2026-06-07T06:14:32.758601+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Host Set identified by {HostSetId}

Get details of HPE Alletra Storage MP B10000 Host Set identified by {HostSetId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-sets/{hostSetId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `hostSetId` (string, required)
    ID of the HPE Alletra Storage MP B10000 Host Set. A 42 digit hexadecimal number.
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    HostSet Resource UID
    Example: "1223f5s"

  - `type` (string, required)
    Type of the resource

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `comment` (string,null)
    Comment on the Host Set
    Example: "hostset comment"

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the host-set resource belongs
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `domain` (string,null)
    Domain name of the Host Set
    Example: "slt"

  - `generation` (integer)
    Generation Time of the Resource
    Example: 101780

  - `hostSetId` (integer,null)
    Numeric ID of the resource
    Example: 101780

  - `members` (array,null)
    system ntp addresses

  - `name` (string,null)
    Host Set Name
    Example: "test-host-set"

  - `resourceUri` (string,null)
    resourceUri for detailed hostset object
    Example: "/v1/storage-systems/host-setss/dbce79b2612cde02a6e0be8934c330ec"

  - `scHostGroupId` (string,null)
    Host Service HostGroup Id
    Example: "1223f5s"

  - `systemUid` (string)
    Serail Number of the system
    Example: "swK21"

  - `systemWwn` (string)
    System wwn
    Example: "swK21"

  - `uri` (string,null)
    Uri
    Example: "/api/v3/hostsets/dbce79b2612cde02a6e0be8934c330ec"

  - `uuid` (string)
    HostSet Resource UUID
    Example: "1223f5s"

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


