---
title: "GET /block-storage/v1alpha1/storage-systems/{systemId}/storage-pools/{id}/volumes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/storage-pools/storagepoolvolumeslist.md"
scraped_at: "2026-06-07T06:14:33.131641+00:00Z"
---

# Get all volumes for storage-pool identified by {id}

Get all volumes for storage-pool identified by {id}

Endpoint: GET /block-storage/v1alpha1/storage-systems/{systemId}/storage-pools/{id}/volumes
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    Identifier of pool. A 32 digit number.
    Example: "147c439db3ecb34d1ccccc932d14fd60"

## Query parameters:

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
    UUID string uniquely identifying the storage system object. Filter
    Example: "e66ed5ce8d35961481a48b4f78bb06b4"

  - `items.type` (string, required)
    type
    Example: "volume"

  - `items.associatedLinks` (array,null)
    Associated Links
    Example: [{"resourceUri":"/block-storage/v1alpha1/storage-systems/storage-pools/{uid}","type":"storage-pools"},{"resourceUri":"/block-storage/v1alpha1/storage-systems/volume-sets/{uid}","type":"volume-sets"},{"resourceUri":"/block-storage/v1alpha1/storage-systems/{uid}","type":"systems"}]

  - `items.associatedLinks.resourceUri` (string,null)
    Resource URI

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
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.generation` (integer,null)
    generation

  - `items.healthState` (string,null)
    Health State of volume. Filter, Sort
    Example: "NORMAL"

  - `items.hostWrittenCapacityMiB` (number,null)
    Host written data size in MiB. Filter, Sort

  - `items.intrinsicResource` (string,null)
    type of volume
    Example: "volume"

  - `items.isInternal` (boolean,null)
    boolean value which specifies if it is a systemVolume or not

  - `items.name` (string,null)
    A user friendly name to identify the storage system volume (resourceName). Filter, Sort
    Example: "Finance"

  - `items.productFamily` (string,null)
    Product Family
    Example: "deviceType1"

  - `items.provisionedSizeMiB` (number,null)
    Provisioned Size in MiB
    Example: 2048

  - `items.resourceUri` (string,null)
    resourceUri for detailed volume object
    Example: "/block-storage/v1alpha1/storage-systems/volumes"

  - `items.sizeMiB` (number,null)
    Size in MiB Filter, Sort
    Example: 2048

  - `items.spaceWarning` (number,null)
    User alloc space warning

  - `items.subType` (string,null)
    subType of the volume
    Example: "PROVTYPE_DDS"

  - `items.systemId` (string,null)
    SystemUid/Serial Number  of the array. Filter, Sort
    Example: "7CE751P312"

  - `items.thinSavings` (string,null)
    Thin savings
    Example: "1:1"

  - `items.usedCapacityPercent` (number,null)
    Used capacity percentage of volume.
    Example: 1.2345

  - `items.usedSizeMiB` (number,null)
    Size in MiB

  - `items.volumeSetId` (string,null)
    SystemUid/serialNumber of the volumeSet.
    Example: "7CE751P312"

  - `items.volumeType` (string,null)
    VV Type
    Example: "VVTYPE_BASE"

  - `items.wwn` (string,null)
    Volume wwn.
    Example: "60002AC0000000000000006B0001FFEB"

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


