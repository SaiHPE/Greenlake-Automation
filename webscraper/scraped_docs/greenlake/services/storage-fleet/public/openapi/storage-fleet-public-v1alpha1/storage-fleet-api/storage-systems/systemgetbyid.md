---
title: "GET /storage-fleet/v1alpha1/storage-systems/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/systemgetbyid.md"
scraped_at: "2026-06-07T06:16:14.559560+00:00Z"
---

# Get storage system object identified by {id}

Get storage system object identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/storage-systems/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    Serial number of the device-type4 storage system
    Example: "SGH029VBHV"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the storage system object.
    Example: "7CE751P312"

  - `type` (string, required)
    type
    Example: "string"

  - `arrayList` (array,null)
    The list of Nimble arrays part of this system.

  - `arrayList.model` (string,null)
    Array model.
    Example: "CS3000"

  - `arrayList.name` (string,null)
    The user provided name of the array.
    Example: "NimbleArray45"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `callhomeStatus` (string)
    Device Call-home connectivity status
    Enum: "ENABLED_NORMAL", "ENABLED_DEGRADED", "DISABLED", "UNKNOWN"

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
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `description` (string,null)
    A brief description of the storage system.

  - `fqdn` (string,null)
    Fully qualified domain name of the system
    Example: "s9.in.hpecorp.net"

  - `generation` (integer,null)
    generation

  - `lastConnectedTime` (integer,null)
    Last time when the system was connected

  - `maxVolumeDecoSizeMib` (string,null)
    Maximum supported size for a DECO volume. This is applicable for HPE Alletra Storage MP 10.4.0, HPE Primera 4.6.0 and HPE Alletra 9K 9.6.0 and later system OS versions.
    Example: "67108864"

  - `mgmtIp` (string,null)

  - `minVolumeDecoSizeMib` (string,null)
    Minimum supported size for a DECO volume. This is applicable for HPE Alletra Storage MP 10.4.0, HPE Primera 4.6.0 and HPE Alletra 9K 9.6.0 and later system OS versions.
    Example: "256"

  - `model` (string,null)
    Model of the storage system

  - `name` (string,null)
    A name to identify the storage system.
    Example: "DeviceType1Billing"

  - `productFamily` (string)
    Storage device type
    Example: "deviceType1"

  - `resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/storage-systems/7CE751P312"

  - `serialNumber` (string,null)
    Serial number of the array
    Example: "CZ2D2407WM consoleUri for detailed storage object"

  - `softwareVersion` (string,null)
    Software version of the storage system

  - `state` (string)
    For deviceType1 State derived from ports, enclosure, disk and node state for deviceType2 state is state reported by deviceType2 array
    Enum: "NORMAL", "DEGRADED"

  - `tierName` (string,null)
    Name of the storage tier
    Example: "HPE GreenLake for Block Storage"

  - `tierType` (string,null)
    StorageTier.
    Enum: "STORAGE_TIER_9000_NVME", "STORAGE_TIER_6000_NVME", "STORAGE_TIER_NIMBLE_HYBRID", "STORAGE_TIER_NIMBLE_AFA", "STORAGE_TIER_600_AFA", "STORAGE_TIER_600_HYBRID", "STORAGE_TIER_NIMBLE_VSA", "STORAGE_TIER_MISSION_CRITICAL", "STORAGE_TIER_BUSINESS_CRITICAL", "STORAGE_TIER_GENERAL_PURPOSE", "STORAGE_TIER_5000", "STORAGE_TIER_10000_NVME", "STORAGE_TIER_10020_MP", "STORAGE_TIER_ALLETRA_MP_X10000", "STORAGE_TIER_UNKNOWN", "STORAGE_TIER_VIRTUAL_ARCUS", "STORAGE_TIER_HPE_BLOCK_STORAGE_AZURE"

  - `upSince` (integer,null)
    The time that the system has been up since
    Example: 1600084190299

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


