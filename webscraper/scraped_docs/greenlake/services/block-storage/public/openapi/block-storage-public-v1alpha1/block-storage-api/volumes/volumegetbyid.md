---
title: "GET /block-storage/v1alpha1/volumes/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volumes/volumegetbyid.md"
scraped_at: "2026-06-07T06:14:39.807828+00:00Z"
---

# Get details of Volume identified by {id}

Get details of Volume identified by {id}

Endpoint: GET /block-storage/v1alpha1/volumes/{id}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UID(volumeuid) of the storage system
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the storage system object.

  - `type` (string, required)
    type
    Example: "string"

  - `associatedLinks` (array,null)
    Associated Links
    Example: [{"resourceUri":"/block-storage/v1alpha1/storage-systems/storage-pools/{uid}","type":"storage-pools"},{"resourceUri":"/block-storage/v1alpha1/storage-systems/volume-sets/{uid}","type":"volume-sets"},{"resourceUri":"/block-storage/v1alpha1/storage-systems/{uid}","type":"systems"}]

  - `associatedLinks.resourceUri` (string,null)
    Resource URI

  - `associatedLinks.type` (string)
    Resource Name

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the volume resource belongs
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

  - `generation` (integer,null)
    generation

  - `healthState` (string,null)
    Health State of volume.`
    Example: "NORMAL"

  - `hostWrittenCapacityMiB` (number,null)
    Host written data size in MiB.

  - `intrinsicResource` (string,null)
    Type of volume
    Example: "volume"

  - `isInternal` (boolean,null)
    boolean value which specifies if it is a systemVolume or not Filter

  - `name` (string,null)
    A user friendly name to identify the storage system volume (resourceName).
    Example: "Finance"

  - `productFamily` (string,null)
    Product Family
    Example: "deviceType1"

  - `provisionedSizeMiB` (number,null)
    Provisioned Size in MiB
    Example: 2048

  - `resourceUri` (string,null)
    resourceUri for detailed volume object
    Example: "/block-storage/v1alpha1/storage-systems/2FF70002AC01F0FF/volumes/{uid}"

  - `sizeMiB` (number,null)
    Size in MiB

  - `spaceWarning` (number,null)
    User alloc space warning

  - `subType` (string,null)
    subType of the volume
    Example: "PROVTYPE_DDS"

  - `systemId` (string,null)
    SystemUid/Serial Number  of the array.
    Example: "7CE751P312"

  - `thinSavings` (string,null)
    Thin savings
    Example: "1:1"

  - `usedCapacityPercent` (number,null)
    Used capacity percentage of volume. Filter, Sort
    Example: 1.2345

  - `usedSizeMiB` (number,null)
    Size in MiB

  - `volumeSetId` (string,null)
    SystemUid/serialNumber of the volumeSet.
    Example: "7CE751P312"

  - `volumeType` (string,null)
    VV Type
    Example: "VVTYPE_BASE"

  - `wwn` (string,null)
    Volume wwn.

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
