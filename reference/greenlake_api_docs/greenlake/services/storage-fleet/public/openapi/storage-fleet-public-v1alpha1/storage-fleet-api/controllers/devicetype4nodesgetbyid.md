---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/controllers/devicetype4nodesgetbyid.md"
scraped_at: "2026-06-07T06:16:08.660391+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Node identified by {id}

Get details of HPE Alletra Storage MP B10000 Node identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the node
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource.
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `type` (string, required)
    type
    Example: "string"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

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

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Controller Node 0"

  - `domain` (string,null)
    Domain that the resource belongs to

  - `enclosureCardId` (integer,null)
    ID of the enclosure card

  - `enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card

  - `enclosureId` (integer,null)
    ID of the enclosure

  - `enclosureUid` (string,null)
    Unique Identifier of the enclosure

  - `generation` (integer,null)
    generation

  - `inCluster` (boolean,null)
    Indicates if this node is part of the cluster.
    Example: true

  - `kernelVersion` (string,null)
    Kernel version
    Example: "4.2.1"

  - `master` (boolean,null)
    Indicates if this is the master node.
    Example: true

  - `memoryMiB` (integer,null)
    Total data memory in the node in MiB
    Example: 5

  - `name` (string,null)
    Name of the resource.
    Example: "4UW0002941-0"

  - `online` (boolean,null)
    Indicates if this node is online
    Example: true

  - `resourceUri` (string,null)
    resourceUri for detailed node object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/nodes/e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `systemId` (string,null)
    SystemId/Serial Number  of the array.
    Example: "7CE751P312"

  - `uptime` (object,null)
    The time that the system has been up since

  - `uptime.ms` (integer,null)
    Epoch time in milliseconds
    Example: 123423423

  - `uptime.tz` (string,null)
    Time zone name
    Example: "IST"

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


