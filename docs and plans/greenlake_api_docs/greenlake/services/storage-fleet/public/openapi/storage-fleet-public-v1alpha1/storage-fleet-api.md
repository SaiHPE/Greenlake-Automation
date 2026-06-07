---
title: "HPE Greenlake For Storage Fleet REST APIs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api.md"
scraped_at: "2026-06-07T05:46:39.159021+00:00Z"
---

# HPE Greenlake For Storage Fleet REST APIs

HPE Greenlake For Storage Fleet REST APIs

Version: 1.2.0
License: HPE End User License Agreement

## Servers

```
https://eu1.data.cloud.hpe.com
```

```
https://us1.data.cloud.hpe.com
```

```
https://jp1.data.cloud.hpe.com
```

## Security

### bearer

Storage Fleet API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE Greenlake For Storage Fleet REST APIs](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api.yaml)

## certificates

The Certificate API provides endpoints for managing and configuring certificates.

### Get all custom certificate policies of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificate-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7getcustomcertificatepolicies.md): Get all custom certificate policies of a HPE Alletra Storage MP X10000 system

### Get Certificate policies of a HPE Alletra Storage MP X10000 system identified by certificatePolicyID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificate-policies/{certificatePolicyId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7getcustomcertificatepoliciesbyid.md): Get Certificate policies of a HPE Alletra Storage MP X10000 system identified by certificatePolicyID

### Get all custom certificates of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7getcustomcertificates.md): Get all custom certificates of a HPE Alletra Storage MP X10000 system

### Create a custom certificate for storage cluster

 - [POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/createstorageclustercustomcertificate.md): This API endpoint is to create a custom certificate for storage cluster

### delete storage cluster custom certificate identified by {certificateId}

 - [DELETE /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/deletestorageclustercustomcertificate.md): delete storage cluster custom certificate identified by {certificateId}

### Get Custom Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7getcustomcertificatebyid.md): Get Custom Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID

### Import certificates for HPE Alletra Storage MP X10000 system identified by certificateId

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates/{certificateId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7importcustomcertificate.md): Import certificates for HPE Alletra Storage MP X10000 system identified by certificateId

### Get all custom certificates of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7gettrustcertificates.md): Get all custom certificates of a HPE Alletra Storage MP X10000 system

### Create a trust certificate for storage cluster

 - [POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/createstorageclustertrustcertificate.md): This API endpoint is to create a trust certificate for storage cluster

### delete storage cluster trust certificate identified by {certificateId}

 - [DELETE /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates/{certificateId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/deletestorageclustertrustcertificate.md): delete storage cluster trust certificate identified by {certificateId}

### Get Trust Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates/{certificateId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7gettrustcertificatebyid.md): Get Trust Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID

### Get all Trust Store of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-stores](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7gettruststores.md): Get all Trust Store of a HPE Alletra Storage MP X10000 system. A Trust Store represents a collection of trusted certificates.

### Get Trust Store of a HPE Alletra Storage MP X10000 system identified by ID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-stores/{TrustStoreId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7gettruststorebyid.md): Get Trust Store of a HPE Alletra Storage MP X10000 system identified by ID. A Trust Store represents a collection of trusted certificates.

## controllers

The controllers API allows the management of controller fleet.

### Get details of HPE Alletra Storage MP B10000 Nodes

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/controllers/devicetype4nodeslist.md): Get details of HPE Alletra Storage MP B10000 Nodes

### Get details of HPE Alletra Storage MP B10000 Node identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/controllers/devicetype4nodesgetbyid.md): Get details of HPE Alletra Storage MP B10000 Node identified by {id}

### Locate node of HPE Alletra Storage MP B10000  identified by {id}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/controllers/devicetype4nodeslocatebyid.md): Locate node of HPE Alletra Storage MP B10000 identified by {id}

### Get component performance statistics details of HPE Alletra Storage MP B10000 node idenfified by {nodeId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{nodeId}/component-performance-statistics](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/controllers/devicetype4nodecomponentperformancestatisticsget.md): Get component performance statistics details of HPE Alletra Storage MP B10000 node idenfified by {nodeId}

## enclosures

The Enclosure API provides endpoints for managing and configuring enclosures.

### Get all enclosures of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/enclosures/devicetype7getenclosures.md): Get all enclosures of a HPE Alletra Storage MP X10000 system

