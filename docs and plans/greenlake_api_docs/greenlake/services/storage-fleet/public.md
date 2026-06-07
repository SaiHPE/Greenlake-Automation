---
title: "HPE GreenLake for Storage Fleet"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public.md"
scraped_at: "2026-06-07T05:46:13.948253+00:00Z"
---

# HPE GreenLake for Storage Fleet

This page provides an introduction and quick start guide for the Storage Fleet API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

HPE GreenLake for Storage Fleet provides RESTful APIs to manage and configure storage systems and devices.

## Features

- Configure storage system settings such as system name and support contacts
- Configure and manage storage system settings for security and encryption for data-at-rest
- Manage storage system date and time settings
- Configure system network and proxy settings
- Report capacity and performance metrics with historical trends


## Developer guide

HPE GreenLake for Storage Fleet provides RESTful APIs to manage and configure storage systems and devices.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API requests to. Storage Fleet has unique endpoints in specific regions. Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU West: [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


#### Authentication

The Storage Fleet API uses an access token for authentication. Instructions
for obtaining an access token can be found on the [Authentication](/docs/greenlake/guides/public/authentication/authentication)
page.

The HTTP Authorization request header is used to provide the access token in
all API requests as a Bearer token.

- `Authorization:Bearer <access token>`


#### Authorization

All API requests are authorized using permissions. The user owning the access
token must have the required permissions assigned for the resources being accessed
in order to be authorized.

#### Required permissions

To use the HPE GreenLake Storage Fleet API, you need appropriate permissions based on your role:

- `storage-fleet.storage-system.read` for all `GET` and `LIST` requests on storage system resources
- `storage-fleet.storage-system.update` for all `PUT` requests on storage system resources
- `storage-fleet.system-settings.read` for all `GET` and `LIST` requests on storage system settings
- `storage-fleet.system-settings.update` for all `PUT` requests on storage system settings


### Making it all work

#### General guidelines

- For asynchronous operations that return HTTP status 201 or 202, use the Location header in the API response to track progress.
- Replace the base URL in examples with the endpoint for your region.


#### Get all storage systems

Retrieves all storage systems available to your account in the specified region.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/storage-systems
```

The endpoint [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com) is the endpoint for the US West application. If you are using HPE GreenLake for Storage Fleet in a different region, replace the endpoint with the corresponding region endpoint.

#### Get all HPE Alletra Storage MP B10000 systems

Retrieves all HPE Alletra Storage MP B10000 systems available to your account in the specified region.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems
```

#### Get all HPE Alletra Storage MP X10000 systems

Retrieves all HPE Alletra Storage MP X10000 systems available to your account in the specified region.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems
```

#### Update storage system configuration settings

Updates system configuration settings for an HPE Alletra Storage MP B10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings
```

Payload:


```bash
{
  "authMode": {
    "authmode": "ciphertext"
  },
  "dateTime": "01/15/2020 10:00:00",
  "installationSites": {
    "city": "Bangalore",
    "company": "Hewlett Packard Enterprise",
    "country": "India",
    "postalCode": "560001",
    "setSystemLocation": false,
    "state": "Karnataka",
    "streetAddress": "7992 Woodland Street",
    "supportProvider": "HPE"
  },
  "name": "Array1",
  "ntpAddresses": [
    "string"
  ],
  "remoteSyslogSettings": {
    "remoteSysLog": 0,
    "remoteSysLogHost": [
      "4.3.2.1:8080,1.2.3.4:8080"
    ],
    "remoteSysLogSecurityHost": [
      "5.6.7.8:8080,8.7.5.6:8080"
    ]
  },
  "srinfo": {
    "newCapacityMiB": 11000
  },
  "supportContact": {
    "company": "HPE",
    "companyCode": "HPE",
    "country": "US",
    "fax": "fax_id",
    "firstName": "john",
    "id": "67d09515-8526-9b02-c0c4-c1f443a39402",
    "lastName": "kevin",
    "notificationSeverities": [
      0,
      1,
      2,
      3,
      4,
      5
    ],
    "preferredLanguage": "en",
    "primaryEmail": "kevin.john@hpe.com",
    "primaryPhone": "98783456",
    "receiveEmail": true,
    "receiveGrouped": true,
    "secondaryEmail": "winny.pooh@hpe.com",
    "secondaryPhone": "23456789",
    "systemId": "7CE751P312"
  },
  "systemParameters": {
    "overprovRatioLimit": 2,
    "overprovRatioWarning": 1,
    "rwareConfidence": "low",
    "rwareRetentionTime": 1209600
  },
  "timezone": "Asia/Calcutta"
}
```

Updates system configuration settings for an HPE Alletra Storage MP X10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}
```

Payload:


```bash
{
  "auditPolicy": {
    "fwdThreshold": 4,
    "servers": [
      {
        "port": 1514,
        "protocol": "TCP",
        "target": "10.1.1.0"
      }
    ]
  },
  "autoSupport": "On",
  "clusterManagementDnsName": "usr1",
  "clusterManagementIpAddress": "10.0.0.11",
  "clusterManagementSubnetAddress": "255.255.255.0",
  "clusterManagementSubnetDefaultGateway": "255.255.255.1",
  "clusterName": "mip-01",
  "dnsServers": [
    "string"
  ],
  "force": true,
  "ntpServers": [
    "string"
  ],
  "outboundProxy": {
    "password": "ASCFJIUHGN7656NHIJF",
    "port": 3200,
    "server": "192.34.12.3",
    "username": "abcd"
  },
  "presentationTimeZone": "US/East-Indiana",
  "s3FrontEndConfiguration": {
    "s3DataNetworkConfigurations": [
      {
        "dataSubnet": "172.19.1.0/24",
        "dataSubnetGateway": "172.19.1.0",
        "s3IpRanges": [
          "172.19.3.50#44"
        ]
      }
    ],
    "s3DataNetworkDnsSubdomains": [
      "storage-dns-domain.com"
    ]
  },
  "supportContact": {
    "company": "HPE",
    "contactEmailAddress": "John@email.com",
    "country": "India",
    "firstName": "Jane",
    "lastName": "Joe",
    "phoneNumber": "5846624589",
    "preferredLanguage": "English"
  },
  "supportTunnel": "On"
}
```

#### Get all enclosures of a storage system

Retrieves all enclosures associated with the specified HPE Alletra Storage MP B10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures
```

