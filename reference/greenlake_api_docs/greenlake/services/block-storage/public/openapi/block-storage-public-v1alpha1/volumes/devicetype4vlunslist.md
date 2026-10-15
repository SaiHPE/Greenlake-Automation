---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/vluns"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4vlunslist.md"
scraped_at: "2026-06-07T06:14:29.317429+00:00Z"
---

# Get details of vluns for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

Get details of vluns for Volume identified by {volumeId} for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes/{id}/vluns
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID(volumeuid) of the storage system
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter by Key.
    Example: "name eq array1 and wwn eq 2FF70002AC018D94"

  - `sort` (string)
    Query to sort the response with specified key and order
    Example: "id asc,name desc"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    uid of the vlun Filter

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.active` (boolean,null)
    Indicates if this is an active VLUN or a template
    Example: true

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

  - `items.deviceWwns` (string,null)
    Device WWNs
    Example: "wwn"

  - `items.diskPartition` (string,null)
    Disk partition of host

  - `items.displayname` (string,null)
    SED state

  - `items.domain` (string,null)
    SED state

  - `items.failedPathInterval` (integer,null)
    Monitoring interval in seconds after which the host checks for failed paths
    Example: 1

  - `items.failedPathPolicy` (string,null)
    Failed path monitoring method

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.initiators` (object,null)
    Initiator details

  - `items.initiators.deviceDiscoveredName` (string,null)
    Host/HostGroup name on device.
    Example: "TEST11"

  - `items.initiators.id` (string)
    Resource id
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.initiators.resourceUri` (string,null)
    Resource URI
    Example: "/v1/host-initiators/6848ef683c27403e96caa51816ddc72c"

  - `items.initiators.type` (string)
    Resource Name
    Example: "host-initiators"

  - `items.lun` (integer,null)
    Exported LUN ID Filter, Sort
    Example: 1

  - `items.mountPoint` (string,null)
    Mount points of devices

  - `items.mountPointFsau` (integer,null)
    File system allocation unit in MiB
    Example: 1

  - `items.multiPathType` (string,null)
    Multi-path method in use

  - `items.portPos` (object,null)
    System port VLUN is exported through. It includes node number, slot number, and port number

  - `items.portPos.node` (integer,null)
    Filter, Sort
    Example: 1

  - `items.portPos.port` (integer,null)
    Filter, Sort
    Example: 1

  - `items.portPos.slot` (integer,null)
    Filter, Sort
    Example: 1

  - `items.rawVolume` (string,null)
    Volume that has not been formatted. Yes if it supports

  - `items.remoteName` (string,null)
    Host WWN, iSCSI name, or SAS address; depending on port type

  - `items.resourceUri` (string,null)
    resourceUri for detailed vlun object
    Example: "- TO BE IMPLEMENTED"

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.status` (string,null)
    SED state

  - `items.systemId` (string,null)
    System Uid Filter

  - `items.targetNqn` (string,null)
    "Subsystem NQN id for the NVMe host to which the volumes are exported"
    Example: "nqn.2020-09.com.hpe:b0eb957f-cb5c-4b31-a97a-80f9be7d77de"

  - `items.tpgId` (integer,null)
    SED state
    Example: 1

  - `items.usedSpace` (integer,null)
    Host devices used space in MiB
    Example: 1

  - `items.vlunType` (string,null)
    VLUN type

  - `items.volumeGroup` (string,null)
    Volume group info

  - `items.volumeManager` (string,null)
    Volume Manager tool used

  - `items.volumeName` (string,null)
    Name of exported virtual volume or volume set name Filter

  - `items.volumeWwn` (string,null)
    WWN of exported volume.If a volume set is exported, then this value is null. Filter

  - `items.vvReservedUserSpace` (integer,null)
    Volume user reserved space in MiB
    Example: 1

  - `items.vvSize` (integer,null)
    Size of volume in MiB
    Example: 1

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