### Get Enclosure of a HPE Alletra Storage MP X10000 system identified by enclosureID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures/{enclosureId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/enclosures/devicetype7getenclosurebyid.md): Get Enclosure of HPE Alletra Storage MP X10000 system identified by enclosureID

### Edit settings of HPE Alletra Storage MP X10000 system Enclosure identified by {enclosureId}

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures/{enclosureId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/enclosures/devicetype7editenclosurebyid.md): Edit settings of HPE Alletra Storage MP X10000 system Enclosure identified by {enclosureId}

## encryption

The encryption API allows the actions on encryption.

### Encryption Backup Action on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/backup](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4backupactiononencryption.md): Encryption Backup Action on HPE Alletra Storage MP B10000 identified by {systemId}

### Check EKM configuration on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/checkekm](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4checkekmconfiguration.md): Check EKM configuration on HPE Alletra Storage MP B10000 identified by {systemId}

### Encryption Enable Action on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/enable](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4enableactiononencryption.md): Encryption Enable Action on HPE Alletra Storage MP B10000 identified by {systemId}

### Encryption Rekey Action on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/rekey](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4rekeyactiononencryption.md): Encryption Rekey Action on HPE Alletra Storage MP B10000 identified by {systemId}

### Encryption Restore Action on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/restore](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4restoreactiononencryption.md): Encryption Restore Action on HPE Alletra Storage MP B10000 identified by {systemId}

### Set EKM configuration on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/setekm](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4setekmconfiguration.md): Set EKM configuration on HPE Alletra Storage MP B10000 identified by {systemId}

### Set EKM configuration and Encryption Backup Action on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/setekm-backup](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/encryption/devicetype4setekmbackupactiononencryption.md): Set EKM configuration and Encryption Backup Action on HPE Alletra Storage MP B10000 identified by {systemId}

## jbofioms

The JBOF IOM API provides endpoints for managing and configuring JBOF IOMs.

### Get all JBOF IOMs of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/jbofioms](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/jbofioms/devicetype7getjbofioms.md): Get all JBOF IOMs of a HPE Alletra Storage MP X10000 system

### Get JBOF IOM of a HPE Alletra Storage MP X10000 system identified by jbofIomID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/jbofioms/{jbofiomId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/jbofioms/devicetype7getjbofiombyid.md): Get JBOF IOM of a HPE Alletra Storage MP X10000 system identified by jbofIomID

### Edit settings of a HPE Alletra Storage MP X10000 system JBOF IOM identified by jbofIomID

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/jbofioms/{jbofiomId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/jbofioms/devicetype7editjbofiombyid.md): Edit settings of a HPE Alletra Storage MP X10000 system JBOF IOM identified by jbofIomID

## object-notification-clients

The Object Notification Client API provides endpoints for managing and configuring object notification clients.

### Get all Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/object-notification-clients/devicetype7getstorageclusterobjectnotificationclientbysystemid.md): Get all Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {systemId}

### Add Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/object-notification-clients/devicetype7addstoragesystemobjectnotificationclientsettingsbyid.md): Add Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {systemId}

### Delete Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {clientId}

 - [DELETE /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients/{clientId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/object-notification-clients/devicetype7deletestoragesystemobjectnotificationclientsettingsbyid.md): Edit Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {clientId}

### Get Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {clientId}

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients/{clientId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/object-notification-clients/devicetype7getstorageclusterobjectnotificationclientbyid.md): Get Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {clientId}

### Edit Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {clientId}

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients/{clientId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/object-notification-clients/devicetype7editstoragesystemobjectnotificationclientsettingsbyid.md): Edit Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {clientId}

## ports

The ports API allows the management of ports.

### Get details of HPE Alletra Storage MP B10000 Ports

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4portslist.md): Get details of HPE Alletra Storage MP B10000 Ports

### Get details of performance metrics of host ports on storage system identified by {systemid}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports-performance](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4portsperformancehistoryget.md): Get details of performance metrics of host ports on storage system identified by {systemid}

### Get details of HPE Alletra Storage MP B10000 Port identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4portsgetbyid.md): Get details of HPE Alletra Storage MP B10000 Port identified by {id}

