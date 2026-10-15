---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/ports/devicetype4portsgetbyid.md"
scraped_at: "2026-06-07T06:15:56.803760+00:00Z"
---

# Get details of HPE Alletra Storage MP B10000 Port identified by {id}

Get details of HPE Alletra Storage MP B10000 Port identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    UID of the port
    Example: "d0fcfe2ff572f44e5beb0a9712c76d5d"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the resource
    Example: "9d765763116c20a508e8996f2a10821d"

  - `type` (string, required)
    type
    Example: "string"

  - `associatedLinks` (array)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `cardType` (object,null)
    Type of the PCI card this port is on

  - `cardType.default` (string,null)

  - `cardType.key` (string,null)

  - `class` (integer,null)
    Fibre Channel class (can be either 2 or 3)

  - `class2` (string,null)
    Class2 state and configuration

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

  - `config` (string,null)
    Configuration state of port
    Example: "valid"

  - `configMode` (string,null)
    Connection mode of the port

  - `connectionType` (string,null)
    port connection type

  - `customerId` (string,null)
    customerId
    Example: "string"

  - `devices` (array,null)

  - `devices.device` (string,null)
    Type of the device. This is applicable for HPE Alletra Storage MP B10000 10.5.50 OS version and above.

  - `devices.name` (string,null)
    Name of the device

  - `devices.port` (integer,null)
    Port of the device. This is applicable for HPE Alletra Storage MP B10000 10.5.50 OS version and above.

  - `devices.position` (integer,null)
    Position of the device

  - `devices.slot` (integer,null)
    Slot of the device. This is applicable for HPE Alletra Storage MP B10000 10.5.50 OS version and above.

  - `displayname` (string,null)
    Name to be used for display purposes

  - `domain` (string,null)
    Domain that the resource belongs to

  - `enclosureCardId` (integer,null)
    ID of the enclosure card

  - `enclosureCardPciId` (integer,null)
    ID of the enclosure card PCI card

  - `enclosureCardPciUid` (string,null)
    UID of the enclosure card PCI card

  - `enclosureCardUid` (string,null)
    Unique Identifier of the enclosure card

  - `enclosureId` (integer,null)
    ID of the enclosure

  - `enclosureUid` (string,null)
    Unique Identifier of the enclosure

  - `failoverStatus` (string,null)
    Failover status of this port and the partner

  - `fcData` (object,null)

  - `fcData.nodeWwn` (string,null)
    nodeWWN of the FC port

  - `fcData.portWwn` (string,null)
    portWWN of the FC port

  - `fileData` (object,null)

  - `fileData.failoverIps` (string,null)
    Failover IP details of the File port

  - `fileData.ipDisabled` (boolean,null)
    Indicates if the port IP is disabled or not

  - `fileData.linkState` (string,null)
    Link State of the File port

  - `fileData.prefixLength` (integer,null)
    Prefix length of the File port

  - `fileData.vlanId` (integer,null)
    VLAN id for the File port

  - `fwVersion` (string,null)
    Firmware version
    Example: "12.2.396.1"

  - `generation` (integer,null)
    generation

  - `hostVirtualPorts` (array,null)

  - `hostVirtualPorts.nodeWwn` (string)
    Node WWN of the virtual port

  - `hostVirtualPorts.portLinkState` (string)
    Port link state
    Enum: "LINK_STATE_CONFIG_WAIT", "LINK_STATE_ALPA_WAIT", "LINK_STATE_LOGIN_WAIT", "LINK_STATE_READY", "LINK_STATE_LOSS_SYNC", "LINK_STATE_ERROR", "LINK_STATE_XXX", "LINK_STATE_NONPARTICIPATE", "LINK_STATE_COREDUMP", "LINK_STATE_OFFLINE", "LINK_STATE_FWDEAD", "LINK_STATE_LINK_IDLE_FOR_RESET", "LINK_STATE_DHCP_IN_PROGRESS", "LINK_STATE_PENDING_RESET", "LINK_STATE_UNKNOWN"

  - `hostVirtualPorts.portType` (string)
    Virtual port type
    Enum: "PORT_TYPE_FREE", "PORT_TYPE_HOST", "PORT_TYPE_DISK", "PORT_TYPE_IPORT", "PORT_TYPE_RCFC", "PORT_TYPE_RCIP", "PORT_TYPE_ISCSI", "PORT_TYPE_PEER", "PORT_TYPE_CNA", "PORT_TYPE_FS", "PORT_TYPE_UNKNOWN"

  - `hostVirtualPorts.portWwn` (string)
    Port WWN of the virtual port

  - `hostVirtualPorts.protocol` (string)
    Protocol of the Virtual port
    Enum: "PORT_PROTOCOL_UNKNOWN", "PORT_PROTOCOL_FC", "PORT_PROTOCOL_ISCSCI", "PORT_PROTOCOL_FCOE", "PORT_PROTOCOL_IP", "PORT_PROTOCOL_SAS", "PORT_PROTOCOL_NVME"

  - `hostVirtualPorts.vpi` (integer)
    Virtual port index

  - `interruptCoalesce` (string,null)
    Interrupt Coalesce

  - `ipData` (object,null)

  - `ipData.autoneg` (boolean,null)
    Auto negotiation state of IP port

  - `ipData.delimitedMacAddress` (string,null)
    MAC address of the IP port

  - `ipData.duplex` (string,null)
    Duplex state of IP port

  - `ipData.gatewayAddress` (string,null)
    Gateway Address of IP port

  - `ipData.gatewayAddressV6` (string,null)
    Gateway Address of IP port

  - `ipData.ipAddress` (string,null)
    IP address of IP port

  - `ipData.ipAddressV6` (string,null)
    IP address of IP port

  - `ipData.macAddress` (string,null)
    IP address of IP port

  - `ipData.mtu` (string,null)
    Maximum transmission unit (MTU) size

  - `ipData.subnetMask` (string,null)
    NetMask of IP port

  - `ipData.subnetMaskV6` (string,null)
    NetMask of IP port

  - `iscsiData` (object,null)

  - `iscsiData.delimitedMacAddress` (string,null)
    MAC address of the iSCSI port

  - `iscsiData.ethernetFlowControl` (string,null)
    Flow control setting of the port. Applicable for HPE Alletra Storage MP B10000 10.5.0 OS version and above. Possible values are "None", "DCBX=IEEE", "DCBX=IEEE PFC=Off" and "EthPause".

  - `iscsiData.gatewayAddress` (string,null)
    Gateway Address of iSCSI port

  - `iscsiData.gatewayAddressV6` (string,null)
    Gateway Address of iSCSI port.

  - `iscsiData.ipAddress` (string,null)
    IP address of iSCSI port

  - `iscsiData.ipAddressV6` (string,null)
    IPv6 address of iSCSI port.

  - `iscsiData.iscsiName` (string,null)
    iSCSI name of iSCSI port

  - `iscsiData.isnsPrimaryAddress` (string,null)
    Primary iSNS address

  - `iscsiData.isnsTcpPort` (integer,null)
    iSNS TCP port

  - `iscsiData.macAddress` (string,null)
    IP address of iSCSI port

  - `iscsiData.peerEnabled` (boolean,null)
    Indicates if the port is peer enabled

  - `iscsiData.sendTargetGroupTag` (integer,null)
    Send target group of the iSCSI port

  - `iscsiData.subnetMask` (string,null)
    NetMask of iSCSI port

  - `iscsiData.subnetMaskV6` (string,null)
    Netmask of iSCSI port.

  - `iscsiData.supportsVlan` (boolean,null)
    Indicates if the port support VLAN

  - `iscsiData.targetPortalGroupTag` (integer,null)
    Target portal group of the iSCSI port

  - `label` (string,null)
    Label
    Example: "IP0"

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

  - `mode` (string,null)
    Current mode the port is in

  - `modeChange` (string,null)
    Indicates if the mode change is allowed or prohibited

  - `name` (string,null)
    Name of the resource

  - `nodeCardId` (string,null)
    Unique Identifier of the node adapter card

  - `nodeId` (string,null)
    Unique Identifier of the node
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `nvmeData` (object,null)

  - `nvmeData.delimitedMacAddress` (string,null)
    MAC address of the NVMe port

  - `nvmeData.eth` (string,null)
    Ethernet name used by the NVMe port

  - `nvmeData.gatewayAddress` (string,null)
    Gateway of the NVMe port

  - `nvmeData.gatewayAddressV6` (string,null)
    Gateway address for the NVMe port.
    Example: "FE80::1"

  - `nvmeData.ipAddress` (string,null)
    IP address of the NVMe port

  - `nvmeData.ipAddressV6` (string,null)
    IPV6 address for the NVMe port.
    Example: "2001:db8:abcd:12:ffff:ffff:ffff:ff16"

  - `nvmeData.macAddress` (string,null)
    MAC address of the NVMe port

  - `nvmeData.nqn` (string,null)
    NVMe qualified name of the NVMe port

  - `nvmeData.pcidev` (string,null)
    PCI device used by the NVMe port

  - `nvmeData.prefixLength` (integer,null)
    Prefix Length of the NVMe port

  - `nvmeData.prefixLengthV6` (integer,null)
    Prefix length of the NVMe port.
    Example: 13

  - `nvmeData.protocol` (string)
    Current protocol the port is in

  - `nvmeData.rate` (string)
    Configured speed of the NVMe port

  - `nvmeData.state` (string,null)
    State of the resource

  - `nvmeData.transport` (object,null)
    Transport type of the NVMe port.

  - `nvmeData.vlanCount` (integer,null)
    Number of configured VLANs on this NVMe port

  - `nvmeData.vlans` (array,null)

  - `nvmeData.vlans.ethernetFlowControl` (string,null)
    Flow control setting of the NVMe port. Applicable for HPE Alletra Storage MP B10000 10.5.0 OS version and above. Possible values are "None", "DCBX=IEEE", "DCBX=IEEE PFC=Off" and "EthPause".

  - `nvmeData.vlans.gatewayAddress` (string,null)
    VLAN Gateway address for the NVMe port

  - `nvmeData.vlans.gatewayAddressV6` (string,null)
    Gateway address for the NVMe port. If Vlan is configured, then this is Vlan gateway address of this port.
    Example: "FE80::1"

  - `nvmeData.vlans.ipAddress` (string,null)
    VLAN IP address for the NVMe port

  - `nvmeData.vlans.ipAddressV6` (string,null)
    IPV6 address for the NVMe port. If Vlan is configured, then this is Vlan IPV6 address of this port.
    Example: "2001:db8:abcd:12:ffff:ffff:ffff:ff16"

  - `nvmeData.vlans.prefixLength` (integer,null)
    Prefix length of the NVMe port

  - `nvmeData.vlans.vlanId` (string,null)
    VLAN id for the NVMe port

  - `partner` (object,null)

  - `partner.nodeWwnOrName` (string,null)
    Node WWN (for FC) or iSCSI name (for iSCSI)

  - `partner.portWwnOrIp` (string,null)
    Port WWN (for FC) or IP address (for iSCSI)

  - `partner.position` (object,null)

  - `partner.position.node` (integer,null)
    Port position node number

  - `partner.position.port` (integer,null)
    Port position port number

  - `partner.position.slot` (integer,null)
    Port position slot number

  - `portSfp` (object,null)

  - `portSfp.qualified` (boolean,null)
    Indicates if the SFP is qualified or not

  - `portSfp.rxLossPin` (object,null)
    RX loss pin position. If position is HI, RX loss of signal

  - `portSfp.rxPowerLow` (boolean,null)
    Indicates if RX power is low or not

  - `portSfp.speed` (integer,null)
    Speed in bits per second

  - `portSfp.supportDdm` (boolean,null)
    Indicates if the SFP supports DDM

  - `portSfp.txDisablePin` (object,null)
    TX disable pin position. If position is HI, TX laser is disabled

  - `portSfp.txFaultPin` (object,null)
    TX fault pin position. If position is HI, TX fault

  - `portType` (string,null)
    Type of the port based on the device it is connected to

  - `resourceUri` (string,null)
    resourceUri for detailed ports object
    Example: "/storage-fleet/v1alpha1/devtype4-storage-systems/7CE751P312/ports/220fcd48857f63c0f354c6723ec5d5cb"

  - `revision` (string,null)
    Revision of the Host Bus Adapter

  - `smartSan` (string,null)
    Smart SAN status

  - `speedActual` (string,null)
    Actual speed that port is running at

  - `speedConfigured` (string,null)
    Speed that is configured to run as

  - `speedMax` (string,null)
    Maximum speed that port can run at

  - `speedMin` (string,null)
    Minimum speed that port can run at

  - `stateDescription` (array,null)
    Detailed descriptions of the port state

  - `systemId` (string,null)
    SystemUid / SerialNumber of the array
    Example: "7CE751P312"

  - `tgtModeWriteOpt` (string,null)
    Target mode write optimization setting

  - `uniqueWwn` (string,null)
    Unique WWN setting

  - `vcn` (string,null)
    VLUN change notification

  - `virtualPorts` (array,null)
    Virtual ports

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


