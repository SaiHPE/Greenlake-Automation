---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7getstorageclusters.md"
scraped_at: "2026-06-07T06:16:13.985366+00:00Z"
---

# Get all HPE Alletra Storage MP X10000 system

Get all HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems
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
    Lucene query to filter systems by Key.
    Example: "NAME eq g1a1"

  - `sort` (string)
    Lucene query to sort systems by Key.
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
    Unique identifier for the Storage system. Filter, Sort
    Example: "ASHBFY6567YGHJ"

  - `items.type` (string, required)
    The type of the resource.
    Example: "group"

  - `items.apiVersion` (string,null)
    API version Details.
    Example: "sc.hpe.com/v1"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    CustomerID for the Storage system. Filter
    Example: "ASHBFDJHFB6567YGHJ"

  - `items.generation` (integer,null)
    The most recent specification that has been observed by the controller. Filter, Sort
    Example: 1690045300

  - `items.kind` (string,null)
    Kind of the resource
    Example: "enclosures"

  - `items.logicalClusterSerialNumber` (string)
    10-digit identifier. This can serve as alternate Key for the resource. The value is fixed and immutable.
    Example: "ABGFDYRKJ1"

  - `items.resourceUri` (string,null)
    resourceUri for detailed Storage object
    Example: "/storage-fleet/v1alpha1/devtype7-storage-systems/7CE751P312/"

  - `items.status` (object,null)

  - `items.status.auditPolicy` (object,null)

  - `items.status.auditPolicy.fwdThreshold` (integer,null)
    Forward threshold - Message severity level at which audit events will be forwarded. Supported values:
  0 - Emergency: system is unusable
  1 - Alert: action must be taken immediately
  2 - Critical: critical conditions
  3 - Error: error conditions
  4 - Warning: warning conditions
  5 - Notice: normal but significant condition
  6 - Informational: informational messages
  7 - Debug: debug-level messages
    Example: 4

  - `items.status.auditPolicy.servers` (array,null)

  - `items.status.auditPolicy.servers.permittedPeers` (array,null)
    The permitted TLS peers
    Example: ["SHA256:10:C4:26:1D:CB:3C:AB:12:DB:1A:F0:47:37:AE:6D:D2:DE:66:B5:71:B7:2E:5B:BB:AE:0C:7E:7F:5F:0D:E9:64","SHA1:DD:23:E3:E7:70:F5:B4:13:44:16:78:A5:5A:8C:39:48:53:A6:DD:25"]

  - `items.status.auditPolicy.servers.port` (integer,null)
    Remote syslog server port
    Example: 1514

  - `items.status.auditPolicy.servers.protocol` (string,null)
    Transport protocol to use. Supported value is only {"TCP"}.
    Example: "TCP"

  - `items.status.auditPolicy.servers.target` (string,null)
    Remote syslog server address. Value of target could be Name or IP address
    Example: "10.1.1.0"

  - `items.status.auditPolicy.servers.trustStore` (string,null)
    It is used to set the name of the TrustStore resource to use. Initially, this will be restricted to a single trust store and will be set to "default"
    Example: "default"

  - `items.status.auditPolicy.servers.verifyPeer` (boolean,null)
    Indicates Whether the remote peer should be verified
    Example: true

  - `items.status.autoSupport` (string,null)
    Current status of the auto-support setting. {"On", "Off"}
    Example: "On"

  - `items.status.backendSubnets` (array,null)
    Backend Subnets for RDMA, Management Role

  - `items.status.backendSubnets.role` (string,null)
    Role of the backend subnets.
    Example: "RDMA"

  - `items.status.backendSubnets.subnet` (string,null)
    Subnet
    Example: "192.168.16.0/22"

  - `items.status.clusterManagementDnsName` (string,null)
    Storage system Management DNS Name
    Example: "usr1"

  - `items.status.clusterManagementIpAddress` (string,null)
    Storage system Management IPAddress.
    Example: "10.0.0.11"

  - `items.status.clusterManagementSubnetAddress` (string,null)
    Subnet Address of Storage system Management .
    Example: "255.255.255.0"

  - `items.status.clusterManagementSubnetDefaultGateway` (string,null)
    Default gateway of Storage system Management.
    Example: "255.255.255.1"

  - `items.status.clusterName` (string,null)
    Name of the Storage system.
    Example: "mip-01"

  - `items.status.conditions` (array,null)
    Array of conditions representing recent changes to the state of the storage system resource.

  - `items.status.conditions.lastTransitionTime` (string,null)
    Time of the last event.
    Example: "2023-07-21T05:59:58Z"

  - `items.status.conditions.message` (string,null)
    Describe about the Transition state.
    Example: "ending update, Updated DNSServers, Updated NtpServers, Updated proxy Successfully"

  - `items.status.conditions.observedGeneration` (integer,null)
    observedGeneration
    Example: 1

  - `items.status.conditions.reason` (string,null)
    contains a programmatic identifier indicating the reason for the condition's last transition.
    Example: "SuccessfulUpdate"

  - `items.status.conditions.status` (string,null)
    status for the event.
    Example: "true"

  - `items.status.conditions.type` (string)
    type of condition.
    Example: "Ready"

  - `items.status.dare` (object,null)

  - `items.status.dare.enabled` (boolean,null)
    Indicates whether data-at-rest encryption has been activated.
    Example: true

  - `items.status.dnsServers` (array,null)
    IP addresses for this storage system dns servers. List of IP Addresses.

  - `items.status.dnsSubdomain` (string,null)
    SubDomain of the DNS.
    Example: "10.0.1.17"

  - `items.status.lastModifiedTime` (string,null)
    UTC Time at which the status for this object was last updated.
    Example: "2023-07-26T06:50:10Z"

  - `items.status.ntpServers` (array,null)
    IP addresses for this Storage system NTP servers. List of IP Addresses.

  - `items.status.observedGeneration` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 25

  - `items.status.outboundProxy` (object,null)

  - `items.status.outboundProxy.port` (integer,null)
    The TCP port number to which proxy requests should be sent.
    Example: 3200

  - `items.status.outboundProxy.server` (string,null)
    The IPv4 Address or fully qualified domain name of the Outbound Proxy Server.
    Example: "192.34.12.3"

  - `items.status.presentationTimeZone` (string,null)
    The Time Zone to use for presenting times to the end user in the user interface.
    Example: "US/East-Indiana"

  - `items.status.ready` (boolean,null)
    Status.
    Example: true

  - `items.status.s3FrontEndConfiguration` (object,null)

  - `items.status.s3FrontEndConfiguration.s3DataNetworkConfigurations` (array,null)

  - `items.status.s3FrontEndConfiguration.s3DataNetworkConfigurations.dataSubnet` (string,null)
    Data Subnet.
    Example: "172.19.1.0/24"

  - `items.status.s3FrontEndConfiguration.s3DataNetworkConfigurations.dataSubnetGateway` (string,null)
    Data subnet Gateway
    Example: "172.19.1.0"

  - `items.status.s3FrontEndConfiguration.s3DataNetworkConfigurations.s3IpRanges` (array,null)
    List of IP address ranges for S3
    Example: ["172.19.3.50#44"]

  - `items.status.s3FrontEndConfiguration.s3DataNetworkConfigurations.s3RdmaIpRanges` (array,null)
    This field specifies the range of IP addresses used for S3 RDMA traffic on the front-end data ports.
    Example: ["172.19.1.100#44"]

  - `items.status.s3FrontEndConfiguration.s3DataNetworkDnsSubdomains` (array,null)
    List of IP address ranges for S3
    Example: ["storage-dns-domain.com"]

  - `items.status.s3RdmaCapable` (boolean,null)
    Indicates if this storage cluster can support S3 over RDMA. true means all nodes are configured with front-end NICs that support Object over RDMA, allowing the s3RdmaIPRanges attribute to be configured.
    Example: true

  - `items.status.strongPasswordMode` (string,null)
    Configuration of the strong password mode of the Storage system
    Example: "Password Mode"

  - `items.status.supportContact` (object,null)

  - `items.status.supportContact.company` (string,null)
    Name of the Company
    Example: "HPE"

  - `items.status.supportContact.contactEmailAddress` (string,null)
    Contact Email Address
    Example: "John@email.com"

  - `items.status.supportContact.country` (string,null)
    Country.
    Example: "India"

  - `items.status.supportContact.firstName` (string,null)
    First Name
    Example: "Jane"

  - `items.status.supportContact.lastName` (string,null)
    First Name
    Example: "Joe"

  - `items.status.supportContact.phoneNumber` (string,null)
    Phone Number.
    Example: "5846624589"

  - `items.status.supportContact.preferredLanguage` (string,null)
    Preferred Language.
    Example: "English"

  - `items.status.supportTunnel` (string,null)
    User-configurable to turn on/off support engineer tunnel access into the storage system.
    Example: "On"

  - `items.systemId` (string,null)
    Identifier of the Storage system. Filter, Sort
    Example: "USE603C8P1"

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


