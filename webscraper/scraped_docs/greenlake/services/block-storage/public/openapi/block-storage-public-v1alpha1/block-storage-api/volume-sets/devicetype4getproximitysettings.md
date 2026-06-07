---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/volume-sets/devicetype4getproximitysettings.md"
scraped_at: "2026-06-07T06:14:35.673794+00:00Z"
---

# Get hosts and proximity details identified by application set {id} for HPE Alletra Storage MP B10000 identified by {systemId}

Get hosts and proximity details identified by application set {id} for HPE Alletra Storage MP B10000 identified by {systemId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    ID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Id of the resource

  - `items.type` (string, required)
    type
    Example: "string"

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

  - `items.generation` (integer,null)
    generation

  - `items.hostGroupName` (string,null)
    Host group name
    Example: "hostset1"

  - `items.hosts` (array,null)

  - `items.hosts.dsccHostName` (string,null)
    Name of host in Data Services Cloud Console
    Example: "host1"

  - `items.hosts.hostId` (string,null)
    Unique ID of host
    Example: "0af26e4430948dd5c37bea1757107caf"

  - `items.hosts.hostNqn` (array,null)
    Host NQN information
    Example: ["nqn.2014-08.net.hpecorp.storage.mip:nvme:ESX173"]

  - `items.hosts.name` (string,null)
    Host name
    Example: "host1"

  - `items.hosts.os` (string,null)
    OS of host
    Example: "Windows Server"

  - `items.hosts.proximity` (object,null)

  - `items.hosts.proximity.isRemoteArraySupportReplication` (boolean)
    Boolean value to indicate if remote array OS version supports replication
    Example: true

  - `items.hosts.proximity.isSourceArraySupportReplication` (boolean)
    Boolean value to indicate if source array OS version supports replication
    Example: true

  - `items.hosts.proximity.localSystem` (string,null)
    Local system where host I/O path is Active optimized
    Example: "CS2-A630-SVQ8"

  - `items.hosts.proximity.proximityValue` (string,null)
    Host proximity to determine the Asymmetric Logical path access state
    Example: "PRIMARY"

  - `items.hosts.proximity.remoteSystem` (string,null)
    Remote system where host I/O path is Active Non-optimized
    Example: "s2937"

  - `items.hosts.targetNqn` (string,null)
    "Subsystem NQN id for the NVMe host to which the volumes are exported"
    Example: "nqn.2020-09.com.hpe:b0eb957f-cb5c-4b31-a97a-80f9be7d77de"

  - `items.systemId` (string,null)
    Unique ID or serial number of the system.
    Example: "7CE816P0SR"

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
