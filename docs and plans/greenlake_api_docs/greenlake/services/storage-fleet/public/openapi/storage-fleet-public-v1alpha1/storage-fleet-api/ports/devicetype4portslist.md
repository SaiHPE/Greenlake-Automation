---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4portslist.md"
scraped_at: "2026-06-07T06:16:10.147865+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Ports

Get details of HPE Alletra Storage MP B10000 Ports

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports
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
    oData query to filter ports by Key.
    Example: "name eq 1:0:1 and systemWWN eq 2FF70002AC018D94"

  - `sort` (string)
    oData query to sort ports by Key.
    Example: "name desc"

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
    Unique Identifier of the resource Filter
    Example: "9d765763116c20a508e8996f2a10821d"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.associatedLinks` (array)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.cardType` (object,null)
    Type of the PCI card this port is on

  - `items.cardType.default` (string,null)

  - `items.cardType.key` (string,null)

  - `items.class` (integer,null)
    Fibre Channel class (can be either 2 or 3)

  - `items.class2` (string,null)
    Class2 state and configuration

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

  - `items.config` (string,null)
    Configuration state of port
    Example: "valid"

  - `items.configMode` (string,null)
    Connection mode of the port

  - `items.connectionType` (string,null)
    port connection type

  - `items.customerId` (string,null)
    customerId
    Example: "string"

  - `items.devices` (array,null)

  - `items.devices.device` (string,null)
    Type of the device. This is applicable for HPE Alletra Storage MP B10000 10.5.50 OS version and above.

  - `items.devices.name` (string,null)
    Name of the device

  - `items.devices.port` (integer,null)
    Port of the device. This is applicable for HPE Alletra Storage MP B10000 10.5.50 OS version and above.

  - `items.devices.position` (integer,null)
    Position of the device

  - `items.devices.slot` (integer,null)
    Slot of the device. This is applicable for HPE Alletra Storage MP B10000 10.5.50 OS version and above.

  - `items.displayname` (string,null)
    Name to be used for display purposes

  - `items.domain` (string,null)
    Domain that the resource belongs to

  - `items.enclosureCardId` (integer,null)
    ID of the enclosure card

  - `items.enclosureCardPciUid` (string,null)
    UID of the enclosure card PCI card

  - `items.enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card

  - `items.enclosureId` (integer,null)
    ID of the enclosure

  - `items.enclosureUid` (string,null)
    Unique Identifier of the enclosure Filter

  - `items.fcData` (object,null)

  - `items.fcData.nodeWwn` (string,null)
    nodeWWN of the FC port

  - `items.fcData.portWwn` (string,null)
    portWWN of the FC port

  - `items.fileData` (object,null)

  - `items.fileData.failoverIps` (string,null)
    Failover IP details of the File port

  - `items.fileData.ipDisabled` (boolean,null)
    Indicates if the port IP is disabled or not

  - `items.fileData.linkState` (string,null)
    Link State of the File port

  - `items.fileData.prefixLength` (integer,null)
    Prefix length of the File port

  - `items.fileData.vlanId` (integer,null)
    VLAN id for the File port

  - `items.fwVersion` (string,null)
    Firmware version
    Example: "12.2.396.1"

  - `items.generation` (integer,null)
    generation

  - `items.hostVirtualPorts` (array,null)

  - `items.hostVirtualPorts.nodeWwn` (string)
    Node WWN of the virtual port

  - `items.hostVirtualPorts.portLinkState` (string)
    Port link state
    Enum: "LINK_STATE_CONFIG_WAIT", "LINK_STATE_ALPA_WAIT", "LINK_STATE_LOGIN_WAIT", "LINK_STATE_READY", "LINK_STATE_LOSS_SYNC", "LINK_STATE_ERROR", "LINK_STATE_XXX", "LINK_STATE_NONPARTICIPATE", "LINK_STATE_COREDUMP", "LINK_STATE_OFFLINE", "LINK_STATE_FWDEAD", "LINK_STATE_LINK_IDLE_FOR_RESET", "LINK_STATE_DHCP_IN_PROGRESS", "LINK_STATE_PENDING_RESET", "LINK_STATE_UNKNOWN"

  - `items.hostVirtualPorts.portType` (string)
    Virtual port type
    Enum: "PORT_TYPE_FREE", "PORT_TYPE_HOST", "PORT_TYPE_DISK", "PORT_TYPE_IPORT", "PORT_TYPE_RCFC", "PORT_TYPE_RCIP", "PORT_TYPE_ISCSI", "PORT_TYPE_PEER", "PORT_TYPE_CNA", "PORT_TYPE_FS", "PORT_TYPE_UNKNOWN"

  - `items.hostVirtualPorts.portWwn` (string)
    Port WWN of the virtual port

  - `items.hostVirtualPorts.protocol` (string)
    Protocol of the Virtual port
    Enum: "PORT_PROTOCOL_UNKNOWN", "PORT_PROTOCOL_FC", "PORT_PROTOCOL_ISCSCI", "PORT_PROTOCOL_FCOE", "PORT_PROTOCOL_IP", "PORT_PROTOCOL_SAS", "PORT_PROTOCOL_NVME"

  - `items.hostVirtualPorts.vpi` (integer)
    Virtual port index

  - `items.interruptCoalesce` (string,null)
    Interrupt Coalesce

  - `items.ipData` (object,null)

  - `items.ipData.autoneg` (boolean,null)
    Auto negotiation state of IP port

  - `items.ipData.delimitedMacAddress` (string,null)
    MAC address of the IP port

  - `items.ipData.duplex` (string,null)
    Duplex state of IP port

  - `items.ipData.gatewayAddress` (string,null)
    Gateway Address of IP port

  - `items.ipData.gatewayAddressV6` (string,null)
    Gateway Address of IP port

  - `items.ipData.ipAddress` (string,null)
    IP address of IP port

  - `items.ipData.ipAddressV6` (string,null)
    IP address of IP port

  - `items.ipData.macAddress` (string,null)
    IP address of IP port

  - `items.ipData.mtu` (string,null)
    Maximum transmission unit (MTU) size

  - `items.ipData.subnetMask` (string,null)
    NetMask of IP port

  - `items.ipData.subnetMaskV6` (string,null)
    NetMask of IP port

  - `items.iscsiData` (object,null)

  - `items.iscsiData.delimitedMacAddress` (string,null)
    MAC address of the iSCSI port

  - `items.iscsiData.ethernetFlowControl` (string,null)
    Flow control setting of the port. Applicable for HPE Alletra Storage MP B10000 10.5.0 OS version and above. Possible values are "None", "DCBX=IEEE", "DCBX=IEEE PFC=Off" and "EthPause".

  - `items.iscsiData.gatewayAddress` (string,null)
    Gateway Address of iSCSI port

  - `items.iscsiData.gatewayAddressV6` (string,null)
    Gateway Address of iSCSI port.

  - `items.iscsiData.ipAddress` (string,null)
    IP address of iSCSI port

  - `items.iscsiData.ipAddressV6` (string,null)
    IPv6 address of iSCSI port.

  - `items.iscsiData.iscsiName` (string,null)
    iSCSI name of iSCSI port

  - `items.iscsiData.isnsPrimaryAddress` (string,null)
    Primary iSNS address

  - `items.iscsiData.isnsTcpPort` (integer,null)
    iSNS TCP port

  - `items.iscsiData.macAddress` (string,null)
    IP address of iSCSI port

  - `items.iscsiData.peerEnabled` (boolean,null)
    Indicates if the port is peer enabled

  - `items.iscsiData.sendTargetGroupTag` (integer,null)
    Send target group of the iSCSI port

  - `items.iscsiData.subnetMask` (string,null)
    NetMask of iSCSI port

  - `items.iscsiData.subnetMaskV6` (string,null)
    Netmask of iSCSI port.

  - `items.iscsiData.supportsVlan` (boolean,null)
    Indicates if the port support VLAN

  - `items.iscsiData.targetPortalGroupTag` (integer,null)
    Target portal group of the iSCSI port

  - `items.label` (string,null)
    Label Filter, Sort
    Example: "IP0"

  - `items.manufacturing` (object,null)
    Manufacturing information

  - `items.manufacturing.assemblyRev` (string,null)
    Assembly revision
    Example: "002*"

  - `items.manufacturing.checkSum` (string,null)
    Checksum
    Example: "--"

  - `items.manufacturing.hpeModelName` (string,null)
    HPE model name
    Example: "HPE 3PAR 600 2S Node"

  - `items.manufacturing.manufacturer` (string,null)
    Manufacturer.
    Example: "XYRATEX"

  - `items.manufacturing.model` (string,null)
    Model
    Example: "0974244-06"

  - `items.manufacturing.saleablePartNumber` (string,null)
    Saleable part number
    Example: "0974244-06"

  - `items.manufacturing.saleableSerialNumber` (string,null)
    Saleable serial number
    Example: "4UW0002941"

  - `items.manufacturing.serialNumber` (string,null)
    Serial number.
    Example: "PMW0974244G4T88"

  - `items.manufacturing.sparePartNumber` (string,null)
    Spare part number
    Example: "P04031-001"

  - `items.mode` (string,null)
    Current mode the port is in Filter, Sort

  - `items.modeChange` (string,null)
    Indicates if the mode change is allowed or prohibited

  - `items.name` (string,null)
    Name of the resource Filter, Sort

  - `items.nodeId` (string,null)
    Unique Identifier of the node Filter
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `items.nvmeData` (object,null)

  - `items.nvmeData.delimitedMacAddress` (string,null)
    MAC address of the NVMe port

  - `items.nvmeData.eth` (string,null)
    Ethernet name used by the NVMe port

  - `items.nvmeData.gatewayAddress` (string,null)
    Gateway of the NVMe port

  - `items.nvmeData.gatewayAddressV6` (string,null)
    Gateway address for the NVMe port.
    Example: "FE80::1"

  - `items.nvmeData.ipAddress` (string,null)
    IP address of the NVMe port

  - `items.nvmeData.ipAddressV6` (string,null)
    IPV6 address for the NVMe port.
    Example: "2001:db8:abcd:12:ffff:ffff:ffff:ff16"

  - `items.nvmeData.macAddress` (string,null)
    MAC address of the NVMe port

  - `items.nvmeData.mode` (string)
    Current mode the port is in

  - `items.nvmeData.nqn` (string,null)
    NVMe qualified name of the NVMe port

  - `items.nvmeData.pcidev` (string,null)
    PCI device used by the NVMe port

  - `items.nvmeData.prefixLength` (integer,null)
    Prefix Length of the NVMe port

  - `items.nvmeData.prefixLengthV6` (integer,null)
    Prefix length of the NVMe port.
    Example: 13

  - `items.nvmeData.protocol` (string)
    Current protocol the port is in

  - `items.nvmeData.rate` (string)
    Configured speed of the NVMe port

  - `items.nvmeData.state` (string,null)
    State of the resource

  - `items.nvmeData.transport` (object,null)
    Transport type of the NVMe port.

  - `items.nvmeData.vlanCount` (integer,null)
    Number of configured VLANs on this NVMe port

  - `items.nvmeData.vlans` (array,null)

  - `items.nvmeData.vlans.ethernetFlowControl` (string,null)
    Flow control setting of the NVMe port. Applicable for HPE Alletra Storage MP B10000 10.5.0 OS version and above. Possible values are "None", "DCBX=IEEE", "DCBX=IEEE PFC=Off" and "EthPause".

  - `items.nvmeData.vlans.gatewayAddress` (string,null)
    VLAN Gateway address for the NVMe port

  - `items.nvmeData.vlans.gatewayAddressV6` (string,null)
    Gateway address for the NVMe port. If Vlan is configured, then this is Vlan gateway address of this port.
    Example: "FE80::1"

  - `items.nvmeData.vlans.ipAddress` (string,null)
    VLAN IP address for the NVMe port

  - `items.nvmeData.vlans.ipAddressV6` (string,null)
    IPV6 address for the NVMe port. If Vlan is configured, then this is Vlan IPV6 address of this port.
    Example: "2001:db8:abcd:12:ffff:ffff:ffff:ff16"

  - `items.nvmeData.vlans.prefixLength` (integer,null)
    Prefix length of the NVMe port

  - `items.nvmeData.vlans.vlanId` (string,null)
    VLAN id for the NVMe port

  - `items.partner` (object,null)

  - `items.partner.nodeWwnOrName` (string,null)
    Node WWN (for FC) or iSCSI name (for iSCSI)  Filter, Sort

  - `items.partner.portWwnOrIp` (string,null)
    Port WWN (for FC) or IP address (for iSCSI)  Filter, Sort

  - `items.partner.position` (object,null)

  - `items.partner.position.node` (integer,null)
    Port position node number

  - `items.partner.position.port` (integer,null)
    Port position port number

  - `items.partner.position.slot` (integer,null)
    Port position slot number

  - `items.portSfp` (object,null)

  - `items.portSfp.qualified` (boolean,null)
    Indicates if the SFP is qualified or not

  - `items.portSfp.rxLossPin` (object,null)
    RX loss pin position. If position is HI, RX loss of signal

  - `items.portSfp.rxPowerLow` (boolean,null)
    Indicates if RX power is low or not

  - `items.portSfp.speed` (integer,null)
    Speed in bits per second

  - `items.portSfp.supportDdm` (boolean,null)
    Indicates if the SFP supports DDM

  - `items.portSfp.txDisablePin` (object,null)
    TX disable pin position. If position is HI, TX laser is disabled

  - `items.portSfp.txFaultPin` (object,null)
    TX fault pin position. If position is HI, TX fault

  - `items.portType` (string,null)
    Type of the port based on the device it is connected to Filter, Sort

  - `items.protocol` (string,null)
    Current protocol the port is in Filter, Sort

  - `items.resourceUri` (string,null)
    resourceUri for detailed port object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/ports/220fcd48857f63c0f354c6723ec5d5cb"

  - `items.revision` (string,null)
    Revision of the Host Bus Adapter

  - `items.smartSan` (string,null)
    Smart SAN status

  - `items.speedActual` (string,null)
    Actual speed that port is running at  Filter

  - `items.speedConfigured` (string,null)
    Speed that is configured to run as

  - `items.speedMax` (string,null)
    Maximum speed that port can run at

  - `items.speedMin` (string,null)
    Minimum speed that port can run at

  - `items.stateDescription` (array,null)
    Detailed descriptions of the port state

  - `items.systemId` (string,null)
    SystemUid/SerialNumber of the array.
    Example: "7CE751P312"

  - `items.tgtModeWriteOpt` (string,null)
    Target mode write optimization setting

  - `items.uniqueWwn` (string,null)
    Unique WWN setting

  - `items.vcn` (string,null)
    VLUN change notification

  - `items.virtualPorts` (array,null)
    Virtual ports

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


