---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/telemetry"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4telemetryget.md"
scraped_at: "2026-06-07T06:16:19.321943+00:00Z"
---

# Get telemetry status for an HPE Alletra Storage MP B10000 storage system

Get telemetry status for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/telemetry
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

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
    Unique identifier of the callhome status.

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.collectionServer` (string,null)
    Callhome Collection server URL

  - `items.connectivityStatus` (string,null)
    Callhome connectivity status.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.connectivityTestTime` (object,null)
    Last connectivity test time.

  - `items.connectivityTestTime.ms` (integer,null)
    Epoch time in milliseconds
    Example: 1599631885

  - `items.connectivityTestTime.tz` (string,null)
    Time zone name
    Example: "Asia/Kolkata"

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cv"

  - `items.details` (array,null)

  - `items.details.args` (array,null)

  - `items.details.default` (string,null)
    Text in the default language

  - `items.details.key` (string,null)
    Key of the message

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627533960634

  - `items.lastFileSent` (string,null)
    Last sent file name via callhome.

  - `items.lastFileTransferTime` (object,null)
    Last sent file time via callhome.

  - `items.lastSuccessfulConnectivityTestTime` (object,null)
    Last successful connectivity time.

  - `items.proxyConnectivity` (string,null)
    Proxy connectivity status.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.rDaConfigured` (string,null)
    Callhome transport agent configuration details.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.rDaStatus` (string,null)
    Status of Callhome Transport Agent.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.rSvsStatus` (string,null)
    Status of callhome agent.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.rTsStatus` (string,null)
    Status of Real time scrubber.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/telemetryStatus"

  - `items.rolledUpStatus` (string,null)
    Callhome Rolled up status.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.sharedVolumeStatus` (string,null)
    Shared Volume status
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

  - `items.transferStatus` (string,null)
    Callhome File Transfer transfer.
    Enum: "NORMAL", "FAILED", "NOT_APPLICABLE", "DISABLED", null

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