### Port enable disable identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4portenable.md): Port enable disable identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Clear the details of the ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/clear](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4portsclear.md): Clear the details of the ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Edit iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-iscsi](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4iscsiportedit.md): Edit iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Edit rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-rcip](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4rcipportedit.md): Edit rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Edit ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/fc](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4fcportedit.md): Edit ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Initialize the details of the ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/initialize](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4initialiseports.md): Initialize the details of the ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Ping iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/ping-iscsi](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4iscsiportping.md): Ping iscsi ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

### Ping rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/ping-rcip](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/ports/devicetype4rcipportping.md): Ping rcip ports identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}

## shelves

The shelves API allows the management of shelves.

### Get details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosure-cards](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurecardlist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {systemId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Connectors

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosure-connectors](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureconnectorslist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Connectors

### Get details of HPE Alletra Storage MP B10000 Enclosures

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureslist.md): Get details of HPE Alletra Storage MP B10000 Enclosures

### Get details of HPE Alletra Storage MP B10000 disks identified by {cageId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4diskslist.md): Get details of HPE Alletra Storage MP B10000 disks identified by {cageId}

### Get details of HPE Alletra Storage MP B10000 disk identified by {cageId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4disksgetbyid.md): Get details of HPE Alletra Storage MP B10000 disk identified by {cageId} and {id}

### Get details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {enclosureId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurecardslist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {enclosureId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Card identified by {enclosureId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurecardsgetbyid.md): Get details of HPE Alletra Storage MP B10000 Enclosure Card identified by {enclosureId} and {id}

### Locate IO Module of HPE Alletra Storage MP B10000 identified by {id}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurecardslocateiobyid.md): Locate IO Module of HPE Alletra Storage MP B10000 identified by {id}

### Get details of HPE Alletra Storage MP B10000 Enclosure Connectors identified by {enclosureId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureconnectorlist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Connectors identified by {enclosureId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Connector identified by {enclosureId} and {enclosureConnectorId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors/{enclosureConnectorId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureconnectorsgetbyid.md): Get details of HPE Alletra Storage MP B10000 Enclosure Connector identified by {enclosureId} and {enclosureConnectorId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Disks identified by {enclosureId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-disks](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurediskslist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Disks identified by {enclosureId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Disk identified by {enclosureId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-disks/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosuredisksgetbyid.md): Get details of HPE Alletra Storage MP B10000 Enclosure Disk identified by {enclosureId} and {id}

### Get details of HPE Alletra Storage MP B10000 Enclosure Powers identified by {enclosureId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-powers](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurepowerslist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Powers identified by {enclosureId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Power identified by {enclosureId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-powers/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosurepowersgetbyid.md): Get details of HPE Alletra Storage MP B10000 Enclosure Power identified by {enclosureId} and {id}

### Get details of HPE Alletra Storage MP B10000 Enclosure Sleds identified by {enclosureId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosuresledslist.md): Get details of HPE Alletra Storage MP B10000 Enclosure Sleds identified by {enclosureId}

### Get details of HPE Alletra Storage MP B10000 Enclosure Sled identified by {enclosureId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosuresledsgetbyid.md): Get details of HPE Alletra Storage MP B10000 Enclosure Sled identified by {enclosureId} and {id}

### Locate drive of HPE Alletra Storage MP B10000 identified by {id}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosuresledslocatedrivebyid.md): Locate drive of HPE Alletra Storage MP B10000 identified by {id}

### Get details of HPE Alletra Storage MP B10000 Enclosure identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosuresgetbyid.md): Get details of HPE Alletra Storage MP B10000 Enclosure identified by {id}

### Locate enclosure drive of HPE Alletra Storage MP B10000 identified by {id}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureslocatebyid.md): Locate enclosure drive of HPE Alletra Storage MP B10000 identified by {id}

### Edit details of HPE Alletra Storage MP B10000 Enclosure identified by {id}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4enclosureseditbyid.md): Edit details of HPE Alletra Storage MP B10000 Enclosure identified by {id}

### Get details of performance metrics of physical drives on storage system identified by {systemid}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/physicaldrives-performance](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/shelves/devicetype4physicaldriveperformancehistoryget.md): Get details of performance metrics of physical drives on storage system identified by {systemid}

## storage-nodes

The Storage Node API provides endpoints for managing and configuring storage nodes.

### Get all storage nodes of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-nodes/devicetype7getstoragenodes.md): Get all storage nodes of a HPE Alletra Storage MP X10000 system

