---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4volumesetsnapshotslist.md"
scraped_at: "2026-06-07T06:14:26.898928+00:00Z"
---

# Get snapshot details of volume sets identified by {id} for HPE Alletra Storage MP B10000

Get snapshot details of volume sets identified by {id} for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `filter` (string)
    oData query to filter by Key.
    Example: "name eq array1 and wwn eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort by Key.
    Example: "systemWWN desc"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    uid of the snapshotset. Filter
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

  - `items.appSetImportance` (string,null)
    Importance Level
    Example: "MEDIUM"

  - `items.appSetName` (string,null)
    Application set name
    Example: "KA_VEGA_APPSET1_186"

  - `items.appSetType` (string,null)
    Type of the snapshotset
    Example: "Oracle Database"

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

  - `items.creationTime` (object,null)
    Creation Time

  - `items.creationTime.ms` (integer,null)

  - `items.creationTime.tz` (string,null)

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.displayName` (string,null)
    Display Name
    Example: "Application Set KA_VEGA_APPSET1_186 "

  - `items.domain` (string,null)
    Domain name
    Example: "Domain"

  - `items.exportStatus` (string,null)
    Export status
    Example: "PARTIALLY_EXPORTED"

  - `items.generation` (integer,null)
    generation

  - `items.kvPairsPresent` (boolean)
    Represents KV pairs present or not
    Example: true

  - `items.members` (array,null)
    Volume Names
    Example: ["vol1","vol2"]

  - `items.mode` (string,null)
    Mode of the snapshotset
    Example: "RO"

  - `items.name` (string,null)
    Name of the snapshotset. Filter, Sort
    Example: "KA_VEGA_APPSET2_186"

  - `items.shortName` (string,null)
    Short name of the snapshotset
    Example: "VegaSnapshotSets~92775"

  - `items.snapSetId` (integer,null)
    ID
    Example: 5

  - `items.snapSetParentId` (integer,null)
    ParentId of the snapSet
    Example: 5

  - `items.snapSetParentName` (string,null)
    Parent name of the snapSet
    Example: "HPE"

  - `items.systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `items.vvSetType` (string,null)
    Type of the volume-set
    Example: "VVSET"

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
