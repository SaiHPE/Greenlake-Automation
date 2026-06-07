---
title: "GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7singlebuckets.md"
scraped_at: "2026-06-07T06:15:32.306074+00:00Z"
---

# Get single HPE Alletra Storage MP X10000 ObjectStore bucket

Get HPE Alletra Storage MP X10000 ObjectStore bucket identified by {bucketId}

Endpoint: GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    A unique identifier assigned to each object service device
    Example: "8UW0002928"

  - `bucketId` (string, required)
    A unique identifier assigned to each bucket created in the ObjectStore
    Example: "bucket1"

## Query parameters:

  - `select` (string)
    A query to retrieve only the specified parameters. Use . to denote nested fields.
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier of the bucket resource
    Example: "id1"

  - `type` (string, required)
    Type of the resource

  - `bucketTags` (array,null)
    Tags for the bucket

  - `bucketTags.key` (string, required)
    Key of the Tag
    Example: "location"

  - `bucketTags.value` (string)
    Value for the Key
    Example: "us"

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system to which the resource belongs.
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `compression` (boolean)
    Field to check if compression is  enabled or disabled

  - `createdAt` (string)

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1sd"

  - `generation` (integer)

  - `name` (string)
    Name of the bucket
    Example: "myBucketName"

  - `notificationService` (string)
    Indicates whether the Notification Service is enabled for this bucket.
    Example: "DISABLED"

  - `notificationServiceConfiguration` (object,null)
    Event configurations for the bucket.

  - `objectLockConfiguration` (object,null)
    Locking details for the bucket

  - `objectLockConfiguration.objectLockEnabled` (string,null)
    Field to check if object lock is enabled
    Example: "Enabled"

  - `objectLockConfiguration.rule` (object,null)
    Rule for the object lock

  - `objectLockConfiguration.rule.defaultRetention` (object,null)
    Default retention period applied to new objects under the bucket’s object lock.

  - `objectLockConfiguration.rule.defaultRetention.days` (integer,null)
    Days for the retention
    Example: 1

  - `objectLockConfiguration.rule.defaultRetention.mode` (string,null)
    Mode for the retention
    Example: "GOVERNANCE"

  - `objectLockConfiguration.rule.defaultRetention.years` (integer,null)
    Years for the retention
    Example: 1

  - `systemUid` (string)
    Identifier of the storage system
    Example: "system1"

  - `versioning` (string)
    Indicates whether versioning is enabled for this bucket.
    Example: "Disabled"

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


