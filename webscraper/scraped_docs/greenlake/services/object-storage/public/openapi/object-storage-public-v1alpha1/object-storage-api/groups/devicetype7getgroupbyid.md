---
title: "GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/groups/devicetype7getgroupbyid.md"
scraped_at: "2026-06-07T06:15:32.851215+00:00Z"
---

# Get single group details for HPE Alletra Storage MP X10000 ObjectStore

Get single group details for HPE Alletra Storage MP X10000 ObjectStore identified by {groupId}

Endpoint: GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `groupId` (string, required)
    A unique identifier assigned to each group created in the ObjectStore
    Example: "testGroup"

  - `systemId` (string, required)
    A unique identifier assigned to each object service device
    Example: "8UW0002928"

## Query parameters:

  - `select` (string)
    A query to retrieve only the specified parameters. Use . to denote nested fields.
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier of the group resource
    Example: "MINIO162_Group"

  - `type` (string, required)
    Type of the resource

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

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1sd"

  - `generation` (integer)

  - `members` (array)

  - `name` (string)
    Example: "NewGroup1"

  - `policy` (string)

  - `status` (string)
    Example: "enabled"

  - `systemUid` (string)
    Identifier of the storage system
    Example: "MINIO162"

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


