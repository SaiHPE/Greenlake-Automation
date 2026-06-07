---
title: "GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hosts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/hosts/devicetype4getallhosts.md"
scraped_at: "2026-06-07T06:14:24.226069+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Hosts

Get details of HPE Alletra Storage MP B10000 Hosts

Endpoint: GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/hosts
Version: 1.0.0
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
    Lucene query to filter host by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004817"

  - `sort` (string)
    oData query to sort host resource by Key.
    Example: "HostSpeed desc"

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
    Host Resource UID Filter
    Example: "132b493352ca3141456333edf403be0c"

  - `items.type` (string, required)
    type of the resource

  - `items.agent` (object,null)
    HPE Alletra Storage MP B10000 Host Agent

  - `items.agent.architecture` (string,null)
    Architecture Name
    Example: "SAN"

  - `items.agent.bootFromSan` (string,null)
    Boot from SAN
    Example: "yes"

  - `items.agent.clusterName` (string,null)
    Cluster Cluster
    Example: "SAN-cluster"

  - `items.agent.clusterSoftware` (string,null)
    Cluster OS
    Example: "Linux"

  - `items.agent.clusterVersion` (string,null)
    Cluster Version
    Example: "v1.0.0"

  - `items.agent.hostApps` (string,null)
    Host Applications
    Example: "mysql"

  - `items.agent.ipAddr` (string,null)
    Ip Address
    Example: "10.15.12.136"

  - `items.agent.lastUpdated` (object,null)
    HPE Alletra Storage MP B10000 Host Agent

  - `items.agent.lastUpdated.ms` (integer,null)
    Epoch Time
    Example: 101780

  - `items.agent.lastUpdated.tz` (string,null)
    String Time
    Example: "123545"

  - `items.agent.multiPathSoftware` (string,null)
    Multipath Software
    Example: "OS"

  - `items.agent.multiPathSoftwareVersion` (string,null)
    MultiPath Software Version
    Example: "v1.0.0"

  - `items.agent.os` (string,null)
    Operating System Name
    Example: "Linux"

  - `items.agent.osPatch` (string,null)
    Os patch
    Example: "v1.0.0"

  - `items.agent.osVersion` (string,null)
    Os version
    Example: "v1.0.0"

  - `items.agent.reportedName` (string,null)
    Reported Name
    Example: "slvs"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the host resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.descriptors` (object,null)
    Host Descriptors

  - `items.descriptors.comment` (string,null)
    Comment
    Example: "Comments"

  - `items.descriptors.contact` (string,null)
    Contact
    Example: "1234567788e"

  - `items.descriptors.location` (string,null)
    Location
    Example: "US"

  - `items.descriptors.model` (string,null)
    Model
    Example: "AIX"

  - `items.displayname` (string,null)
    Name to be used for display purposes
    Example: "Drive 0.SIDE_NONE.2.0"

  - `items.domain` (string,null)
    Domain name of the Host
    Example: "slt"

  - `items.generation` (integer)
    Generation Time of the Resource Filter, Sort
    Example: 1652172502

  - `items.hostId` (integer,null)
    Numeric ID of the resource
    Example: 101780

  - `items.initiatorChapEnabled` (boolean,null)
    Indicates if the Initiator Chap is enabled or not

  - `items.initiatorChapName` (string,null)
    Initiator Chap Name
    Example: "chapName"

  - `items.initiatorEncryptedChapSecret` (string,null)
    Initiator Encrypted Chap Secret
    Example: "secret"

  - `items.isNvmfStretched` (boolean,null)
    Indicates if this host is NVMe stretched.

  - `items.isVvolHost` (boolean,null)
    Indicates if this host is used to export VASA vVol over NVMe Protocol.

  - `items.minLunId` (integer,null)
    LUN Id of the host
    Example: 10

  - `items.name` (string,null)
    Host Name Filter, Sort
    Example: "test-host"

  - `items.persona` (object,null)
    Host Persona

  - `items.persona.id` (string, required)
    ID of the resource

  - `items.persona.capabilities` (array,null)

  - `items.persona.name` (string,null)
    Host Name
    Example: "test-host"

  - `items.resourceUri` (string,null)
    Resoure Uri of the Host
    Example: "/api/v3/hosts/2492b4e84f7536577a38be78f0da0c1a"

  - `items.scHostId` (string,null)
    Host Service Host Id Filter
    Example: "132b493352ca3141456333edf403be0c"

  - `items.state` (object,null)
    Host State

  - `items.state.detailed` (object,null)

  - `items.state.detailed.args` (array,null)
    system ntp addresses

  - `items.state.detailed.default` (string,null)
    Default Name
    Example: "Host sltestish"

  - `items.state.detailed.key` (string,null)
    Key of the Host Name
    Example: "HOST_NAME"

  - `items.state.detailed.localizedText` (string,null)
    Localized Text
    Example: "Localized text of the resource capabilities"

  - `items.state.overall` (string,null)
    Host State
    Example: "NORMAL"

  - `items.stateDescription` (array,null)

  - `items.stateVal` (integer,null)
    Health Status of the Host
    Example: 1

  - `items.systemUid` (string)
    Serial Number of the system Filter
    Example: "swK21"

  - `items.systemWwn` (string)
    System wwn Filter, Sort
    Example: "swK21"

  - `items.targetChapEnabled` (boolean,null)
    Indicates if the Target Chap is enabled or not

  - `items.targetChapName` (string,null)
    Target Chap Name
    Example: "sltest1"

  - `items.targetEncryptedChapSecret` (string,null)
    Target Encrypted Chap Secret
    Example: "Target Encrypted Chap Secret"

  - `items.uaRepLun` (boolean,null)
    Indicates if the UaRepLun is enabled or not

  - `items.uri` (string,null)
    Resoure Uri of the Host
    Example: "/api/v3/hosts/2492b4e84f7536577a38be78f0da0c1a"

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


