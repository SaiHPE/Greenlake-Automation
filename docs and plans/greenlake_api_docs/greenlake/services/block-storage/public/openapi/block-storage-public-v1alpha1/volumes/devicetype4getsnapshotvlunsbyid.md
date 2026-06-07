---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/vluns/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volumes/devicetype4getsnapshotvlunsbyid.md"
scraped_at: "2026-06-07T06:14:28.101960+00:00Z"
---

# Get details of vlun identified by {id} for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000

Get details of vlun identified by {id} for Snapshot identified by {snapshotId} for HPE Alletra Storage MP B10000

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{snapshotId}/vluns/{id}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `snapshotId` (string, required)
    UID of the snapshots
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

  - `id` (string, required)
    UID of the vlun
    Example: "a7c4e6593f51d0b98f0e40d7e6df04fd"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    uid of the vlun

  - `type` (string, required)
    VLUN type

  - `active` (boolean,null)
    Indicates if this is an active VLUN or a template
    Example: true

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

  - `deviceWwns` (string,null)
    Device WWNs

  - `diskPartition` (string,null)
    Disk partition of host

  - `displayname` (string,null)
    SED state

  - `domain` (string,null)
    SED state

  - `failedPathInterval` (integer,null)
    Monitoring interval in seconds after which the host checks for failed paths
    Example: 1

  - `failedPathPolicy` (string,null)
    Failed path monitoring method

  - `generation` (integer,null)
    generation

  - `initiators` (object,null)
    Initiator details

  - `initiators.deviceDiscoveredName` (string,null)
    Host/HostGroup name on device.
    Example: "TEST11"

  - `initiators.id` (string)
    Resource id
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `initiators.resourceUri` (string,null)
    Resource URI
    Example: "/v1/host-initiators/6848ef683c27403e96caa51816ddc72c"

  - `initiators.type` (string)
    Resource Name
    Example: "host-initiators"

  - `lun` (integer,null)
    Exported LUN ID
    Example: 1

  - `mountPoint` (string,null)
    Mount points of devices

  - `mountPointFsau` (integer,null)
    File system allocation unit in MiB
    Example: 1

  - `multiPathType` (string,null)
    Multi-path method in use

  - `portPos` (object,null)
    System port VLUN is exported through. It includes node number, slot number, and port number

  - `portPos.node` (integer,null)
    Example: 1

  - `portPos.port` (integer,null)
    Example: 1

  - `portPos.slot` (integer,null)
    Example: 1

  - `rawVolume` (string,null)
    Volume that has not been formatted. Yes if it supports

  - `remoteName` (string,null)
    Host WWN, iSCSI name, or SAS address; depending on port type

  - `resourceUri` (string,null)
    resourceUri for detailed vlun object
    Example: "- TO BE IMPLEMENTED"

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `status` (string,null)
    SED state

  - `systemId` (string,null)
    SED state

  - `targetNqn` (string,null)
    "Subsystem NQN id for the NVMe host to which the volumes are exported"
    Example: "nqn.2020-09.com.hpe:b0eb957f-cb5c-4b31-a97a-80f9be7d77de"

  - `tpgId` (integer,null)
    SED state
    Example: 1

  - `usedSpace` (integer,null)
    Host devices used space in MiB
    Example: 1

  - `vlunType` (string,null)
    VLUN type

  - `volumeGroup` (string,null)
    Volume group info

  - `volumeManager` (string,null)
    Volume Manager tool used

  - `volumeName` (string,null)
    Name of exported virtual volume or volume set name

  - `volumeWwn` (string,null)
    WWN of exported volume.If a volume set is exported, then this value is null.

  - `vvReservedUserSpace` (integer,null)
    Volume user reserved space in MiB
    Example: 1

  - `vvSize` (integer,null)
    Size of volume in MiB
    Example: 1

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