### Get StorageNode of a HPE Alletra Storage MP X10000 system identified by storageNodeID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes/{storageNodeId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-nodes/devicetype7getstoragenodebyid.md): Get StorageNode of a HPE Alletra Storage MP X10000 system identified by storageNodeID

### Edit settings of a HPE Alletra Storage MP X10000 system Storage Node  identified by storageNodeID

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/storage-nodes/{storageNodeId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-nodes/devicetype7editstoragenodebyid.md): Edit settings of a HPE Alletra Storage MP X10000 system Storage Node identified by storageNodeID

## storage-systems

The storage-systems API allows the management of storage device.

### Get all HPE Alletra Storage MP B10000 storage systems

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemslist.md): Get all HPE Alletra Storage MP B10000 storage systems

### Get HPE Alletra Storage MP B10000 object identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemgetbyid.md): Get HPE Alletra Storage MP B10000 object identified by {id}

### Locate an HPE Alletra Storage MP B10000 system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemlocate.md): Locate an HPE Alletra Storage MP B10000 system

### Get capacity trend data for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/capacity-history](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemcapacityhistoryget.md): Get capacity trend data for an HPE Alletra Storage MP B10000 storage system

### Get system capacity for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/capacity-summary](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemcapacitysummaryget.md): Get system capacity for an HPE Alletra Storage MP B10000 storage system

### Get component performance statistics details for an HPE Alletra Storage MP B10000 storage system idenfified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/component-performance-statistics](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemcomponentperformancestatisticsget.md): Get component performance statistics details for an HPE Alletra Storage MP B10000 storage system idenfified by {systemId}

### Get licenses of the storage system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/licenses](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4licensesgetbyid.md): Get licenses of the storage system identified by {systemId}

### Get performance trend data for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/performance-history](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4systemperformancehistoryget.md): Get performance trend data for an HPE Alletra Storage MP B10000 storage system

### Get performance statistics for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/performance-statistics](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype4getsystemperformancestatistics.md): Get performance statistics for an HPE Alletra Storage MP B10000 storage system

### Get all HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7getstorageclusters.md): Get all HPE Alletra Storage MP X10000 system

### Get HPE Alletra Storage MP X10000 system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7getstorageclusterbyid.md): Get HPE Alletra Storage MP X10000 system identified by {systemId}

### Edit settings of HPE Alletra Storage MP X10000 system identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7editstoragesystemsettingsbyid.md): Edit settings of HPE Alletra Storage MP X10000 system identified by {systemId}

### Get capacity trend data for a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/capacity-history](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7systemcapacityhistoryget.md): Get capacity trend data for a HPE Alletra Storage MP X10000 system

### Get capacity summary for a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/capacity-summary](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7systemcapacitysummaryget.md): Get capacity summary for a HPE Alletra Storage MP X10000 system

### Get performance trend data for a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/performance-history](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7systemperformancehistoryget.md): Get performance trend data for a HPE Alletra Storage MP X10000 system

### Get SMTP settings of HPE Alletra Storage MP X10000 system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/smtp-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7getstorageclustersmtpsettingsbyid.md): Get SMTP settings of HPE Alletra Storage MP X10000 system identified by {systemId}

### Edit settings of HPE Alletra Storage MP X10000 system SMTP server identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/smtp-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7editstoragesystemsmtpsettingsbyid.md): Edit settings of HPE Alletra Storage MP X10000 system  SMTP server identified by {systemId}

### Get all storage systems

 - [GET /storage-fleet/v1alpha1/storage-systems](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/systemslist.md): Get all storage systems

### Get storage system object identified by {id}

 - [GET /storage-fleet/v1alpha1/storage-systems/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/systemgetbyid.md): Get storage system object identified by {id}

### Get all device types

 - [GET /storage-fleet/v1alpha1/storage-types](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/getdevicetype.md): Get all device types

## switches

The Switch API provides endpoints for managing and configuring switches.

### Get details of HPE Alletra Storage MP B10000 Switch ports

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switch-ports](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchportslist.md): Get details of HPE Alletra Storage MP B10000 Switch ports

### Get details of HPE Alletra Storage MP B10000 Switches

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switcheslist.md): Get details of HPE Alletra Storage MP B10000 Switches

### Get details of HPE Alletra Storage MP B10000 Switch identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchesgetbyid.md): Get details of HPE Alletra Storage MP B10000 Switch identified by {id}

