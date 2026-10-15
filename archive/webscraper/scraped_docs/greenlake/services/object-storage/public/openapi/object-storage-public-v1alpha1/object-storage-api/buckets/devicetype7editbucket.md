---
title: "PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7editbucket.md"
scraped_at: "2026-06-07T06:15:32.227610+00:00Z"
---

# Edit the properties of an existing bucket in HPE Alletra Storage MP X10000 ObjectStore

Edit bucket properties in HPE Alletra Storage MP X10000 ObjectStore identified by {systemId} and {bucketId}

Endpoint: PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    A unique identifier assigned to each object service device
    Example: "8UW0002928"

  - `bucketId` (string, required)
    A unique identifier assigned to each bucket created in the ObjectStore
    Example: "bucket1"

## Request fields (application/json):

  - `bucketTags` (array,null)
    Tags for the bucket

  - `bucketTags.key` (string, required)
    Key of the Tag
    Example: "location"

  - `bucketTags.value` (string)
    Value for the Key
    Example: "us"

  - `compression` (string)
    Field to enable or disable compression for the bucket
    Enum: "ENABLED", "DISABLED"

  - `notificationService` (string)
    Enables or disables the bucket’s Notification Service.
    Enum: "ENABLED", "DISABLED"

  - `notificationServiceConfiguration` (object,null)
    Event configurations for the bucket.

  - `objectLockConfiguration` (object,null)
    Object Locking details for the bucket

  - `objectLockConfiguration.objectLockEnabled` (string)
    Field to enable object lock
    Enum: "ENABLED"

  - `objectLockConfiguration.rule` (object,null)
    Rule for the object lock

  - `objectLockConfiguration.rule.defaultRetention` (object,null)
    Default retention period applied to new objects under the bucket’s object lock.

  - `objectLockConfiguration.rule.defaultRetention.days` (integer,null)
    Days for the retention
    Example: 1

  - `objectLockConfiguration.rule.defaultRetention.mode` (string,null)
    Mode for the retention
    Enum: "GOVERNANCE", "COMPLIANCE"

  - `objectLockConfiguration.rule.defaultRetention.years` (integer,null)
    Years for the retention
    Example: 1

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


