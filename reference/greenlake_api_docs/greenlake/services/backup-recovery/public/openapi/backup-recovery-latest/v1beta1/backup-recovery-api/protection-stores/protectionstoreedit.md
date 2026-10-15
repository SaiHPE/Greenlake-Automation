---
title: "PATCH /backup-recovery/v1beta1/protection-stores/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstoreedit.md"
scraped_at: "2026-06-07T06:14:17.434039+00:00Z"
---

# Modify a Protection Store

Modify a Protection Store.

Endpoint: PATCH /backup-recovery/v1beta1/protection-stores/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Protection Store.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

## Request fields (application/merge-patch+json):

  - `displayName` (string)
    The user-defined name for the Protection Store.

## Response 200 fields (application/json):

  - `id` (string, required)
    UUID string uniquely identifying the Protection Store.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `type` (string, required)
    The type of resource.

  - `createdAt` (string, required)
    UTC time when the Protection Store was created.
    Example: "2019-07-21T17:32:28Z"

  - `updatedAt` (string, required)
    UTC time when the Protection Store was last updated.
    Example: "2019-07-21T17:32:28Z"

  - `cloudStoreAddress` (array)
    List of URLs for the storage provisioned for the Cloud Protection Store.
    Example: ["https://cosm-9d7ab727-38c2-43ac-938d-99b9bf6d2e08.s3.us-east-1.amazonaws.com"]

  - `connectedState` (string)
    The connected state of the Protection Store. The store is DISCONNECTED if its no longer associated with a Storage System.
    Enum: "CONNECTED", "DISCONNECTED"

  - `consoleUri` (string)
    The URI for console screen that displays this object.

  - `customerId` (string)
    The customer application identifier.
    Example: "9b4c14a63cd5490797c4cf44c5b641e4"

  - `dataOrchestratorInfo` (array)

  - `dataOrchestratorInfo.displayName` (string)
    User-defined name of the Data Orchestrator.
    Example: "DO-1"

  - `dataOrchestratorInfo.id` (string)
    UUID string uniquely identifying the Data Orchestrator.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f399"

  - `dataOrchestratorInfo.resourceUri` (string)
    The 'self' reference resource URI to the Data Orchestrator

  - `displayName` (string)
    The user-defined name for the Protection Store.
    Example: "cloud_store_SOD5057LHR"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `maxCapacityInBytes` (integer)
    Maximum capacity of the Protection Store in bytes. This is applicable only for On-premises Protection Stores.
    Example: 2407653459860

  - `name` (string)
    The system-defined name for the Protection Store. This will be the name of the Catalyst store on the Storage System.

  - `protectionStoreType` (string)
    Type of the Protection Store.
    Enum: "ON_PREMISES", "CLOUD"

  - `resourceUri` (string)
    The 'self' reference resource URI for the Protection Store.
    Example: "/backup-recovery/v1beta1/protection-stores/{id}"

  - `sizeOnDiskInBytes` (integer)
    Consumed capacity in bytes of the recovery points in Protection Store.
    Example: 2407653459860

  - `state` (string)
    The current state of the Protection Store.
    Enum: "OFFLINE", "ONLINE", "READ_ONLY", "NOT_READY", "STORE_FAILURE"

  - `stateReason` (string)
    Summary reason for the current state of the Protection Store.

  - `status` (string)
    The current status of the Protection Store.
    Enum: "OK", "ERROR", "WARNING"

  - `storageLocationInfo` (object)
    Details of the Storage Location for Cloud Protection Store

  - `storageLocationInfo.id` (string)
    String uniquely identifying the Storage Location.
    Example: "aws:ap-southeast-3"

  - `storageLocationInfo.name` (string)
    A system specified name for the resource.
    Example: "Jakarta - AWS"

  - `storageLocationInfo.resourceUri` (string)
    The 'self' reference resource URI to the Storage Location.

  - `storageSystemInfo` (object)
    Describes the Storage System hosting the Protection Store.

  - `storageSystemInfo.displayName` (string)
    The user-defined name of the Storage System.
    Example: "SOD5057LHR"

  - `storageSystemInfo.id` (string)
    UUID string uniquely identifying the Storage System.
    Example: "19Z1HYVZD5057LHR"

  - `storageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `storageSystemInfo.type` (string)
    Type of Storage System.
    Enum: "PROTECTION_STORE_GATEWAY", "STOREONCE"

  - `userDataStoredInBytes` (integer)
    Total size of the recovery points in bytes stored in the Protection Store.
    Example: 2407653459860

  - `region` (string)
    The region in which the Cloud Protection Store is created.

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


