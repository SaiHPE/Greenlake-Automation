---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths/{hostPathId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/host-paths/devicetype4gethostpathsbyid.md"
scraped_at: "2026-06-07T06:14:23.794424+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Host Path identified by {HostPathId}

Get details of HPE Alletra Storage MP B10000 Host Path identified by {HostPathId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths/{hostPathId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `hostPathId` (string, required)
    ID of the HPE Alletra Storage MP B10000 Host Path. A 42 digit hexadecimal number.
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    HostPath Resource UID
    Example: "1223f5s"

  - `type` (string, required)
    type of the resource

  - `address` (string,null)
    WWN Address of the Host Path
    Example: "810009440c9ce5824"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the host-path resource belongs
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `domain` (string,null)
    Domain name of the Host
    Example: "-"

  - `driverVersion` (string,null)
    Driver version
    Example: "v1.0.0"

  - `firmwareVersion` (string,null)
    Firmware version
    Example: "v1.0.0"

  - `generation` (integer)
    Generation Time of the Resource
    Example: 1652172206

  - `hostId` (integer,null)
    ID of the Host resource
    Example: 101780

  - `hostName` (string,null)
    Host Name
    Example: "test-host"

  - `hostSpeed` (integer,null)
    ID of the Host resource
    Example: 100

  - `ipAddr` (string,null)
    Ip Address
    Example: "1.1.1.1"

  - `model` (string,null)
    Host Model
    Example: "model_1"

  - `nvmeSubsystemNqn` (string,null)
    Subsystem NQN of NVMe/TCP hostpath
    Example: "nqn.2020-07.com.hpe:8ee43ce5-8264-4fcf-9990-a894f56386c7"

  - `pathType` (string,null)
    Path Type
    Example: "FC"

  - `portPos` (object,null)

  - `portPos.node` (integer,null)
    Node Port
    Example: 1

  - `portPos.port` (integer,null)
    Port
    Example: 1

  - `portPos.slot` (integer,null)
    Slot
    Example: 1

  - `resourceUri` (string,null)
    resourceUri for detailed hostpath object
    Example: "/v1/storage-systems/host-paths/dbce79b2612cde02a6e0be8934c330ec"

  - `scHostInitiatorId` (string,null)
    Host Service Initiator Id
    Example: "1223f5s"

  - `switchPortWwn` (string,null)
    Switch Port WWN
    Example: "5001438026e98a60"

  - `systemUid` (string)
    System Uid
    Example: "7CE727P35M"

  - `systemWwn` (string)
    System serial Number
    Example: "swK21"

  - `uri` (string,null)
    Uri
    Example: "/api/v3/hostpaths/dbce79b2612cde02a6e0be8934c330ec"

  - `vendor` (string,null)
    Vendor
    Example: "-"

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


