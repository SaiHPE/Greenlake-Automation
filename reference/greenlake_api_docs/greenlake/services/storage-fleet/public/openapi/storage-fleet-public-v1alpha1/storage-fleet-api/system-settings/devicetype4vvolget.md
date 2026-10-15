---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvol"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vvolget.md"
scraped_at: "2026-06-07T06:16:20.227475+00:00Z"
---

# Get vVol details for an HPE Alletra Storage MP B10000 storage system

Get vVol details for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvol
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
    oData query to filter by Key.
    Example: "name eq array1 and wwn eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort by Key.
    Example: "systemWWN desc"

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
    Numeric ID of the resource
    Example: "79"

  - `items.type` (string, required)
    Type of VMware vVol
    Example: "FC"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

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

  - `items.compressionPolicy` (boolean,null)
    Compression policy of VMware vVol
    Example: true

  - `items.customerId` (string,null)
    customerId
    Example: "fafafaefu987823hfa"

  - `items.dedup` (string,null)
    VMware vVol deduplication
    Example: "dedup"

  - `items.displayName` (string,null)
    Name to be used for display purposes
    Example: "vVol"

  - `items.domain` (string,null)
    Domain that the resource belongs to
    Example: "Domain"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627538867363

  - `items.logicalSizeMiB` (integer,null)
    Logical size in MiB
    Example: 243

  - `items.name` (string,null)
    name of the resource
    Example: "vVol1"

  - `items.parentId` (integer,null)
    VMware vVol parent id
    Example: 88

  - `items.physicalSizeMiB` (integer,null)
    Physical size in MiB
    Example: 54

  - `items.provType` (string,null)
    Provision type of VMware vVol
    Enum: "PROVTYPE_FULL", "PROVTYPE_THIN", "PROVTYPE_SNAPSHOT", "PROVTYPE_PEER", "PROVTYPE_DEDUP", "PROVTYPE_DDS", "PROVTYPE_UNKNOWN"

  - `items.resourceUri` (string,null)
    URI of the resource
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/vvol"

  - `items.scName` (string,null)
    Name of Storage Container this VMware vVol belongs to
    Example: "sc1"

  - `items.scUuid` (string,null)
    Unique UID of Storage Container this VMware vVol belongs to
    Example: "983ihuah83ifua"

  - `items.systemId` (string,null)
    SystemUid/serialNumber of the array.
    Example: "7CE751P312"

  - `items.systemWwn` (string,null)
    WWN of the array
    Example: "2FF70002AC018D94"

  - `items.uid` (string,null)
    Unique Identifier of the resource
    Example: "908r897r928r4oo"

  - `items.uri` (string,null)
    uri for the vVol
    Example: "/api/v3/vvol/99691e493067b2b2acf1774fc0ccc011"

  - `items.vmName` (string,null)
    Name of Virtual Machine this VMware vVol belongs to
    Example: "VMware1"

  - `items.vmUuid` (string,null)
    Unique UID of Virual Machine this VMware vVol belongs to
    Example: "098327782ijrifn"

  - `items.vmwType` (string,null)
    VMW type of the VMware vVol
    Example: "vvol"

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


