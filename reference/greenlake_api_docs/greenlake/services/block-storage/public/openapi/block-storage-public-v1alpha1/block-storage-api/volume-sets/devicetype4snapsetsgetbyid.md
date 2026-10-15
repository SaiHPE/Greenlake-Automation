---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/snapsets/{snapsetId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4snapsetsgetbyid.md"
scraped_at: "2026-06-07T06:14:34.509004+00:00Z"
---

# Get details of snapsets identified by {snapsetId} for Applicationset identified by {appsetId} for HPE Alletra Storage MP B10000

Get details of snapset identified by {snapsetId} for Applicationset identified by {appsetId} for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/snapsets/{snapsetId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `appsetId` (string, required)
    UID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `snapsetId` (string, required)
    Identifier of snapset.
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    uid of the snapshotset.
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

  - `appSetImportance` (string,null)
    Importance Level
    Example: "NORMAL"

  - `appSetName` (string,null)
    Application set name
    Example: "KA_VEGA_APPSET1_186"

  - `appSetType` (string,null)
    Type of the snapshotset
    Example: "Oracle Database"

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

  - `creationTime` (object,null)
    Creation Time

  - `creationTime.ms` (integer,null)

  - `creationTime.tz` (string,null)

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `displayName` (string,null)
    Display Name
    Example: "Application Set KA_VEGA_APPSET1_186 "

  - `domain` (string,null)
    Domain name
    Example: "Domain"

  - `exportStatus` (string,null)
    Export status
    Example: "PARTIALLY_EXPORTED"

  - `generation` (integer,null)
    generation

  - `kvPairsPresent` (boolean)
    Represents KV pairs present or not
    Example: true

  - `members` (array,null)
    Volume Names
    Example: ["vol1","vol2"]

  - `mode` (string,null)
    Mode of the snapset.
    Example: "RO"

  - `name` (string,null)
    Name of the snapshotset.
    Example: "KA_VEGA_APPSET2_186"

  - `shortName` (string,null)
    Short name of the snapshotset
    Example: "VegaSnapshotSets~92775"

  - `snapSetId` (integer,null)
    ID
    Example: 5

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
