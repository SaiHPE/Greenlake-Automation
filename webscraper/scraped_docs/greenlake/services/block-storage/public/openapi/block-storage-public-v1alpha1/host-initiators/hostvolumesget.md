---
title: "GET /block-storage/v1alpha1/host-initiators/{hostId}/volumes"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-initiators/hostvolumesget.md"
scraped_at: "2026-06-07T06:14:23.577207+00:00Z"
---

# Get details of volumes associated with a host identified by {uid}

Get details of volumes associated with a host identified by {uid}

Endpoint: GET /block-storage/v1alpha1/host-initiators/{hostId}/volumes
Version: 1.0.0
Security: bearer

## Path parameters:

  - `hostId` (string, required)
    Id of the Host.
    Example: "2b09e744496246859fde6c132b2091d3"

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
    ID of the resource
    Example: "e66ed5ce8d35961481a48b4f78bb06b4"

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

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
    customerId
    Example: "fc5f41652a53497e88cdcebc715cc1cf"

  - `items.intrinsicResource` (string,null)
    type of volume
    Example: "vvol"

  - `items.iops` (number,null)
    IOPS
    Example: 4702

  - `items.latencyMs` (number,null)
    Latency in ms
    Example: 1.2

  - `items.lunId` (integer,null)
    lunid

  - `items.pathCount` (integer,null)
    The number of connections from that volume
    Example: 2

  - `items.readLatency` (number,null)
    Latency in ms
    Example: 1.2

  - `items.resourceUri` (string,null)
    resourceUri of the volume
    Example: "/storage-fleet/v1alpha1/devtype1-storage-systems/7CE738P06J/volumes/e1839c72fef8784f2c77194efb8b2620"

  - `items.systemId` (string,null)
    SystemUid of the system associated with the volume
    Example: "7CE751P312"

  - `items.targetNqn` (string,null)
    Subsystem NQN id for the NVMe host to which the volume is exported
    Example: "nqn.2021-04.com.hpe:volume-1"

  - `items.throughputKbps` (number,null)
    The throughput in kbps
    Example: 477219.2

  - `items.volumeName` (string,null)
    The name of the volume
    Example: "test-vv"

  - `items.writeLatency` (number,null)
    Latency in ms
    Example: 1.2

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


