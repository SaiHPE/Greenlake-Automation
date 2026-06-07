---
title: "PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7editstoragesystemsettingsbyid.md"
scraped_at: "2026-06-07T06:16:13.968109+00:00Z"
---

# Edit settings of HPE Alletra Storage MP X10000 system identified by {systemId}

Edit settings of HPE Alletra Storage MP X10000 system identified by {systemId}

Endpoint: PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the Storage system
    Example: "USE603C8P1"

## Request fields (application/json):

  - `auditPolicy` (object,null)

  - `auditPolicy.fwdThreshold` (integer,null)
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

  - `auditPolicy.servers` (array,null)

  - `auditPolicy.servers.permittedPeers` (array,null)
    The permitted TLS peers
    Example: ["SHA256:10:C4:26:1D:CB:3C:AB:12:DB:1A:F0:47:37:AE:6D:D2:DE:66:B5:71:B7:2E:5B:BB:AE:0C:7E:7F:5F:0D:E9:64","SHA1:DD:23:E3:E7:70:F5:B4:13:44:16:78:A5:5A:8C:39:48:53:A6:DD:25"]

  - `auditPolicy.servers.port` (integer,null)
    Remote syslog server port
    Example: 1514

  - `auditPolicy.servers.protocol` (string,null)
    Transport protocol to use. Supported value is only {"TCP"}.
    Example: "TCP"

  - `auditPolicy.servers.target` (string,null)
    Remote syslog server address. Value of target could be Name or IP address
    Example: "10.1.1.0"

  - `auditPolicy.servers.trustStore` (string,null)
    It is used to set the name of the TrustStore resource to use. Initially, this will be restricted to a single trust store and will be set to "default"
    Example: "default"

  - `auditPolicy.servers.verifyPeer` (boolean,null)
    Indicates Whether the remote peer should be verified
    Example: true

  - `autoSupport` (string,null)
    Current status of the auto-support setting. {"On", "Off"}
    Example: "On"

  - `clusterManagementDnsName` (string,null)
    Storage system Management DNS Name
    Example: "usr1"

  - `clusterManagementIpAddress` (string,null)
    Storage system Management IPAddress.
    Example: "10.0.0.11"

  - `clusterManagementSubnetAddress` (string,null)
    Subnet Address of Storage system Management .
    Example: "255.255.255.0"

  - `clusterManagementSubnetDefaultGateway` (string,null)
    Default gateway of Storage system Management.
    Example: "255.255.255.1"

  - `clusterName` (string,null)
    Name of the Storage System.
    Example: "mip-01"

  - `dnsServers` (array,null)
    IP addresses for this Storage system dns servers. List of IP Addresses.

  - `force` (boolean)
    Ignore warnings and forcibly merge specified group with this group. Possible values: 'true', 'false'.
    Example: true

  - `ntpServers` (array,null)
    IP addresses for this Storage system NTP servers. List of IP Addresses.

  - `outboundProxy` (object,null)

  - `outboundProxy.password` (string,null)
    The password, if any, to use with the proxy server hashed value.
    Example: "ASCFJIUHGN7656NHIJF"

  - `outboundProxy.port` (integer,null)
    The TCP port number to which proxy requests should be sent.
    Example: 3200

  - `outboundProxy.server` (string,null)
    The IPv4 Address or fully qualified domain name of the Outbound Proxy Server.
    Example: "192.34.12.3"

  - `outboundProxy.username` (string,null)
    Username.
    Example: "abcd"

  - `presentationTimeZone` (string,null)
    The Time Zone to use for presenting times to the end user in the user interface.
    Example: "US/East-Indiana"

  - `s3FrontEndConfiguration` (object,null)

  - `s3FrontEndConfiguration.s3DataNetworkConfigurations` (array,null)

  - `s3FrontEndConfiguration.s3DataNetworkConfigurations.dataSubnet` (string,null)
    Data Subnet.
    Example: "172.19.1.0/24"

  - `s3FrontEndConfiguration.s3DataNetworkConfigurations.dataSubnetGateway` (string,null)
    Data subnet Gateway
    Example: "172.19.1.0"

  - `s3FrontEndConfiguration.s3DataNetworkConfigurations.s3IpRanges` (array,null)
    List of IP address ranges for S3
    Example: ["172.19.3.50#44"]

  - `s3FrontEndConfiguration.s3DataNetworkConfigurations.s3RdmaIpRanges` (array,null)
    This field specifies the range of IP addresses used for S3 RDMA traffic on the front-end data ports.
    Example: ["172.19.1.100#44"]

  - `s3FrontEndConfiguration.s3DataNetworkDnsSubdomains` (array,null)
    List of IP address ranges for S3
    Example: ["storage-dns-domain.com"]

  - `supportContact` (object,null)

  - `supportContact.company` (string,null)
    Name of the Company
    Example: "HPE"

  - `supportContact.contactEmailAddress` (string,null)
    Contact Email Address
    Example: "John@email.com"

  - `supportContact.country` (string,null)
    Country.
    Example: "India"

  - `supportContact.firstName` (string,null)
    First Name
    Example: "Jane"

  - `supportContact.lastName` (string,null)
    First Name
    Example: "Joe"

  - `supportContact.phoneNumber` (string,null)
    Phone Number.
    Example: "5846624589"

  - `supportContact.preferredLanguage` (string,null)
    Preferred Language.
    Example: "English"

  - `supportTunnel` (string,null)
    User-configurable to turn on/off support engineer tunnel access into the Storage system.
    Example: "On"

## Response 202 fields (application/json):

  - `taskUri` (string, required)
    Task URI which can be used to monitor the status of the operation.
    Example: "/rest/vega/v1/tasks/4969a568-6fed-4915-bcd5-e4566a75e00c"

  - `message` (string)
    Task Message.
    Example: "Successfully submitted"

  - `status` (string)
    Status of the task.
    Example: "SUBMITTED"

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


