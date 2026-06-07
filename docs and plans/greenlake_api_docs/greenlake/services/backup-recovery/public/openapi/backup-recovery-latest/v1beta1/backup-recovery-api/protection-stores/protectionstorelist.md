---
title: "GET /backup-recovery/v1beta1/protection-stores"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-stores/protectionstorelist.md"
scraped_at: "2026-06-07T06:14:17.300516+00:00Z"
---

# Get details of all the Protection Stores

List all the Protection Stores.

Endpoint: GET /backup-recovery/v1beta1/protection-stores
Version: 1.1.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    The number of items to skip before starting to collect the result set

  - `limit` (integer)
    The numbers of items to return

  - `filter` (string)
    The filter query parameter is used to filter the set of resources returned in the response.

The returned set of resources will match the criteria in the filter query parameter.

A comparison compares a property name to a literal. The comparisons supported are the following:

- “eq” : Is a property equal to value. Valid for number, boolean and string properties
- “gt” : Is a property greater than a value. Valid for number or string timestamp properties
- “lt” : Is a property less than a value. Valid for number or string timestamp properties
- “in” : Is a value in a property (that is an array of strings)

Filters are supported on following attributes:

- protectionStoreType
- storageSystemInfo/id
- storageSystemInfo/displayName

Example:

GET ./protection-stores?filter=storageSystemInfo/displayName eq 'SOD5057LHR'

  - `sort` (string)
    Comma separated list of properties defining the sort order

  - `select` (string)
    The select query parameter is used to limit the properties returned in the GET response.

Multiple properties can be specified to be returned. The server will only return the set of properties requested by the client.

Example:

GET ./protection-stores?select=storageSystemInfo/displayName,status'

## Response 200 fields (application/json):

  - `count` (integer, required)
    Total number of records returned.

  - `items` (array, required)

  - `items.id` (string, required)
    UUID string uniquely identifying the Protection Store.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

  - `items.type` (string, required)
    The type of resource.

  - `items.createdAt` (string, required)
    UTC time when the Protection Store was created.
    Example: "2019-07-21T17:32:28Z"

  - `items.updatedAt` (string, required)
    UTC time when the Protection Store was last updated.
    Example: "2019-07-21T17:32:28Z"

  - `items.cloudStoreAddress` (array)
    List of URLs for the storage provisioned for the Cloud Protection Store.
    Example: ["https://cosm-9d7ab727-38c2-43ac-938d-99b9bf6d2e08.s3.us-east-1.amazonaws.com"]

  - `items.connectedState` (string)
    The connected state of the Protection Store. The store is DISCONNECTED if its no longer associated with a Storage System.
    Enum: "CONNECTED", "DISCONNECTED"

  - `items.consoleUri` (string)
    The URI for console screen that displays this object.

  - `items.customerId` (string)
    The customer application identifier.
    Example: "9b4c14a63cd5490797c4cf44c5b641e4"

  - `items.dataOrchestratorInfo` (array)

  - `items.dataOrchestratorInfo.displayName` (string)
    User-defined name of the Data Orchestrator.
    Example: "DO-1"

  - `items.dataOrchestratorInfo.id` (string)
    UUID string uniquely identifying the Data Orchestrator.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f399"

  - `items.dataOrchestratorInfo.resourceUri` (string)
    The 'self' reference resource URI to the Data Orchestrator

  - `items.displayName` (string)
    The user-defined name for the Protection Store.
    Example: "cloud_store_SOD5057LHR"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.maxCapacityInBytes` (integer)
    Maximum capacity of the Protection Store in bytes. This is applicable only for On-premises Protection Stores.
    Example: 2407653459860

  - `items.name` (string)
    The system-defined name for the Protection Store. This will be the name of the Catalyst store on the Storage System.

  - `items.protectionStoreType` (string)
    Type of the Protection Store.
    Enum: "ON_PREMISES", "CLOUD"

  - `items.resourceUri` (string)
    The 'self' reference resource URI for the Protection Store.
    Example: "/backup-recovery/v1beta1/protection-stores/{id}"

  - `items.sizeOnDiskInBytes` (integer)
    Consumed capacity in bytes of the recovery points in Protection Store.
    Example: 2407653459860

  - `items.state` (string)
    The current state of the Protection Store.
    Enum: "OFFLINE", "ONLINE", "READ_ONLY", "NOT_READY", "STORE_FAILURE"

  - `items.stateReason` (string)
    Summary reason for the current state of the Protection Store.

  - `items.status` (string)
    The current status of the Protection Store.
    Enum: "OK", "ERROR", "WARNING"

  - `items.storageLocationInfo` (object)
    Details of the Storage Location for Cloud Protection Store

  - `items.storageLocationInfo.id` (string)
    String uniquely identifying the Storage Location.
    Example: "aws:ap-southeast-3"

  - `items.storageLocationInfo.name` (string)
    A system specified name for the resource.
    Example: "Jakarta - AWS"

  - `items.storageLocationInfo.resourceUri` (string)
    The 'self' reference resource URI to the Storage Location.

  - `items.storageSystemInfo` (object)
    Describes the Storage System hosting the Protection Store.

  - `items.storageSystemInfo.displayName` (string)
    The user-defined name of the Storage System.
    Example: "SOD5057LHR"

  - `items.storageSystemInfo.id` (string)
    UUID string uniquely identifying the Storage System.
    Example: "19Z1HYVZD5057LHR"

  - `items.storageSystemInfo.resourceUri` (string)
    Reference to resource.

  - `items.storageSystemInfo.type` (string)
    Type of Storage System.
    Enum: "PROTECTION_STORE_GATEWAY", "STOREONCE"

  - `items.userDataStoredInBytes` (integer)
    Total size of the recovery points in bytes stored in the Protection Store.
    Example: 2407653459860

  - `items.region` (string)
    The region in which the Cloud Protection Store is created.

  - `offset` (integer)
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


