---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/cim"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicecimget.md"
scraped_at: "2026-06-07T06:16:16.330781+00:00Z"
---

# Get CIM Network-Service details for an HPE Alletra Storage MP B10000 storage system

Get CIM Network-Service details for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/cim
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
    Unique Identifier of the resource
    Example: "012e5dce5c029c4c56bdda9b3e1eaaad"

  - `items.type` (string, required)
    The type of resource.
    Example: "cim-settings"

  - `items.cimPolicy` (string,null)
    Specifies the CIM Policy of CIM server
    Example: "replica_entity,one_hwid_per_view,use_pegasus_interop_namespace,no_tls_strict"

  - `items.cimState` (string,null)
    Specifies whether CIM state is active or inactive
    Example: "Active"

  - `items.cimVersion` (string,null)
    CIM version information
    Example: "V1"

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

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1qw"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627533171477

  - `items.httpPort` (integer,null)
    HTTP port number
    Example: 5988

  - `items.httpState` (boolean,null)
    Specifies whether HTTPState is enabled or disabled for CIM Server

  - `items.httpsPort` (integer,null)
    Specifies HTTPS port number
    Example: 5989

  - `items.httpsState` (boolean,null)
    Specifies whether HTTPS state is enabled or disabled for cim server
    Example: true

  - `items.pgVersion` (string,null)
    Information about PGVersion of CIM server
    Example: "2.14.1"

  - `items.serviceState` (boolean,null)
    Specifies whether service state is enabled or disabled
    Example: true

  - `items.slpPort` (integer,null)
    SLPport specification
    Example: 427

  - `items.slpState` (boolean,null)
    whether slpstate is enabled or disabled
    Example: true

  - `items.systemId` (string,null)
    SystemId of the storage system
    Example: "4UW0001540"

  - `items.systemWwn` (string,null)
    WWN of the array
    Example: "2FF70002AC018D94"

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


