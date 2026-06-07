---
title: "GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7listbuckets.md"
scraped_at: "2026-06-07T06:15:32.066463+00:00Z"
---

# Get all buckets for HPE Alletra Storage MP X10000 ObjectStore

Retrieves a list of buckets associated with a specific HPE Alletra Storage MP X10000 ObjectStore. The results can be filtered, sorted, and paginated using query parameters to customize the response based on your requirements.

Endpoint: GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets
Version: 1.1.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    A unique identifier assigned to each object service device
    Example: "8UW0002928"

## Query parameters:

  - `filter` (string)
    oData query to filter bucket by Key.
    Example: "id eq \"abc\""

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    A query to retrieve only the specified parameters. Use . to denote nested fields.
    Example: "id"

  - `sort` (string)
    A list of properties defining the sort order. This takes a single property name followed
by the direction to sort in, separated by a space.
The supported properties are systemUid, id and generation. If not specified,
the default behaviour is to sort by generation. The supported directions are
asc and desc for ascending and descending respectively.
    Example: "id desc"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier of the bucket resource
    Example: "id1"

  - `items.type` (string, required)
    Type of the resource

  - `items.bucketTags` (array,null)
    Tags for the bucket

  - `items.bucketTags.key` (string, required)
    Key of the Tag
    Example: "location"

  - `items.bucketTags.value` (string)
    Value for the Key
    Example: "us"

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system to which the resource belongs.
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.compression` (boolean)
    Field to check if compression is  enabled or disabled

  - `items.createdAt` (string)

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1sd"

  - `items.generation` (integer)

  - `items.name` (string)
    Name of the bucket
    Example: "myBucketName"

  - `items.notificationService` (string)
    Indicates whether the Notification Service is enabled for this bucket.
    Example: "DISABLED"

  - `items.notificationServiceConfiguration` (object,null)
    Event configurations for the bucket.

  - `items.objectLockConfiguration` (object,null)
    Locking details for the bucket

  - `items.objectLockConfiguration.objectLockEnabled` (string,null)
    Field to check if object lock is enabled
    Example: "Enabled"

  - `items.objectLockConfiguration.rule` (object,null)
    Rule for the object lock

  - `items.objectLockConfiguration.rule.defaultRetention` (object,null)
    Default retention period applied to new objects under the bucket’s object lock.

  - `items.objectLockConfiguration.rule.defaultRetention.days` (integer,null)
    Days for the retention
    Example: 1

  - `items.objectLockConfiguration.rule.defaultRetention.mode` (string,null)
    Mode for the retention
    Example: "GOVERNANCE"

  - `items.objectLockConfiguration.rule.defaultRetention.years` (integer,null)
    Years for the retention
    Example: 1

  - `items.systemUid` (string)
    Identifier of the storage system
    Example: "system1"

  - `items.versioning` (string)
    Indicates whether versioning is enabled for this bucket.
    Example: "Disabled"

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


