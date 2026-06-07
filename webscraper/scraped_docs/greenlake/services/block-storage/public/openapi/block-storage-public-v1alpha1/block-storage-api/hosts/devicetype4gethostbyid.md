---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hosts/{hostId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/block-storage-api/hosts/devicetype4gethostbyid.md"
scraped_at: "2026-06-07T06:14:32.808427+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Host identified by {HostId}

Get details of HPE Alletra Storage MP B10000 Host identified by {HostId}

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hosts/{hostId}
Version: 1.0.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `hostId` (string, required)
    ID of the HPE Alletra Storage MP B10000 Host Set. A 42 digit hexadecimal number.
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Host Resource UID
    Example: "132b493352ca3141456333edf403be0c"

  - `type` (string, required)
    Type of the resource

  - `agent` (object,null)
    HPE Alletra Storage MP B10000 Host Agent

  - `agent.architecture` (string,null)
    Architecture Name
    Example: "SAN"

  - `agent.bootFromSan` (string,null)
    Boot from SAN
    Example: "yes"

  - `agent.clusterName` (string,null)
    Cluster Cluster
    Example: "SAN-cluster"

  - `agent.clusterSoftware` (string,null)
    Cluster OS
    Example: "Linux"

  - `agent.clusterVersion` (string,null)
    Cluster Version
    Example: "v1.0.0"

  - `agent.hostApps` (string,null)
    Host Applications
    Example: "mysql"

  - `agent.ipAddr` (string,null)
    Ip Address
    Example: "10.15.12.136"

  - `agent.lastUpdated` (object,null)
    HPE Alletra Storage MP B10000 Host Agent

  - `agent.lastUpdated.ms` (integer,null)
    Epoch Time
    Example: 101780

  - `agent.lastUpdated.tz` (string,null)
    String Time
    Example: "123545"

  - `agent.multiPathSoftware` (string,null)
    Multipath Software
    Example: "OS"

  - `agent.multiPathSoftwareVersion` (string,null)
    MultiPath Software Version
    Example: "v1.0.0"

  - `agent.os` (string,null)
    Operating System Name
    Example: "Linux"

  - `agent.osPatch` (string,null)
    Os patch
    Example: "v1.0.0"

  - `agent.osVersion` (string,null)
    Os version
    Example: "v1.0.0"

  - `agent.reportedName` (string,null)
    Reported Name
    Example: "slvs"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the host resource belongs
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `descriptors` (object,null)
    Host Descriptors

  - `descriptors.comment` (string,null)
    Comment
    Example: "Comments"

  - `descriptors.contact` (string,null)
    Contact
    Example: "1234567788e"

  - `descriptors.location` (string,null)
    Location
    Example: "US"

  - `descriptors.model` (string,null)
    Model
    Example: "AIX"

  - `displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `domain` (string,null)
    Domain name of the Host
    Example: "slt"

  - `generation` (integer)
    Generation Time of the Resource
    Example: 1652172502

  - `hostId` (integer,null)
    Numeric ID of the resource
    Example: 101780

  - `initiatorChapEnabled` (boolean,null)
    Indicates if the Initiator Chap is enabled or not

  - `initiatorChapName` (string,null)
    Initiator Chap Name
    Example: "chapName"

  - `initiatorEncryptedChapSecret` (string,null)
    Initiator Encrypted Chap Secret
    Example: "secret"

  - `isNvmfStretched` (boolean,null)
    Indicates if this host is NVMe stretched.

  - `isVvolHost` (boolean,null)
    Indicates if this host is used to export VASA vVol over NVMe Protocol.

  - `minLunId` (integer,null)
    LUN Id of the host
    Example: 10

  - `name` (string,null)
    Host Name
    Example: "test-host"

  - `persona` (object,null)
    Host Persona

  - `persona.id` (string, required)
    ID of the resource

  - `persona.capabilities` (array,null)

  - `resourceUri` (string,null)
    Resoure Uri of the Host
    Example: "/api/v3/hosts/2492b4e84f7536577a38be78f0da0c1a"

  - `scHostId` (string,null)
    Host Service Host Id
    Example: "132b493352ca3141456333edf403be0c"

  - `state` (object,null)
    Host State

  - `state.detailed` (object,null)

  - `state.detailed.args` (array,null)
    system ntp addresses

  - `state.detailed.default` (string,null)
    Default Name
    Example: "Host sltestish"

  - `state.detailed.key` (string,null)
    Key of the Host Name
    Example: "HOST_NAME"

  - `state.detailed.localizedText` (string,null)
    Localized Text
    Example: "Localized text of the resource capabilities"

  - `state.overall` (string,null)
    Host State
    Example: "NORMAL"

  - `stateDescription` (array,null)

  - `stateVal` (integer,null)
    Health Status of the Host
    Example: 1

  - `systemUid` (string)
    Serial Number of the system
    Example: "swK21"

  - `systemWwn` (string)
    System wwn
    Example: "swK21"

  - `targetChapEnabled` (boolean,null)
    Indicates if the Target Chap is enabled or not

  - `targetChapName` (string,null)
    Target Chap Name
    Example: "sltest1"

  - `targetEncryptedChapSecret` (string,null)
    Target Encrypted Chap Secret
    Example: "Target Encrypted Chap Secret"

  - `uaRepLun` (boolean,null)
    Indicates if the UaRepLun is enabled or not

  - `uri` (string,null)
    Resoure Uri of the Host
    Example: "/api/v3/hosts/2492b4e84f7536577a38be78f0da0c1a"

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


