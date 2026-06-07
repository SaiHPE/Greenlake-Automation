---
title: "PATCH /private-cloud-business/v1beta1/vm-provisioning-policies/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/private-cloud-business-api/vm-provisioning-policies/vmprovisioningpolicyedit.md"
scraped_at: "2026-06-07T06:15:37.621544+00:00Z"
---

# Update VM provisioning policy by policy id

Update attributes of the specified VM provisioning policy

Endpoint: PATCH /private-cloud-business/v1beta1/vm-provisioning-policies/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    Unique identifier of a VM provisioning policy

## Request fields (application/merge-patch+json):

  - `description` (string)
    A brief description of the VM provisioning policy.

  - `protectionPolicy` (object)
    Protection policy.

  - `protectionPolicy.id` (string, required)
    An identifier for the protection policy.

  - `protectionPolicy.name` (string, required)
    Name of the protection policy.

  - `protectionPolicy.description` (string)
    The description of the vm provisioning policy.

  - `protectionPolicy.effectiveFromDateTime` (string)
    Time in UTC at which the protection policy assignment will be effective from.
    Example: "2020-03-03T05:03:08.902Z"

  - `protectionPolicy.overrides` (object)
    Protection policy advance settings.

  - `protectionPolicy.overrides.consistency` (string, required)
    Specifies whether to create crash consistent or application consistent snapshot. CRASH_CONSISTENT_ON_FAILURE: If an application consistent snapshot fails for any reason, with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `protectionPolicy.overrides.backupGranularity` (string, required)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `storageType` (string)
    Storage Type of the system.
    Enum: "Alletra dHCI"

  - `volumeInfo` (object)
    DHCI volume attributes

  - `volumeInfo.allFlash` (boolean)
    This indicates whether all flash is enabled or not.

  - `volumeInfo.conversionType` (string)
    Conversion type of the volume
    Enum: "CONVERSIONTYPE_THIN", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2"

  - `volumeInfo.dataReduction` (boolean)
    Specifies if data reduction capability is enabled. Data reduction is a combination of both deduplication and compression.

  - `volumeInfo.deduplication` (boolean)
    Specifies if dedupe is enabled for volumes created. Deduplication is a process that eliminates excessive copies of data and significantly decreases storage capacity requirements.

  - `volumeInfo.encryption` (object)
    Encryption for the volumes.

  - `volumeInfo.encryption.cipher` (string, required)
    Encryption cipher for the volumes.
    Enum: "AES_256_XTS", "None"

  - `volumeInfo.encryption.provider` (string)
    Library that provides the ability to encrypt sensitive data.

  - `volumeInfo.encryption.scope` (string)
    Enables one to manage encryption at the level of an individual blob or container.
    Enum: "Volume", "Pool", "Group", "None"

  - `volumeInfo.qos` (object)
    Quality of service.

  - `volumeInfo.qos.perfMbpsLimit` (number, required)
    Throughput limit for this volume in MB/s. If limit_mbps is not specified when a volume is created, or if limit_mbps is set to -1, then the volume has no MBPS limit. MBPS limit should be in range [1, 4294967294] or -1 for unlimited. If both limit_iops and limit_mbps are specified, limit_mbps must not be hit before limit_iops. In other words, IOPS and MBPS limits should honor limit_iops &lt;= ((limit_mbps MB/s * 2^20 B/MB) / block_size B). Signed 64-bit integer.
    Example: 1200

  - `volumeInfo.qos.perfIopsLimit` (number, required)
    IOPS limit for this volume. If limit_iops is not specified when a volume is created, or if limit_iops is set to -1, then the volume has no IOPS limit. If limit_iops is not specified while creating a clone, IOPS limit of parent volume will be used as limit. IOPS limit should be in range [256, 4294967294] or -1 for unlimited. If both limit_iops and limit_mbps are specified, limit_mbps must not be hit before limit_iops. In other words, IOPS and MBPS limits should honor limit_iops &lt;= ((limit_mbps MB/s * 2^20 B/MB) / block_size B). Signed 64-bit integer.
    Example: 1200

  - `volumeInfo.snapshotAllocWarning` (integer)
    Sets a snapshot space allocation limit. The snapshot space of the virtual volume is prevented from growing beyond the indicated percentage of the virtual volume size. A warning alert is generated when the reserved snapshot space of the virtual volume exceeds the indicated percentage of the virtual volume size.

  - `volumeInfo.userAllocWarning` (integer)
    Sets a user space allocation limit. The user space of the TPVV(thin provisioned virtual volume) is prevented from growing beyond the indicated percentage of the virtual volume size. A warning alert is generated when the user data space of the TPVV exceeds the specified percentage of the virtual volume size.

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


