---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4storagecontainerget.md"
scraped_at: "2026-06-07T06:16:06.595976+00:00Z"
---

# Get Storage Container details for an HPE Alletra Storage MP B10000 storage system

Get Storage Container details for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs
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
    oData query to filter by Key.
    Example: "name eq array1 and wwn eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort by Key.
    Example: "systemWWN desc"

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
    UID of the storage container
    Example: "fc5f41652a53497e88cdcebc715cc1xz"

  - `items.type` (string, required)
    type of the resource
    Example: "storage Container"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.autoDissmissed` (integer,null)
    name of the resource
    Example: 3

  - `items.comment` (string,null)
    comments
    Example: "v1 is a storage container"

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

  - `items.creationTime` (object,null)
    Creation Time

  - `items.creationTime.ms` (integer,null)

  - `items.creationTime.tz` (string,null)

  - `items.customerId` (string,null)
    customerId
    Example: "fafafaefu987823hfa"

  - `items.displayName` (string,null)
    Name to be used for display purposes
    Example: "Storage Container"

  - `items.domain` (string,null)
    domain of the storage container
    Example: "Domain"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627538867363

  - `items.growthLimitMiB` (number,null)
    Indicates that the auto-grow operation is limited to the specified storage amount.
    Example: 12

  - `items.growthSizeMiB` (number,null)
    Indicates the growth increment size, the amount of logical disk storage created on each auto-grow operation.
    Example: 123

  - `items.growthWarnMiB` (number,null)
    Indicates that the threshold of used logical disk space, when exceeded, results in a warning alert.
    Example: 46

  - `items.hostGroups` (array,null)
    Hosts

  - `items.hostGroups.id` (string, required)
    uid
    Example: "Uid"

  - `items.hostGroups.hosts` (array,null)
    Hosts

  - `items.hostGroups.hosts.name` (string,null)
    name
    Example: "Name"

  - `items.hostGroups.hosts.userCreated` (boolean,null)
    Indicates whether host created by user through Data Services Cloud Console or not
    Example: true

  - `items.hostGroups.userCreated` (boolean,null)
    Indicates whether host group created by user through Data Services Cloud Console or not
    Example: true

  - `items.hostList` (array,null)
    vVols storage container host list

  - `items.inUseMiB` (integer,null)
    space used by the storage container
    Example: 243

  - `items.name` (string,null)
    name of the resource
    Example: "vvolsc1"

  - `items.numOfVms` (integer,null)
    no. of VMs in storage container
    Example: 3

  - `items.numOfVvols` (integer,null)
    no. of vVols in storage container
    Example: 6

  - `items.pevvs` (array,null)
    vVols storage container PEVV list

  - `items.provisionedMiB` (integer,null)
    provisioned size of storage container
    Example: 23

  - `items.resourceUri` (string)
    resourceUri for detailed snmpUsers object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/vvolscs/9c3c4f29a82fd8d632ff379116fa0b8f"

  - `items.scId` (integer,null)
    ID of the storage container
    Example: 56

  - `items.scType` (string,null)
    The type of the storage container.
    Example: "SCSI"

  - `items.scUuid` (string,null)
    sc_uuid of storage container
    Example: "fc5f41652a53497e88cdcebc715cc1xz"

  - `items.systemId` (string,null)
    systemId of the resource
    Example: "7CE751P312"

  - `items.systemWwn` (string,null)
    systemWWN of the resource
    Example: "4UW001500"

  - `items.totalMiB` (integer,null)
    name of the resource
    Example: 458

  - `items.transportType` (string,null)
    Transport Type of the host attached to storage container. Valid values are FC, iSCSI, NVMe/FC and NVMe/TCP.
    Example: "FC"

  - `items.uri` (string,null)
    uri for the storage container
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/vvolscs"

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