Retrieves all enclosures associated with the specified HPE Alletra Storage MP X10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures
```

#### Update enclosure settings

Updates enclosure settings for the specified HPE Alletra Storage MP B10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}
```

Payload:


```bash
{
  "id": "5",
  "location": "MIP-01 H29 36-38"
}
```

Updates enclosure settings for the specified HPE Alletra Storage MP X10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures/{enclosureId}
```

Payload:


```bash
{
  "locatorLedState": "On"
}
```

#### Get all nodes of a storage system

Retrieves all nodes associated with the specified HPE Alletra Storage MP B10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes
```

Retrieves all storage nodes associated with the specified HPE Alletra Storage MP X10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes
```

#### Update storage node configuration

Updates the configuration for a specific storage node in an HPE Alletra Storage MP X10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes/{nodeId}
```

Payload:


```bash
{
  "frontendNics": [
    {
      "ports": [
        {
          "mtu": 1600
        }
      ],
      "slotNumber": 1
    }
  ]
}
```

#### Get all switches of a storage system

Retrieves all switches associated with the specified HPE Alletra Storage MP B10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches
```

Retrieves all switches associated with the specified HPE Alletra Storage MP X10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches
```

#### Locate a switch of a storage system

Locate a switch associated with an HPE Alletra Storage MP B10000 system.


```bash
POST https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}
```

Payload:


```bash
{
  "locate": true
}
```

Locate a switch associated with an HPE Alletra Storage MP X10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches/{switchId}
```

Payload:


```bash
{
  "internalNtpServer": "172.190.10.12",
  "locatorLedState": "On"
}
```

#### Get all custom certificates of a system

Retrieves all custom certificates associated with the specified HPE Alletra Storage MP X10000 system.


```bash
GET https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates
```

#### Create a custom certificate

Creates and adds a custom certificate to the specified HPE Alletra Storage MP X10000 system.


```bash
POST https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates
```

Payload:


```bash
{
  "name": "cert-1",
  "customCertificatePolicyRef": "s3-default-certificate-policy",
  "commonName": "S3",
  "organizationUnit": "string",
  "organization": "HPE",
  "locality": "MA",
  "province": "KA",
  "country": "IN",
  "selfSigned": true,
  "additionalProp1": {}
}
```

#### Update a custom certificate

Updates an existing custom certificate for the specified HPE Alletra Storage MP X10000 system.


```bash
PUT https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}
```

Payload:


```bash
{
  "certificate": "string",
  "caCertificate": "string"
}
```

#### Delete a custom certificate

Removes a custom certificate from the specified HPE Alletra Storage MP X10000 system.


```bash
DELETE https://us-west.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}
```