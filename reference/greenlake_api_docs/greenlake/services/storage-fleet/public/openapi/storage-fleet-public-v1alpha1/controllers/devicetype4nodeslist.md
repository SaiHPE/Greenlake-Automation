---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/controllers/devicetype4nodeslist.md"
scraped_at: "2026-06-07T06:15:54.528779+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Nodes

Get details of HPE Alletra Storage MP B10000 Nodes

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes
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
    oData query to filter nodes resource by key.
    Example: "systemUid eq 7CE751P312"

  - `sort` (string)
    oData query to sort nodes resource by key.
    Example: "systemId desc"

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
    Unique Identifier of the resource. Filter
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.associatedLinks` (array)
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

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "Controller Node 0"

  - `items.domain` (string,null)
    Domain that the resource belongs to

  - `items.enclosureCardId` (integer,null)
    ID of the enclosure card

  - `items.enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card Filter

  - `items.enclosureId` (integer,null)
    ID of the enclosure

  - `items.enclosureUid` (string,null)
    Unique Identifier of the enclosure Filter

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.inCluster` (boolean,null)
    Indicates if this node is part of the cluster.
    Example: true

  - `items.kernelVersion` (string,null)
    Kernel version
    Example: "4.2.1"

  - `items.master` (boolean,null)
    Indicates if this is the master node.
    Example: true

  - `items.memoryMiB` (integer,null)
    Total data memory in the node in MiB
    Example: 5

  - `items.name` (string,null)
    Name of the resource. Filter, Sort
    Example: "4UW0002941-0"

  - `items.nodeId` (integer,null)
    Numeric ID of the resource.

  - `items.online` (boolean,null)
    Indicates if this node is online
    Example: true

  - `items.resourceUri` (string,null)
    resourceUri for detailed node object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/2FF70002AC018D94/nodes/e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.systemId` (string,null)
    SystemId/serialNumber of the array.
    Example: "7CE751P312"

  - `items.uptime` (object,null)
    The time that the system has been up since

  - `items.uptime.ms` (integer,null)
    Epoch time in milliseconds
    Example: 123423423

  - `items.uptime.tz` (string,null)
    Time zone name
    Example: "IST"

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


## Response 304 fields
