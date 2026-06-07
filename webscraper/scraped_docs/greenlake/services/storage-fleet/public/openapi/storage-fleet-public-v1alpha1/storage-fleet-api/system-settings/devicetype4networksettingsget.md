---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networksettingsget.md"
scraped_at: "2026-06-07T06:16:17.046262+00:00Z"
---

# Get Network-Settings details for an HPE Alletra Storage MP B10000 storage system

Get Network-Settings details for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

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
    Identifier for the resource.
    Example: "6848ef683c27403e96caa51816ddc72c"

  - `items.type` (string, required)
    type
    Example: "Type of the resource"

  - `items.portManagement` (object,null)
    Port Management details for a device

  - `items.portManagement.id` (string, required)
    Unique Identifier of the resource
    Example: "eb5149ef0d3bc95f2a7e24c4b29edc92"

  - `items.portManagement.type` (string, required)
    The type of resource.
    Example: "network-settings"

  - `items.portManagement.associatedLinks` (array,null)
    Associated Links Details

  - `items.portManagement.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.portManagement.associatedLinks.type` (string)
    Resource Name

  - `items.portManagement.authenticationRequired` (string,null)
    Is authentication required. Allowed values are enabled or disabled
    Example: "enabled"

  - `items.portManagement.commonResourceAttributes` (object,null)

  - `items.portManagement.commonResourceAttributes.cloudState` (string)
    The cloud connectivity status of the system associated with this resource
    Example: "CONNECTED"

  - `items.portManagement.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.portManagement.commonResourceAttributes.errMessage` (string,null)
    Reason why the system associated with the resource is blocked
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.portManagement.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1cv"

  - `items.portManagement.defaultRouteIpv4` (string,null)
    Default IPV4 route address of the network port
    Example: "15.212.12.30"

  - `items.portManagement.defaultRouteIpv6` (string,null)
    Default IPV6 route address of the network port
    Example: "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

  - `items.portManagement.displayname` (string,null)
    Name to be used for display purposes
    Example: "Management Port"

  - `items.portManagement.dnsServer` (string,null)
    DNS Server of the network port
    Example: "10.112.132.43"

  - `items.portManagement.domain` (string,null)
    Domain that the resource belongs to
    Example: "sample.com"

  - `items.portManagement.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627533960634

  - `items.portManagement.ipV4Data` (object,null)

  - `items.portManagement.ipV4Data.activeNode` (integer,null)
    Active node ID
    Example: 1

  - `items.portManagement.ipV4Data.autoSense` (boolean,null)
    Specifies if the autosense is enabled for network port
    Example: true

  - `items.portManagement.ipV4Data.fullDuplex` (boolean,null)
    Is network port full duplex
    Example: true

  - `items.portManagement.ipV4Data.ipAddress` (string,null)
    IP Address of the network port
    Example: "15.12.123.234"

  - `items.portManagement.ipV4Data.netMask` (string,null)
    Net mask of the network port
    Example: "255.255.255.0"

  - `items.portManagement.ipV4Data.speed` (integer,null)
    Speed of the network port
    Example: 1000

  - `items.portManagement.ipV4Data.state` (object,null)
    State of the resource

  - `items.portManagement.ipV4Data.state.detailed` (array,null)
    Array of the detailed states of the resource

  - `items.portManagement.ipV4Data.state.overall` (string,null)
    Overall state of the resource
    Enum: "STATE_UNKNOWN", "STATE_NORMAL", "STATE_DEGRADED", "STATE_FAILED", "STATE_NOT_APPLICABLE", "STATE_NEW", null

  - `items.portManagement.ipV4Data.status` (string,null)
    Status of the network port
    Example: "Active"

  - `items.portManagement.ipV6Data` (object,null)

  - `items.portManagement.newDefaultRouteIpv4` (string,null)
    New default IPV4 route address of the network port
    Example: "15.212.12.30"

  - `items.portManagement.newDefaultRouteIpv6` (string,null)
    New default IPV6 route address of the network port
    Example: "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

  - `items.portManagement.newIpV4Data` (object,null)

  - `items.portManagement.newIpv6Data` (object,null)

  - `items.portManagement.ntpServer` (string,null)
    NTP Server of the network port
    Example: "16.110.23.123 16.110.23.124"

  - `items.portManagement.proxyPort` (integer,null)
    Proxy Server Port. Allowed values are 1-65535
    Example: 45

  - `items.portManagement.proxyProtocol` (string,null)
    Supported proxy protocols are HTTP, SOCKS4 and SOCKS5.
    Example: "HTTP"

  - `items.portManagement.proxyServer` (string,null)
    Proxy server IP address
    Example: "proxy.company.net"

  - `items.portManagement.proxyUser` (string,null)
    Username for authentication. (Required only if Authentication required is enabled)
    Example: "proxySampleUser"

  - `items.portManagement.systemId` (string,null)
    Serial Number of the array
    Example: "7CEFVC12"

  - `items.portManagement.vpIpList` (array,null)
    A list of VASA Provider IP addresses configured at array node level. Applicable for HPE Alletra Storage MP B10000 storage system with 10.5.0 version and later.

  - `items.portManagement.vpIpList.ipv4Address` (string,null)
    IPV4 address of the VASA provider
    Example: "16.172.189.111"

  - `items.portManagement.vpIpList.ipv4NetMask` (string,null)
    IPV4 NetMask of the VASA provider
    Example: "255.255.224.0"

  - `items.portManagement.vpIpList.ipv6Address` (string,null)
    IPV6 address of the VASA provider
    Example: "16.172.189.111"

  - `items.portManagement.vpIpList.ipv6PrefixLen` (string,null)
    IPV6 Prefix length
    Example: "16"

  - `items.portManagement.vpIpList.nodeId` (integer,null)
    The unique identifier of the node. This will be non-network master node.
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


