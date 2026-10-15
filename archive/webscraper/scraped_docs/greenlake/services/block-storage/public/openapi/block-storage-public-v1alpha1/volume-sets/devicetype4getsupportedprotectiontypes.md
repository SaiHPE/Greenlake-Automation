---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/supported-protection"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4getsupportedprotectiontypes.md"
scraped_at: "2026-06-07T06:14:27.103860+00:00Z"
---

# Get supported protection types for application set identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Get supported protection types for application set identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/supported-protection
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
    Identifier for the resource.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.asyncPartners` (array,null)
    List of potential replication partners that can be part of asynchronous protection policy

  - `items.asyncPartners.id` (string, required)
    Id of replication partner
    Example: "5a5ce66d4814a5e5156de428abb0a589"

  - `items.asyncPartners.asyncPartner` (string,null)
    Shows asynchronous replication partner associated with SLD configuration. This is applicable only if the parent partner is of sync type.
    Example: "CS2-A630-SVQ8"

  - `items.asyncPartners.isActiveSyncSupported` (boolean,null)
    States if Active-Sync is supported or not
    Example: true

  - `items.asyncPartners.isPeerPersistanceSupported` (boolean,null)
    States if Peer Persistance is supported or not
    Example: true

  - `items.asyncPartners.minAsyncRpo` (integer,null)
    Minimum async RPO value in seconds for asynchronous data replication.
    Example: 30

  - `items.asyncPartners.name` (string)
    Name of replication partner
    Example: "s2930"

  - `items.asyncPartners.resourceUri` (string)
    Resource URI for replication partner
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE815P2BH/replicationpartners/5a5ce66d4814a5e5156de428abb0a589"

  - `items.asyncPartners.syncPartner` (string,null)
    Shows synchronous replication partner associated with SLD configuration. This is applicable only if the parent partner is of async type.
    Example: "CS2-A630-SVQ8_1"

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

  - `items.isSldSupported` (boolean)
    Shows if SLD is supported or not
    Example: true

  - `items.protectionTypes` (array,null)
    List of protection policies types that can be configured on the application set Possible values: schedule, async, sync
    Example: ["schedule","async","sync"]

  - `items.syncPartners` (array,null)
    List of potential replication partners that can be part of synchronous protection policy

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
