---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-systems/devicetype7getstorageclusterbyid.md"
scraped_at: "2026-06-07T06:16:00.277157+00:00Z"
---

# Get HPE Alletra Storage MP X10000 system identified by {systemId}

Get HPE Alletra Storage MP X10000 system identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the Storage system
    Example: "USE603C8P1"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier for the Storage system.
    Example: "ASHBFY6567YGHJ"

  - `type` (string, required)
    The type of the resource.
    Example: "group"

  - `apiVersion` (string,null)
    API version Details.
    Example: "sc.hpe.com/v1"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `customerId` (string,null)
    CustomerID for the Storage system.
    Example: "ASHBFDJHFB6567YGHJ"

  - `generation` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 1690045300

  - `kind` (string,null)
    Kind of the resource
    Example: "enclosures"

  - `logicalClusterSerialNumber` (string)
    10-digit identifier. This can serve as alternate Key for the Storage system resource. The value is fixed and immutable.
    Example: "ABGFDYRKJ1"

  - `resourceUri` (string,null)
    resourceUri for detailed Storage object
    Example: "/storage-fleet/v1alpha1/devtype7-storage-systems/7CE751P312/"

  - `status` (object,null)

  - `status.auditPolicy` (object,null)

  - `status.auditPolicy.fwdThreshold` (integer,null)
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

  - `status.auditPolicy.servers` (array,null)

  - `status.auditPolicy.servers.permittedPeers` (array,null)
    The permitted TLS peers
    Example: ["SHA256:10:C4:26:1D:CB:3C:AB:12:DB:1A:F0:47:37:AE:6D:D2:DE:66:B5:71:B7:2E:5B:BB:AE:0C:7E:7F:5F:0D:E9:64","SHA1:DD:23:E3:E7:70:F5:B4:13:44:16:78:A5:5A:8C:39:48:53:A6:DD:25"]

  - `status.auditPolicy.servers.port` (integer,null)
    Remote syslog server port
    Example: 1514

  - `status.auditPolicy.servers.protocol` (string,null)
    Transport protocol to use. Supported value is only {"TCP"}.
    Example: "TCP"

  - `status.auditPolicy.servers.target` (string,null)
    Remote syslog server address. Value of target could be Name or IP address
    Example: "10.1.1.0"

  - `status.auditPolicy.servers.trustStore` (string,null)
    It is used to set the name of the TrustStore resource to use. Initially, this will be restricted to a single trust store and will be set to "default"
    Example: "default"

  - `status.auditPolicy.servers.verifyPeer` (boolean,null)
    Indicates Whether the remote peer should be verified
    Example: true

  - `status.autoSupport` (string,null)
    Current status of the auto-support setting. {"On", "Off"}
    Example: "On"

  - `status.backendSubnets` (array,null)
    Backend Subnets for RDMA, Management Role

  - `status.backendSubnets.role` (string,null)
    Role of the backend subnets.
    Example: "RDMA"

  - `status.backendSubnets.subnet` (string,null)
    Subnet
    Example: "192.168.16.0/22"

  - `status.clusterManagementDnsName` (string,null)
    Storage system Management DNS Name
    Example: "usr1"

  - `status.clusterManagementIpAddress` (string,null)
    Storage system Management IPAddress.
    Example: "10.0.0.11"

  - `status.clusterManagementSubnetAddress` (string,null)
    Subnet Address of Storage system Management .
    Example: "255.255.255.0"

  - `status.clusterManagementSubnetDefaultGateway` (string,null)
    Default gateway of Storage system Management.
    Example: "255.255.255.1"

  - `status.clusterName` (string,null)
    Name of the Storage system.
    Example: "mip-01"

  - `status.conditions` (array,null)
    Array of conditions representing recent changes to the state of the storage system resource.

  - `status.conditions.lastTransitionTime` (string,null)
    Time of the last event.
    Example: "2023-07-21T05:59:58Z"

  - `status.conditions.message` (string,null)
    Describe about the Transition state.
    Example: "ending update, Updated DNSServers, Updated NtpServers, Updated proxy Successfully"

  - `status.conditions.observedGeneration` (integer,null)
    observedGeneration
    Example: 1

  - `status.conditions.reason` (string,null)
    contains a programmatic identifier indicating the reason for the condition's last transition.
    Example: "SuccessfulUpdate"

  - `status.conditions.status` (string,null)
    status for the event.
    Example: "true"

  - `status.conditions.type` (string)
    type of condition.
    Example: "Ready"

  - `status.dare` (object,null)

  - `status.dare.enabled` (boolean,null)
    Indicates whether data-at-rest encryption has been activated.
    Example: true

  - `status.dnsServers` (array,null)
    IP addresses for this storage system dns servers. List of IP Addresses.

  - `status.dnsSubdomain` (string,null)
    SubDomain of the DNS.
    Example: "10.0.1.17"

  - `status.lastModifiedTime` (string,null)
    UTC Time at which the status for this object was last updated.
    Example: "2023-07-26T06:50:10Z"

  - `status.ntpServers` (array,null)
    IP addresses for this Storage system NTP servers. List of IP Addresses.

  - `status.observedGeneration` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 25

  - `status.outboundProxy` (object,null)

  - `status.outboundProxy.port` (integer,null)
    The TCP port number to which proxy requests should be sent.
    Example: 3200

  - `status.outboundProxy.server` (string,null)
    The IPv4 Address or fully qualified domain name of the Outbound Proxy Server.
    Example: "192.34.12.3"

  - `status.presentationTimeZone` (string,null)
    The Time Zone to use for presenting times to the end user in the user interface.
    Example: "US/East-Indiana"

  - `status.ready` (boolean,null)
    Status.
    Example: true

  - `status.s3FrontEndConfiguration` (object,null)

  - `status.s3FrontEndConfiguration.s3DataNetworkConfigurations` (array,null)

  - `status.s3FrontEndConfiguration.s3DataNetworkConfigurations.dataSubnet` (string,null)
    Data Subnet.
    Example: "172.19.1.0/24"

  - `status.s3FrontEndConfiguration.s3DataNetworkConfigurations.dataSubnetGateway` (string,null)
    Data subnet Gateway
    Example: "172.19.1.0"

  - `status.s3FrontEndConfiguration.s3DataNetworkConfigurations.s3IpRanges` (array,null)
    List of IP address ranges for S3
    Example: ["172.19.3.50#44"]

  - `status.s3FrontEndConfiguration.s3DataNetworkConfigurations.s3RdmaIpRanges` (array,null)
    This field specifies the range of IP addresses used for S3 RDMA traffic on the front-end data ports.
    Example: ["172.19.1.100#44"]

  - `status.s3FrontEndConfiguration.s3DataNetworkDnsSubdomains` (array,null)
    List of IP address ranges for S3
    Example: ["storage-dns-domain.com"]

  - `status.s3RdmaCapable` (boolean,null)
    Indicates if this storage cluster can support S3 over RDMA. true means all nodes are configured with front-end NICs that support Object over RDMA, allowing the s3RdmaIPRanges attribute to be configured.
    Example: true

  - `status.strongPasswordMode` (string,null)
    Configuration of the strong password mode of the Storage system
    Example: "Password Mode"

  - `status.supportContact` (object,null)

  - `status.supportContact.company` (string,null)
    Name of the Company
    Example: "HPE"

  - `status.supportContact.contactEmailAddress` (string,null)
    Contact Email Address
    Example: "John@email.com"

  - `status.supportContact.country` (string,null)
    Country.
    Example: "India"

  - `status.supportContact.firstName` (string,null)
    First Name
    Example: "Jane"

  - `status.supportContact.lastName` (string,null)
    First Name
    Example: "Joe"

  - `status.supportContact.phoneNumber` (string,null)
    Phone Number.
    Example: "5846624589"

  - `status.supportContact.preferredLanguage` (string,null)
    Preferred Language.
    Example: "English"

  - `status.supportTunnel` (string,null)
    User-configurable to turn on/off support engineer tunnel access into the storage system.
    Example: "On"

  - `systemId` (string,null)
    Identifier of the Storage system.
    Example: "USE603C8P1"

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