### Locate switch of HPE Alletra Storage MP B10000 identified by {id}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchlocatebyid.md): Locate switch  of HPE Alletra Storage MP B10000 identified by {id}

### Get details of HPE Alletra Storage MP B10000 Switch Fans identified by switch id

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-fans](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchfanlist.md): Get details of HPE Alletra Storage MP B10000 Switch Fans identified by switch id

### Get details of HPE Alletra Storage MP B10000 Switch Fan identified by switchId} and Fan id

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-fans/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchfangetbyid.md): Get details of HPE Alletra Storage MP B10000 Switch Fan identified by switchId and Fan id

### Get details of HPE Alletra Storage MP B10000 Switch ports identified by {switchId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchportlist.md): Get details of HPE Alletra Storage MP B10000 Switch ports identified by {switchId}

### Get details of HPE Alletra Storage MP B10000 Switch Port identified by {switchId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchportgetbyid.md): Get details of HPE Alletra Storage MP B10000 Switch identified by {switchId} and {id}

### Get details of HPE Alletra Storage MP B10000 Switch power supplies identified by {switchId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ps](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchpslist.md): Get details of HPE Alletra Storage MP B10000 Switch power supplies identified by {switchId}

### Get details of HPE Alletra Storage MP B10000 Switch Power Supplies identified by {switchId} and {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ps/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype4switchpsgetbyid.md): Get details of HPE Alletra Storage MP B10000 Switch Power Supplies identified by {switchId} and {id}

### Get all switches of a HPE Alletra Storage MP X10000 system

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype7getswitches.md): Get all switches of a HPE Alletra Storage MP X10000 system

### Get Switch of a HPE Alletra Storage MP X10000 system identified by switchID

 - [GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches/{switchId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype7getswitchbyid.md): Get Switch of a HPE Alletra Storage MP X10000 system identified by switchID

### Edit HPE Alletra Storage MP X10000 system Switch identified by {switchId}

 - [PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches/{switchId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/switches/devicetype7editswitchbyid.md): Edit HPE Alletra Storage MP X10000 system Switch identified by {switchId}

## system-settings

The System Settings API allows the monitoring of System settings for the device.

### Get alert-contact details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4alertcontactslist.md): Get alert-contact details for an HPE Alletra Storage MP B10000 storage system

### Add Alert/Mail contact details

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4alertcontactscreate.md): Add Alert/Mail contact details

### Delete Alert/Email contact for HPE Alletra Storage MP B10000 storage system identified by {id}

 - [DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4alertcontactsdelete.md): Delete Alert/Email contact for HPE Alletra Storage MP B10000 storage system identified by {id}

### Get alert-contact details for an HPE Alletra Storage MP B10000 storage system identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4alertcontactsgetbyid.md): Get alert-contact details for an HPE Alletra Storage MP B10000 storage system identified by {id}

### Edit Alert/Email contact details of HPE Alletra Storage MP B10000 storage system identified by {id}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4alertcontactsupdate.md): Edit Alert/Email contact details of HPE Alletra Storage MP B10000 storage system identified by {id}

### Get array certificates by HPE Alletra Storage MP B10000

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4certificateslist.md): Get array certificates by HPE Alletra Storage MP B10000

### Create certificate on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4postcertificate.md): Create certificate on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get array certificates by HPE Alletra Storage MP B10000 identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4certificatesgetbyid.md): Get array certificates by HPE Alletra Storage MP B10000 identified by {id}

### Import certificate identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4putcertificate.md): Import certificate identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Delete certificates from HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/remove](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4removecertificates.md): Delete certificates from HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get CIM Network-Service details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/cim](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicecimget.md): Get CIM Network-Service details for an HPE Alletra Storage MP B10000 storage system

### Edit CIM network service configuration

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/cim](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicecimupdate.md): Edit CIM network service configuration

### Trigger a collection on the HPE Alletra Storage MP B10000 storage system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/collect-support-data](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4supportdatacollect.md): Trigger a collection on the HPE Alletra Storage MP B10000 storage system

### Set license of the storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/licenses](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4setlicense.md): Set license of the storage system identified by {systemId}

### Delete SMTP/mail server settings

 - [DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4mailsettingsdelete.md): Delete SMTP/mail server settings

### Get the system's SMTP/Mail server settigs

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4mailsettingsget.md): Get the system's SMTP/Mail server settigs

