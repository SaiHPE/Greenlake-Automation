---
title: "GET /block-storage/v1alpha1/volume-sets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/volumesetlist.md"
scraped_at: "2026-06-07T06:14:36.585288+00:00Z"
---

# Get all volume-sets

Get all volume sets

Endpoint: GET /block-storage/v1alpha1/volume-sets
Version: 1.0.0
Security: bearer

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter by Key.
    Example: "name eq volset and systemId eq 7CE751P312"

  - `sort` (string)
    oData query to sort by Key.
    Example: "systemId desc"

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
    id of the volume set Filter
    Example: "4c74ec5c-ecec-4483-9506-3fb5dc45b5d0"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.appType` (string,null)
    Application name Filter
    Example: "Oracle Database"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the volume resource belongs
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
    generation Filter, Sort

  - `items.healthState` (string,null)
    health state

  - `items.hostWrittenCapacityMiB` (number,null)
    Host written capacity in MiB

  - `items.intrinsicResource` (string,null)
    Intrinsic resource type

  - `items.iops` (number,null)
    IOPS

  - `items.isInternal` (boolean,null)
    Is an internal resource

  - `items.latency` (number,null)
    Latency

  - `items.location` (string,null)
    location

  - `items.name` (string,null)
    name of volume-set Filter, Sort
    Example: "snap11"

  - `items.productFamily` (string,null)
    Product Family
    Example: "deviceType1"

  - `items.provisionedSizeMiB` (number,null)
    Provisioned size in MiB

  - `items.resourceUri` (string,null)
    resourceUri for detailed volume object
    Example: "/block-storage/v1alpha1/storage-systems/volume-sets"

  - `items.sizeMiB` (number,null)
    Size in MiB

  - `items.spaceWarning` (number,null)
    Space warning set for the resource

  - `items.subType` (string,null)
    subType

  - `items.systemId` (string,null)
    system ID. Filter, Sort
    Example: "7CE751P312"

  - `items.thinSavings` (string,null)
    ThinSavings

  - `items.throughPut` (number,null)
    ThroughPut for the resource

  - `items.totalReservedMiB` (number,null)
    Total reserved MiB for the resource

  - `items.usedCapacityPercent` (number,null)
    Used capacity percentage

  - `items.usedSizeMiB` (number,null)
    Used size in MiB

  - `items.volumeSetId` (string,null)
    UID of the volume set Id

  - `items.volumeType` (string,null)
    Type of volume

  - `items.volumesCount` (integer,null)
    The number of volumes in an application
    Example: 5

  - `items.wwn` (string,null)
    wwn of the volume

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


