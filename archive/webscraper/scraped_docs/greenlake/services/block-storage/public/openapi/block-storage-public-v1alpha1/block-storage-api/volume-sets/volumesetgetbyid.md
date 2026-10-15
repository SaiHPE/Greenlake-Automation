---
title: "GET /block-storage/v1alpha1/volume-sets/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/volumesetgetbyid.md"
scraped_at: "2026-06-07T06:14:36.587824+00:00Z"
---

# Get volume-set identified by id

Get volume-set identified by id

Endpoint: GET /block-storage/v1alpha1/volume-sets/{id}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UID of Volume Set
    Example: "fd3244ef7f1ab8bd16500c7a41bdf8f8"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    id of the volume set Filter
    Example: "4c74ec5c-ecec-4483-9506-3fb5dc45b5d0"

  - `type` (string, required)
    type
    Example: "string"

  - `appType` (string,null)
    Application name Filter
    Example: "Oracle Database"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

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

  - `exportStatus` (string,null)
    Export status
    Example: "PARTIALLY_EXPORTED"

  - `generation` (integer,null)
    generation Filter, Sort

  - `healthState` (string,null)
    health state

  - `hostWrittenCapacityMiB` (number,null)
    Host written capacity in MiB

  - `intrinsicResource` (string,null)
    Intrinsic resource type

  - `iops` (number,null)
    IOPS

  - `isInternal` (boolean,null)
    Is an internal resource

  - `latency` (number,null)
    Latency

  - `location` (string,null)
    location

  - `name` (string,null)
    name of volume-set Filter, Sort
    Example: "snap11"

  - `productFamily` (string,null)
    Product Family
    Example: "deviceType1"

  - `provisionedSizeMiB` (number,null)
    Provisioned size in MiB

  - `resourceUri` (string,null)
    resourceUri for detailed volume object
    Example: "/block-storage/v1alpha1/storage-systems/volume-sets"

  - `sizeMiB` (number,null)
    Size in MiB

  - `spaceWarning` (number,null)
    Space warning set for the resource

  - `subType` (string,null)
    subType

  - `systemId` (string,null)
    system ID. Filter, Sort
    Example: "7CE751P312"

  - `thinSavings` (string,null)
    ThinSavings

  - `throughPut` (number,null)
    ThroughPut for the resource

  - `totalReservedMiB` (number,null)
    Total reserved MiB for the resource

  - `usedCapacityPercent` (number,null)
    Used capacity percentage

  - `usedSizeMiB` (number,null)
    Used size in MiB

  - `volumeSetId` (string,null)
    UID of the volume set Id

  - `volumeType` (string,null)
    Type of volume

  - `volumesCount` (integer,null)
    The number of volumes in an application
    Example: 5

  - `vvSetType` (string,null)
    Type of the volume-set
    Example: "VVSET"

  - `wwn` (string,null)
    wwn of the volume

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


