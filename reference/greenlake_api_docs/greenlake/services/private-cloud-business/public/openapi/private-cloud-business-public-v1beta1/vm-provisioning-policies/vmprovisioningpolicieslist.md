---
title: "GET /private-cloud-business/v1beta1/vm-provisioning-policies"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/private-cloud-business/public/openapi/private-cloud-business-public-v1beta1/vm-provisioning-policies/vmprovisioningpolicieslist.md"
scraped_at: "2026-06-07T06:15:39.040418+00:00Z"
---

# Get a list of VM provisioning policies

Returns a list of VM provisioning policies according to the given query
parameters for paging, filtering, and sorting.

Endpoint: GET /private-cloud-business/v1beta1/vm-provisioning-policies
Version: 1.1.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to omit from the beginning of the result set.
Use offset in conjunction with limit for pagination. 
For example,  "offset=30&limit=10" indicates the fourth page of 10 items.
    Example: 30

  - `limit` (integer)
    The maximum number of items to include in the response.
Use offset in conjunction with limit for pagination. 
For example, "offset=30&limit=10" indicates the fourth page of 10 items.
    Example: 10

  - `filter` (string)
    An expression to filter the results.
Filtering is supported with following attributes:
 * name
 * id 
 * timestamp
 * clusterid
 * deduplication
 * allFlash
 * encryption.cipher
 * associatedvmid
 * associatedvmname
    Example: "name eq 'vmpp'"

  - `sort` (string)
    A comma separated list of properties to sort by, followed by a direction
