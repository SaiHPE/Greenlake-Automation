---
title: "GET /storage-fleet/v1alpha1/storage-systems"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/systemslist.md"
scraped_at: "2026-06-07T06:16:14.494183+00:00Z"
---

# Get all storage systems

Get all storage systems

Endpoint: GET /storage-fleet/v1alpha1/storage-systems
Version: 1.2.0
Security: bearer

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter systems by Key.
    Example: "name eq VEGA_CB1507_8400_2N_150"

  - `sort` (string)
    Query to sort the response with specified key and order
    Example: "id asc,name desc"

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
    UUID string uniquely identifying the storage system object.
    Example: "7CE751P312"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.arrayList` (array,null)
    The list of Nimble arrays part of this system.

  - `items.arrayList.model` (string,null)
    Array model.
    Example: "CS3000"

  - `items.arrayList.name` (string,null)
    The user provided name of the array.
    Example: "NimbleArray45"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.callhomeStatus` (string)
    Device Call-home connectivity status.
    Enum: "ENABLED_NORMAL", "ENABLED_DEGRADED", "DISABLED", "UNKNOWN"

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

  - `items.description` (string,null)
    A brief description of the storage system.

  - `items.fqdn` (string,null)
    Fully qualified domain name of the array
    Example: "s9.in.hpecorp.net"

  - `items.generation` (integer,null)
    generation

  - `items.lastConnectedTime` (integer,null)
    Last time when the system was connected

  - `items.maxVolumeDecoSizeMib` (string,null)
    Maximum supported size for a DECO volume. This is applicable for HPE Alletra Storage MP 10.4.0, HPE Primera 4.6.0 and HPE Alletra 9K 9.6.0 and later system OS versions.
    Example: "67108864"

  - `items.mgmtIp` (string,null)

  - `items.minVolumeDecoSizeMib` (string,null)
    Minimum supported size for a DECO volume. This is applicable for HPE Alletra Storage MP 10.4.0, HPE Primera 4.6.0 and HPE Alletra 9K 9.6.0 and later system OS versions.
    Example: "256"

  - `items.model` (string,null)
    Model of the storage system Filter, Sort

  - `items.name` (string,null)
    A name to identify the storage system. Filter, Sort
    Example: "DeviceType1Billing"

  - `items.productFamily` (string)
    Storage device type
    Example: "deviceType1"

  - `items.resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/storage-systems/2FF70002AC018D94"

  - `items.serialNumber` (string,null)
    Serial number of the array
    Example: "CZ2D2407WM"

  - `items.softwareVersion` (string,null)
    Software version of the storage system Filter, Sort

  - `items.state` (string)
    For deviceType1 State derived from ports, enclosure, disk and node state for deviceType2 state is state reported by deviceType2 array
    Enum: "NORMAL", "DEGRADED"

  - `items.tierName` (string,null)
    Name of the storage tier
    Example: "HPE GreenLake for Block Storage"

  - `items.tierType` (string,null)
    StorageTier.
    Enum: "STORAGE_TIER_9000_NVME", "STORAGE_TIER_6000_NVME", "STORAGE_TIER_NIMBLE_HYBRID", "STORAGE_TIER_NIMBLE_AFA", "STORAGE_TIER_600_AFA", "STORAGE_TIER_600_HYBRID", "STORAGE_TIER_NIMBLE_VSA", "STORAGE_TIER_MISSION_CRITICAL", "STORAGE_TIER_BUSINESS_CRITICAL", "STORAGE_TIER_GENERAL_PURPOSE", "STORAGE_TIER_5000", "STORAGE_TIER_10000_NVME", "STORAGE_TIER_10020_MP", "STORAGE_TIER_ALLETRA_MP_X10000", "STORAGE_TIER_UNKNOWN", "STORAGE_TIER_VIRTUAL_ARCUS", "STORAGE_TIER_HPE_BLOCK_STORAGE_AZURE"

  - `items.upSince` (integer,null)
    The time that the system has been up since
    Example: 1600084190299

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


