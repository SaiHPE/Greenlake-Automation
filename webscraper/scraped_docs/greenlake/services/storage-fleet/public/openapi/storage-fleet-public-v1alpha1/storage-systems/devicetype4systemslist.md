---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-systems/devicetype4systemslist.md"
scraped_at: "2026-06-07T06:15:59.572069+00:00Z"
---

# Get all HPE Alletra Storage MP B10000 storage systems

Get all HPE Alletra Storage MP B10000 storage systems

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems
Version: 1.2.0
Security: bearer

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    oData query to filter systems by Key.
    Example: "name eq VEGA_CB1507_8400_2N_150"

  - `sort` (string)
    Query to sort the response with specified key and order
    Example: "id asc,name desc"

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
    SystemWWN/UUID string uniquely identifying the storage system object. Filter
    Example: "7CE751P312"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.brandingInfo` (object,null)
    Branding information for HPE Alletra Storage MP B10000 devices. This is available in HPE Alletra Storage MP B10000 systems from 10.6.0 and later OS versions.

  - `items.brandingInfo.hwModel` (string,null)
    Hardware model name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage MP B10000"

  - `items.brandingInfo.hwProduct` (string,null)
    Hardware product name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage MP B10000"

  - `items.brandingInfo.hwProductFull` (string,null)
    Hardware product full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage MP B10000"

  - `items.brandingInfo.osFull` (string,null)
    OS full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage ArcusOS"

  - `items.brandingInfo.osName` (string,null)
    OS name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage ArcusOS"

  - `items.brandingInfo.product` (string,null)
    Product name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage MP B10000"

  - `items.brandingInfo.productFull` (string,null)
    Product full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage MP B10000"

  - `items.brandingInfo.productNoSpace` (string,null)
    Product name with no spaces for HPE Alletra Storage MP B10000 devices.
    Example: "HPE_Alletra_Storage"

  - `items.brandingInfo.softProduct` (string,null)
    Software product name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage"

  - `items.brandingInfo.softProductFull` (string,null)
    Software product full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage"

  - `items.brandingInfo.uiName` (string,null)
    UI name for HPE Alletra Storage MP B10000 devices.
    Example: "Alletra Storage UI"

  - `items.brandingInfo.uiNameFull` (string,null)
    UI full name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE Alletra Storage ui"

  - `items.brandingInfo.vendor` (string,null)
    Vendor name for HPE Alletra Storage MP B10000 devices.
    Example: "HPE"

  - `items.centerplaneType` (string,null)
    Centerplane type
    Example: "4 Node Centerplane"

  - `items.chunkletSizeMiB` (integer,null)
    Size of chunklet in MiB
    Example: 1024

  - `items.clusterLed` (string,null)
    Cluster LED state
    Enum: "LED_UNKNOWN", "LED_OFF", "LED_GREEN", "LED_GREEN_BLNK", "LED_AMBER", "LED_AMBER_BLNK", "LED_BLUE", "LED_BLUE_BLNK", null

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

  - `items.descriptors` (object,null)
    System descriptors

  - `items.descriptors.comment` (string,null)
    CommeUser-specified comment for the system

  - `items.descriptors.contact` (string,null)
    User-specified contact for the system
    Example: "First Last, 12345678, prabhakar.jasiwal@hpe.com"

  - `items.descriptors.location` (string,null)
    User-specified location of the system

  - `items.descriptors.owner` (string,null)
    User-specified owner for the system

  - `items.deviceId` (integer,null)
    Numeric ID of the resource Filter
    Example: 101780

  - `items.deviceType` (object,null)
    device Type

  - `items.deviceType.default` (string,null)
    Text in the default language
    Example: "HPE_3PAR 8450"

  - `items.deviceType.key` (string,null)
    Key of the message
    Example: "sys_type-41"

  - `items.displayname` (string,null)
    Array Display name
    Example: "System VEGA_CB1507_8400_2N_150"

  - `items.domain` (string,null)
    Domain that the resource belongs to

  - `items.fileServiceInfo` (object,null)

  - `items.fileServiceInfo.capacitySummary` (object,null)
    Capacity information for file service

  - `items.fileServiceInfo.capacitySummary.fileAvailableCapacityInMiB` (number)
    Capacity available for use by file service

  - `items.fileServiceInfo.capacitySummary.fileUsedCapacityInMiB` (number)
    Capacity used by file service

  - `items.fileServiceInfo.capacitySummary.totalSystemCapacityInMiB` (number)
    Capacity limit set for fileservice

  - `items.fileServiceInfo.defaultQoS` (object,null)
    Default file QOS values

  - `items.fileServiceInfo.defaultQoS.bwLimitInKiB` (integer)
    Default bandwidth limit in KiB

  - `items.fileServiceInfo.defaultQoS.iopsLimit` (integer)
    Default IOPS limit

  - `items.fileServiceInfo.fileServiceId` (string,null)
    ID of the file service

  - `items.fileServiceInfo.isFileCapable` (boolean,null)
    Indicates whether file services is supported in the system

  - `items.fileServiceInfo.isFileEnabled` (boolean,null)
    Indicates whether file service is enabled in the system

  - `items.fqdn` (string,null)
    Fully qualified domain name of the system
    Example: "s9.in.hpecorp.net"

  - `items.generation` (integer,null)
    generation Filter, Sort

  - `items.inClusterNodes` (array,null)
    IDs of the nodes that are in cluster
    Example: [0,1]

  - `items.locateEnabled` (boolean,null)
    Indicates if the locate beacon is enabled or not

  - `items.maintenanceMode` (array,null)
    Maintenance mode details of the system

  - `items.maintenanceMode.comment` (string,null)
    Comments

  - `items.maintenanceMode.endTime` (object,null)
    end time

  - `items.maintenanceMode.endTime.ms` (integer,null)
    stat time

  - `items.maintenanceMode.endTime.tz` (string,null)
    time zone

  - `items.maintenanceMode.instances` (integer,null)
    Instances

  - `items.maintenanceMode.reasonCode` (string,null)
    Reason code

  - `items.maintenanceMode.startTime` (object,null)
    start time

  - `items.maintenanceMode.startTime.ms` (integer,null)
    epoc time

  - `items.maintenanceMode.user` (string,null)
    User

  - `items.manufacturing` (object,null)
    Manufacturing information

  - `items.manufacturing.assemblyRev` (string,null)
    Assembly revision

  - `items.manufacturing.checkSum` (string,null)
    Checksum

  - `items.manufacturing.hpeModelName` (string,null)
    HPE model name

  - `items.manufacturing.manufacturer` (string,null)
    Manufacturer Filter
    Example: "HPE 3PAR"

  - `items.manufacturing.model` (string,null)
    Model Filter
    Example: "HPE_3PAR 8400"

  - `items.manufacturing.saleablePartNumber` (string,null)
    Saleable part number

  - `items.manufacturing.saleableSerialNumber` (string,null)
    Saleable serial number

  - `items.manufacturing.serialNumber` (string,null)
    Serial number Filter, Sort
    Example: "MXN5442108"

  - `items.manufacturing.sparePartNumber` (string,null)
    Spare part number

  - `items.masterNode` (integer,null)
    ID of the master node
    Example: 4

  - `items.minimumPasswordLength` (integer,null)
    Minimum length of password for users
    Example: 6

  - `items.name` (string,null)
    Name of the resource Filter, Sort
    Example: "VEGA_CB1507_8400_2N_150"

  - `items.networkMasterNode` (integer,null)
    The Node ID of the current network master Filter, Sort
    Example: 1

  - `items.nodeMemory` (string,null)
    Node memory size
    Example: "16"

  - `items.nodesCount` (integer,null)
    Number of nodes in the system
    Example: 2

  - `items.nodesPresent` (array,null)
    IDs of the nodes that are present
    Example: [0,1]

  - `items.onlineNodes` (array,null)
    IDs of the nodes that are online
    Example: [0,1]

  - `items.overallState` (string,null)
    overallState state derived from enclosure, disk and node state For deviceType1 State derived from ports, enclosure, disk and node state. For deviceType2 state is state reported by deviceType2 array. For deviceType4 state is derived from ports,enclosures,disks,nodes and enclosure-cards.
    Enum: "NORMAL", "DEGRADED", null

  - `items.overallStateDescription` (string,null)
    Information of hardware resources that are in degraded state.
    Example: "Degraded Resources: disks, nodes"

  - `items.resourceUri` (string,null)
    resourceUri for detailed storage object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312"

  - `items.safeToRemove` (boolean,null)
    Indicates if the component is safe to remove

  - `items.softwareVersions` (object,null)
    Software versions of the product

  - `items.softwareVersions.baseVersion` (string,null)
    Base Version Filter
    Example: "4.2.0"

  - `items.softwareVersions.components` (array,null)

  - `items.softwareVersions.components.baseVersion` (string,null)
    Base Version
    Example: "4.2.0.48"

  - `items.softwareVersions.components.fullVersion` (string,null)
    Full Version
    Example: "4.2.0.48"

  - `items.softwareVersions.components.name` (string,null)
    Name of the Component
    Example: "CLI Server"

  - `items.softwareVersions.components.release` (string,null)
    Release Version

  - `items.softwareVersions.components.showLevel` (integer,null)
    Show Level
    Example: 1

  - `items.softwareVersions.patches` (string,null)
    Set of Patches Filter

  - `items.state` (object,null)
    State of the resource

  - `items.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.sysLogStatus` (object,null)
    Remote syslog details of the system

  - `items.sysLogStatus.general` (string,null)
    General
    Example: "None,None,None"

  - `items.sysLogStatus.security` (string,null)
    Security
    Example: "None,None,None"

  - `items.systemDate` (integer,null)
    Current date of the system
    Example: 1597918380

  - `items.systemHeadroom` (object)
    Headroom for the storage-system

  - `items.systemHeadroom.performanceHeadroom` (object)
    System performance Headroom

  - `items.systemHeadroom.performanceHeadroom.availableHeadroom` (string)
    Available Headroom on the systems (High Medium or Low)
    Example: "Low"

  - `items.systemHeadroom.performanceHeadroom.headroomUtilization` (string)
    Headroom Utilization on the systems (High Medium or Low)
    Example: "Low"

  - `items.systemHeadroom.performanceHeadroom.utilization` (number)
    Utilization in percentage
    Example: 10

  - `items.systemWwn` (string,null)
    WWN of the array Filter, Sort
    Example: "2FF70002AC018D94"

  - `items.timezone` (string,null)
    Current timezone of the system
    Example: "Asia/Calcutta"

  - `items.uptime` (object,null)
    The time that the system has been up since

  - `items.uptime.ms` (integer,null)
    Epoch time in milliseconds
    Example: 123423423

  - `items.uptime.tz` (string,null)
    Time zone name
    Example: "IST"

  - `items.version` (object,null)

  - `items.version.base` (string,null)
    Base version
    Example: "4.2.0"

  - `items.version.display` (string,null)
    Display name
    Example: "4.2.0"

  - `items.version.full` (string,null)
    Full version
    Example: "4.2.0.48"

  - `items.version.fullWithoutPatches` (string,null)
    Base version without patches
    Example: "4.2.0.48"

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