### Add SMTP/Mail server settigs

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4mailsettingsassociate.md): Add SMTP/Mail server settigs

### Edit SMTP/Mail server settigs

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4mailsettingsupdate.md): Edit SMTP/Mail server settigs

### Get Network-Settings details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networksettingsget.md): Get Network-Settings details for an HPE Alletra Storage MP B10000 storage system

### Post Network-Settings details for an HPE Alletra Storage MP B10000 storage system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networksettingsassociate.md): Post Network-Settings details for an HPE Alletra Storage MP B10000 storage system

### Get service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId} and {nodeId }

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{nodeId}/service-ports](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4nodeserviceportsgetbyid.md): Get service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId} and {nodeId }

### Get quorum witness configuration details from HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4getquorumwitness.md): Get quorum witness configuration details from HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Create quorum witness on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4postquorumwitness.md): Create quorum witness on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Delete quorum witness identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness/{replicationPartnerId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4deletequorumwitness.md): Delete quorum witness identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get details of quorum witness configured on replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness/{replicationPartnerId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4getquorumwitnesswithid.md): Get details of quorum witness configured on replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Edit quorum witness identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness/{replicationPartnerId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4putquorumwitness.md): Edit quorum witness identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get details of performance metrics of remote copy links on storage system identified by {systemid}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/remotecopylinks-performance](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4remotecopylinksperformancehistoryget.md): Get details of performance metrics of remote copy links on storage system identified by {systemid}

### Get details of replication partners on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4getreplicationpartners.md): Get details of replication partners on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Create replication partners on HPE Alletra Storage MP B10000 identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4postreplicationpartners.md): Create replication partners on HPE Alletra Storage MP B10000 identified by {systemId}

### Get details of replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/{replicationPartnerId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4getreplicationpartnerwithid.md): Get details of replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Edit replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/{replicationPartnerId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4putreplicationpartner.md): Edit replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 identified by {systemId}

### Delete replication partner from HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/remove](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4postremovereplicationpartners.md): Delete replication partner from HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/service-ports](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4nodeserviceportslist.md): Get service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId}

### Get SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrlist.md): Get SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system

### Add SNMP Manager settings

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrcreate.md): Add SNMP Manager settings

### Delete SNMP manager settings identified by {id}

 - [DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrdelete.md): Delete SNMP manager settings identified by {id}

### Get a specific SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrgetbyid.md): Get a specific SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system

### Edit SNMP Manager settings for the specified Id

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicesnmpmgrupdate.md): Edit SNMP Manager settings for the specified Id

### Get SNMP users

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-users](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4snmpuserslist.md): Get SNMP users

### Get SNMP users identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-users/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4snmpusersgetbyid.md): Get SNMP users identified by {id}

### Get support settings for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4supportsettingsget.md): Get support settings for an HPE Alletra Storage MP B10000 storage system

### Add support settings for an HPE Alletra Storage MP B10000 storage system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4supportsettingsassociate.md): Add support settings for an HPE Alletra Storage MP B10000 storage system

### Edit support settings for an HPE Alletra Storage MP B10000 storage system

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4supportsettingsupdate.md): Edit support settings for an HPE Alletra Storage MP B10000 storage system

### Get details of sustainability metrics of enclosure and system power supplies in Watts on storage system identified by {systemid}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/sustainability-metrics](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4enclosurepowerssustainability.md): Get details of sustainability metrics of enclosure and system power supplies in Watts on storage system identified by {systemid}

### Get the system settings configuration details

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4systemsettingslist.md): Get the system settings configuration details

### Edit system settings configuration

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4systemsettingsassociate.md): Edit system settings configuration. Only one type of system settings i.e. either "authMode or dateTime or installationSites or name or ntpAddresses or remoteSyslogSettings or srinfo or supportContact or systemParameters" is allowed to be configured at a time.

### Edit system settings configuration

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4systemsettingsupdate.md): Edit system settings configuration. Only one type of system settings i.e. either "authMode or dateTime or installationSites or name or ntpAddresses or remoteSyslogSettings or srinfo or supportContact or systemParameters" is allowed to be configured at a time.

### Get telemetry status for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/telemetry](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4telemetryget.md): Get telemetry status for an HPE Alletra Storage MP B10000 storage system

