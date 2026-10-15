---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-systems/devicetype4systemgetbyid.md"
scraped_at: "2026-06-07T06:15:59.490419+00:00Z"
---

# Get HPE Alletra Storage MP B10000 object identified by {id}

Get HPE Alletra Storage MP B10000 object identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    Serial number of the device-type4 storage system
    Example: "SGH029VBHV"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    SerialNumber/UUID string uniquely identifying the storage system object.
    Example: "7CE751P312"

  - `type` (string, required)
    type
    Example: "string"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `brandingInfo` (object,null)
    Branding information for HPE Alletra Storage MP B10000 devices. This is available in HPE Alletra Storage MP B10000 systems from 10.6.0 and later OS versions.

  - `brandingInfo.hwModel` (string,null)
    Hardware model name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage MP B10000"

  - `brandingInfo.hwProduct` (string,null)
    Hardware product name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage MP B10000"

  - `brandingInfo.hwProductFull` (string,null)
    Hardware product full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage MP B10000"

  - `brandingInfo.osFull` (string,null)
    OS full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage ArcusOS"

  - `brandingInfo.osName` (string,null)
    OS name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage ArcusOS"

  - `brandingInfo.product` (string,null)
    Product name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage MP B10000"

  - `brandingInfo.productFull` (string,null)
    Product full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage MP B10000"

  - `brandingInfo.productNoSpace` (string,null)
    Product name with no spaces for HPE Alletra Storage MP B10000 devices.
    Example: "HPE_Alletra_Storage"

  - `brandingInfo.softProduct` (string,null)
    Software product name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage"

  - `brandingInfo.softProductFull` (string,null)
    Software product full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage"

  - `brandingInfo.uiName` (string,null)
    UI name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage UI"

  - `brandingInfo.uiNameFull` (string,null)
    UI full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage ui"

  - `brandingInfo.vendor` (string,null)
    Vendor name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE"

  - `centerplaneType` (string,null)
    Centerplane type
    Example: "4 Node Centerplane"

  - `chunkletSizeMiB` (integer,null)
    Size of chunklet in MiB
    Example: 1024

  - `clusterLed` (string)
    Cluster LED state
    Enum: "LED_UNKNOWN", "LED_OFF", "LED_GREEN", "LED_GREEN_BLNK", "LED_AMBER", "LED_AMBER_BLNK", "LED_BLUE", "LED_BLUE_BLNK"

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
    Example: "string"

  - `descriptors` (object,null)
    System descriptors

  - `descriptors.comment` (string,null)
    CommeUser-specified comment for the system

  - `descriptors.contact` (string,null)
    User-specified contact for the system
    Example: "First Last, 12345678, prabhakar.jasiwal@hpe.com"

  - `descriptors.location` (string,null)
    User-specified location of the system

  - `descriptors.owner` (string,null)
    User-specified owner for the system

  - `deviceId` (integer,null)
    Numeric ID of the resource
    Example: 101780

  - `deviceType` (object,null)
    device Type

  - `deviceType.default` (string,null)
    Text in the default language
    Example: "HPE_3PAR 8450"

  - `deviceType.key` (string,null)
    Key of the message
    Example: "sys_type-41"

  - `displayname` (string,null)
    Array Display name
    Example: "System VEGA_CB1507_8400_2N_150"

  - `domain` (string,null)
    Domain that the resource belongs to

  - `fileServiceInfo` (object,null)

  - `fileServiceInfo.capacitySummary` (object,null)
    Capacity information for file service

  - `fileServiceInfo.capacitySummary.fileAvailableCapacityInMiB` (number)
    Capacity available for use by file service

  - `fileServiceInfo.capacitySummary.fileUsedCapacityInMiB` (number)
    Capacity used by file service

  - `fileServiceInfo.capacitySummary.totalSystemCapacityInMiB` (number)
    Total system capacity

  - `fileServiceInfo.defaultQoS` (object,null)
    Default file QoS values

  - `fileServiceInfo.defaultQoS.bwLimitInKiB` (integer)
    Default bandwidth limit in KiB

  - `fileServiceInfo.defaultQoS.iopsLimit` (integer)
    Default IOPS limit

  - `fileServiceInfo.fileServiceId` (string,null)
    ID of the file service

  - `fileServiceInfo.isFileCapable` (boolean,null)
    Indicates whether file services is supported in the system

  - `fileServiceInfo.isFileEnabled` (boolean,null)
    Indicates whether file service is enabled in the system

  - `fqdn` (string,null)
    Fully qualified domain name of the system
    Example: "s9.in.hpecorp.net"

  - `generation` (integer,null)
    generation

  - `inClusterNodes` (array,null)
    IDs of the nodes that are in cluster
    Example: [0,1]

  - `locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `maintenanceMode` (array,null)
    Maintenance mode details of the system

  - `maintenanceMode.comment` (string,null)
    Comments

  - `maintenanceMode.endTime` (object,null)
    end time

  - `maintenanceMode.endTime.ms` (integer,null)
    stat time

  - `maintenanceMode.endTime.tz` (string,null)
    time zone

  - `maintenanceMode.instances` (integer,null)
    Instances

  - `maintenanceMode.reasonCode` (string,null)
    Reason code

  - `maintenanceMode.startTime` (object,null)
    start time

  - `maintenanceMode.startTime.ms` (integer,null)
    epoc time

  - `maintenanceMode.user` (string,null)
    User

  - `manufacturing` (object,null)
    Manufacturing information

  - `manufacturing.assemblyRev` (string,null)
    Assembly revision
    Example: "002*"

  - `manufacturing.checkSum` (string,null)
    Checksum
    Example: "--"

  - `manufacturing.hpeModelName` (string,null)
    HPE model name
    Example: "HPE 3PAR 600 2S Node"

  - `manufacturing.manufacturer` (string,null)
    Manufacturer.
    Example: "XYRATEX"

  - `manufacturing.model` (string,null)
    Model
    Example: "0974244-06"

  - `manufacturing.saleablePartNumber` (string,null)
    Saleable part number
    Example: "0974244-06"

  - `manufacturing.saleableSerialNumber` (string,null)
    Saleable serial number
    Example: "4UW0002941"

  - `manufacturing.serialNumber` (string,null)
    Serial number.
    Example: "PMW0974244G4T88"

  - `manufacturing.sparePartNumber` (string,null)
    Spare part number
    Example: "P04031-001"

  - `masterNode` (integer,null)
    ID of the master node
    Example: 4

  - `minimumPasswordLength` (integer,null)
    Minimum length of password for users
    Example: 6

  - `name` (string,null)
    Name of the resource
    Example: "VEGA_CB1507_8400_2N_150"

  - `networkMasterNode` (integer,null)
    The Node ID of the current network master
    Example: 1

  - `nodeMemory` (string,null)
    Node memory size
    Example: "16"

  - `nodesCount` (integer,null)
    Number of nodes in the system
    Example: 2

  - `nodesPresent` (array,null)
    IDs of the nodes that are present
    Example: [0,1]

  - `onlineNodes` (array,null)
    IDs of the nodes that are online
    Example: [0,1]

  - `overallState` (string,null)
    overallState is derived from ports,enclosures,disks,nodes and enclosure-cards.
    Enum: "NORMAL", "DEGRADED", null

  - `overallStateDescription` (string,null)
    Information of hardware resources that are in degraded state.
    Example: "Degraded Resources: disks, nodes"

  - `resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312"

  - `safeToRemove` (boolean,null)
    Indicates if the component is safe to remove

  - `softwareVersions` (object,null)
    Software versions of the product

  - `softwareVersions.baseVersion` (string,null)
    Base Version
    Example: "4.2.0"

  - `softwareVersions.components` (array,null)

  - `softwareVersions.components.fullVersion` (string,null)
    Full Version
    Example: "4.2.0.48"

  - `softwareVersions.components.name` (string,null)
    Name of the Component
    Example: "CLI Server"

  - `softwareVersions.components.release` (string,null)
    Release Version

  - `softwareVersions.components.showLevel` (integer,null)
    Level information of the component
    Example: 1

  - `softwareVersions.patches` (string,null)
    Set of Patches

  - `state` (object,null)
    State of the resource

  - `state.detailed` (array,null)
    Array of the detailed states of the resource

  - `state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `sysLogStatus` (object,null)
    Remote syslog details of the system

  - `sysLogStatus.general` (string,null)
    General
    Example: "None,None,None"

  - `sysLogStatus.security` (string,null)
    Security
    Example: "None,None,None"

  - `systemDate` (integer,null)
    Current date of the system
    Example: 1597918380

  - `systemHeadroom` (object)
    Headroom for the storage-system

  - `systemHeadroom.performanceHeadroom` (object)
    System performance Headroom

  - `systemHeadroom.performanceHeadroom.availableHeadroom` (string)
    Available Headroom on the systems (High Medium or Low)
    Example: "Low"

  - `systemHeadroom.performanceHeadroom.headroomUtilization` (string)
    Headroom Utilization on the systems (High Medium or Low)
    Example: "Low"

  - `systemHeadroom.performanceHeadroom.utilization` (number)
    Utilization in percentage
    Example: 10

  - `systemWwn` (string,null)
    WWN of the array.
    Example: "2FF70002AC018D94"

  - `timezone` (string,null)
    Current timezone of the system.
    Example: "Asia/Calcutta"

  - `uptime` (object,null)
    The time that the system has been up since

  - `uptime.ms` (integer,null)
    Epoch time in milliseconds
    Example: 123423423

  - `uptime.tz` (string,null)
    Time zone name
    Example: "IST"

  - `version` (object,null)

  - `version.base` (string,null)
    Base version
    Example: "4.2.0"

  - `version.display` (string,null)
    Display name
    Example: "4.2.0"

  - `version.full` (string,null)
    Full version
    Example: "4.2.0.48"

  - `version.fullWithoutPatches` (string,null)
    Base version without patches
    Example: "4.2.0.48"

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