indicator ("asc" or "desc").
    Example: "name asc"

  - `select` (string)
    A list of properties to include in the response.
    Example: "id,name"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the VM provisioning policy.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `items.type` (string, required)
    The type of resource.

  - `items.name` (string, required)
    A user friendly name to identify the VM provisioning policy.
    Example: "myProvisioningPolicy"

  - `items.storageType` (string, required)
    Storage Type of the system.
    Enum: "Alletra dHCI"

  - `items.associatedObjects` (array, required)
    Objects that the VM provisioning policy should be associated with.

  - `items.associatedObjects.clusterId` (string, required)
    Identifier of the system cluster.

  - `items.associatedObjects.clusterName` (string, required)
    Name of the system cluster.

  - `items.associatedObjects.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.associatedObjects.resourceUri` (string)
    The URI reference for this resource.

  - `items.associatedObjects.associatedDatastores` (array)
    datastores that the VM provisioning policy should be associated with.

  - `items.associatedObjects.associatedDatastores.id` (string)
    Identifier of the Associated datastore

  - `items.associatedObjects.associatedDatastores.name` (string)
    Name of the Associated datastore

  - `items.associatedObjects.associatedDatastores.type` (string)
    Type of the Associated datastore

  - `items.associatedObjects.associatedVmCount` (integer)
    number of associated VMs

  - `items.associatedObjects.associatedVms` (array)
    Objects that the VM provisioning policy should be associated with.

  - `items.associatedObjects.associatedVms.id` (string)
    Identifier of the Associated VM

  - `items.associatedObjects.associatedVms.name` (string)
    Name of the Associated VM

  - `items.associatedObjects.storageProfileId` (string)
    An identifier for the storage profile.

  - `items.createdAt` (string)

  - `items.customerId` (string)
    The customer application identifier

  - `items.description` (string)
    A brief description of the VM provisioning policy.

  - `items.performancePolicy` (object)
    Performance policy with identifier.

  - `items.performancePolicy.id` (string)
    An identifier for the performance policy.

  - `items.protectionPolicy` (object)
    Protection policy.

  - `items.protectionPolicy.id` (string, required)
    An identifier for the protection policy.

  - `items.protectionPolicy.name` (string, required)
    Name of the protection policy.

  - `items.protectionPolicy.description` (string)
    The description of the vm provisioning policy.

  - `items.protectionPolicy.effectiveFromDateTime` (string)
    Time in UTC at which the protection policy assignment will be effective from.
    Example: "2020-03-03T05:03:08.902Z"

  - `items.protectionPolicy.overrides` (object)
    Protection policy advance settings.

  - `items.protectionPolicy.overrides.consistency` (string, required)
    Specifies whether to create crash consistent or application consistent snapshot. CRASH_CONSISTENT_ON_FAILURE: If an application consistent snapshot fails for any reason, with this option it will then take a crash consistent snapshot and continue.
    Enum: "CRASH", "APPLICATION", "CRASH_CONSISTENT_ON_FAILURE"

  - `items.protectionPolicy.overrides.backupGranularity` (string, required)
    Applicable only to backup copies. Specifies granularity at which the backup is created. The user can specify whether to create volume based backups or application Change Block Tracking (CBT) based backups.
    Enum: "VOLUME", "VMWARE_CBT"

  - `items.resourceUri` (string)
    The self reference for this resource.

  - `items.updatedAt` (string)

  - `items.volumeInfo` (object)
    DHCI volume attributes

  - `items.volumeInfo.allFlash` (boolean)
    This indicates whether all flash is enabled or not.

  - `items.volumeInfo.conversionType` (string)
    Conversion type of the volume
    Enum: "CONVERSIONTYPE_THIN", "CONVERSIONTYPE_V1", "CONVERSIONTYPE_V2"

  - `items.volumeInfo.dataReduction` (boolean)
    Specifies if data reduction capability is enabled. Data reduction is a combination of both deduplication and compression.

  - `items.volumeInfo.deduplication` (boolean)
    Specifies if dedupe is enabled for volumes created. Deduplication is a process that eliminates excessive copies of data and significantly decreases storage capacity requirements.

  - `items.volumeInfo.encryption` (object)
    Encryption for the volumes.

  - `items.volumeInfo.encryption.cipher` (string, required)
    Encryption cipher for the volumes.
    Enum: "AES_256_XTS", "None"

  - `items.volumeInfo.encryption.provider` (string)
    Library that provides the ability to encrypt sensitive data.

  - `items.volumeInfo.encryption.scope` (string)
    Enables one to manage encryption at the level of an individual blob or container.
    Enum: "Volume", "Pool", "Group", "None"

  - `items.volumeInfo.qos` (object)
    Quality of service.

  - `items.volumeInfo.qos.perfMbpsLimit` (number, required)
    Throughput limit for this volume in MB/s. If limit_mbps is not specified when a volume is created, or if limit_mbps is set to -1, then the volume has no MBPS limit. MBPS limit should be in range [1, 4294967294] or -1 for unlimited. If both limit_iops and limit_mbps are specified, limit_mbps must not be hit before limit_iops. In other words, IOPS and MBPS limits should honor limit_iops &lt;= ((limit_mbps MB/s * 2^20 B/MB) / block_size B). Signed 64-bit integer.
    Example: 1200

  - `items.volumeInfo.qos.perfIopsLimit` (number, required)
    IOPS limit for this volume. If limit_iops is not specified when a volume is created, or if limit_iops is set to -1, then the volume has no IOPS limit. If limit_iops is not specified while creating a clone, IOPS limit of parent volume will be used as limit. IOPS limit should be in range [256, 4294967294] or -1 for unlimited. If both limit_iops and limit_mbps are specified, limit_mbps must not be hit before limit_iops. In other words, IOPS and MBPS limits should honor limit_iops &lt;= ((limit_mbps MB/s * 2^20 B/MB) / block_size B). Signed 64-bit integer.
    Example: 1200

  - `items.volumeInfo.snapshotAllocWarning` (integer)
    Sets a snapshot space allocation limit. The snapshot space of the virtual volume is prevented from growing beyond the indicated percentage of the virtual volume size. A warning alert is generated when the reserved snapshot space of the virtual volume exceeds the indicated percentage of the virtual volume size.

  - `items.volumeInfo.userAllocWarning` (integer)
    Sets a user space allocation limit. The user space of the TPVV(thin provisioned virtual volume) is prevented from growing beyond the indicated percentage of the virtual volume size. A warning alert is generated when the user data space of the TPVV exceeds the specified percentage of the virtual volume size.

  - `offset` (integer, required)
    The number of items to skip before starting to collect the result set

  - `total` (integer)
    Total number of documents matching filter criteria.

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