### Get certificates trusted by HPE Alletra Storage MP B10000

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4trustedcertificateslist.md): Get certificates trusted by HPE Alletra Storage MP B10000

### Add trusted certificates for HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4addtrustedcertificates.md): Add trusted certificates for HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get certificates trusted by HPE Alletra Storage MP B10000 identified by {id}

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4trustedcertificatesgetbyid.md): Get certificates trusted by HPE Alletra Storage MP B10000 identified by {id}

### Delete trusted certificates from HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates/remove](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4removetrustedcertificates.md): Delete trusted certificates from HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get VASA Network-Service details for a storage system Primera / Alletra 9K

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicevasaget.md): Get VASA Network-Service details for a storage system Primera / Alletra 9K

### Configures vasa service for the specified id.

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa/{vasaId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkservicevasaconfigure.md): Enables or disable vasa service  on a HPE Alletra Storage MP B10000 storage system

### Configures vasa service for the specified id.

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa/{vasaId}/services](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4networkserviceconfigurevasaservice.md): Enables, disable, updates the cert management mode for VASA services on an HPE Alletra Storage MP B10000 storage system. It also provides the ability to configure the batch parameters for VASA services and set up the second VASA Provider (VP) on a HPE Alletra Storage MP B10000 storage system from OS version 10.5.0 and later.

### Configure IP addresses for VASA Provider High Availability (VPHA) on a HPE Alletra Storage MP B10000 storage system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasaprovider](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vasaprovideraddressconfigure.md): Add a VASA Provider IP address on the specified node. After associating the VASA Provider (VP) to the specific node then this information is used to start second instance of the VP to achieve VPHA. This configuration will provide high availability of the connection between storage device and vSphere client and minimize service downtime during failures. Applicable for HPE Alletra Storage MP B10000 storage system with 10.5.0 version and later.

### Clear VASA Provider IP Address configuration on a HPE Alletra Storage MP B10000 storage system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasaprovider/clear](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vasaprovideraddressclear.md): Clear VASA Provider IP Address Configuration from a node at HPE Alletra Storage MP B10000 storage system. Applicable for HPE Alletra Storage MP B10000 storage system with 10.5.0 version and later.

### Get vCenter settings for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vmmanagersettingslist.md): Get vCenter settings for an HPE Alletra Storage MP B10000 storage system

### Add vCenter settings to HPE Alletra Storage MP B10000 storage system

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4postvcentersettings.md): Add vCenter settings to HPE Alletra Storage MP B10000 storage system

### Delete vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4deletevcentersettings.md): Delete vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Get vCenter setting detail for a given vCenter setting of a HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vmmanagersettingsgetbyid.md): Get vCenter setting detail for a given vCenter setting of a HPE Alletra Storage MP B10000 storage system

### Edit vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 identified by {systemId}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4putvcentersettings.md): Edit vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 identified by {systemId}

### Get vVol details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvol](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4vvolget.md): Get vVol details for an HPE Alletra Storage MP B10000 storage system

### Get Storage Container details for an HPE Alletra Storage MP B10000 storage system

 - [GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4storagecontainerget.md): Get Storage Container details for an HPE Alletra Storage MP B10000 storage system

### Delete storage container of HPE Alletra Storage MP B10000 storage system identified by {id}

 - [DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4storagecontainerdeletebyid.md): Delete storage container of HPE Alletra Storage MP B10000 storage system identified by {id}

### Edit storage container of HPE Alletra Storage MP B10000 storage system identified by {id}

 - [PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4storagecontainereditbyid.md): Edit storage container of HPE Alletra Storage MP B10000 storage system identified by {id}

## vvolscs

### Creates VMware storage container on HPE Alletra Storage MP B10000 storage system identified by {systemId}

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/vvolscs/devicetype4createvvolsc.md): Creates VMware storage container on HPE Alletra Storage MP B10000 storage system identified by {systemId}

### Attach host to storage container identified by {vvolscId} from HPE Alletra Storage MP B10000

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}/attach](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/vvolscs/devicetype4attachvolsc.md): Attach host to storage container identified by {volumeId} from HPE Alletra Storage MP B10000

### Detach host from storage container identified by {vvolscId} from HPE Alletra Storage MP B10000

 - [POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}/detach](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/vvolscs/devicetype4detachvolsc.md): Detach host from storage container identified by {volumeId} from HPE Alletra Storage MP B10000

