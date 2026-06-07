---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4supportsettingsget.md"
scraped_at: "2026-06-07T06:16:05.017658+00:00Z"
---

# Get support settings for an HPE Alletra Storage MP B10000 storage system

Get support settings for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings
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
    Unique identifier of the support settings.
    Example: "7CE726P1VX"

  - `items.type` (string, required)
    The type of resource.
    Example: "support-settings"

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

  - `items.connectToHpe` (string,null)
    Enable remote support by allowing sending of files from device to HPE. Allowed values: enabled or disabled.
    Example: "disabled"

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1az"

  - `items.emailNotifications` (string,null)
    Receive email notifications. Allowed values: enabled or disabled.
    Example: "enabled"

  - `items.enterpriseServerUrl` (string,null)
    Callhome collection server URL
    Example: "server.com/collect"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627540915530

  - `items.miniInsploreEnabled` (string,null)
    Enables/Disable scheduled Mini-Insplore collection. Allowed values: enabled or disabled.
    Example: "disabled"

  - `items.remoteAccess` (string,null)
    Enable/Disable Remote Access. Allowed values: DISABLE or ENABLE_NONROOT or ENABLE_ROOT. It is mandatory.
    Enum: "DISABLE", "ENABLE_NONROOT", "ENABLE_ROOT"

  - `items.remoteRequest` (array,null)
    Remote Request Details

  - `items.remoteRequest.remoteAccessRequest` (object,null)
    Remote Access info

  - `items.remoteRequest.remoteAccessRequest.data` (array,null)
    Info of the person requesting remote access

  - `items.remoteRequest.remoteAccessRequest.data.email` (string,null)
    Email of the person requesting remote access
    Example: "xyz@hpe.com"

  - `items.remoteRequest.remoteAccessRequest.data.id` (string)
    id of the request
    Example: "12rft5567d"

  - `items.remoteRequest.remoteAccessRequest.message` (object,null)
    Remote Access Alert Message

  - `items.remoteRequest.remoteAccessRequest.message.args` (array,null)
    email addresses

  - `items.remoteRequest.remoteAccessRequest.message.default` (string,null)
    Default Name
    Example: "Remote access has been requested"

  - `items.remoteRequest.remoteAccessRequest.message.key` (string,null)
    Key of the Message
    Example: "NEW_ACCESS_REQUEST"

  - `items.remoteRequest.remoteSession` (object,null)
    Information of established remote session

  - `items.resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/supportsettings"

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


