---
title: "GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/devicetype7getaccesspolicybyid.md"
scraped_at: "2026-06-07T06:15:31.534122+00:00Z"
---

# Get single HPE Alletra Storage MP X10000 ObjectStore access policy

Get HPE Alletra Storage MP X10000 ObjectStore access policy identified by {policyId}

Endpoint: GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    A unique identifier assigned to each object service device
    Example: "8UW0002928"

  - `policyId` (string, required)
    A unique identifier assigned to each access policy created in the ObjectStore
    Example: "policy1"

## Query parameters:

  - `select` (string)
    A query to retrieve only the specified parameters. Use . to denote nested fields.
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier of the access policy resource
    Example: "123456"

  - `type` (string, required)
    Type of resource
    Example: "access-policy"

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

  - `name` (string)
    Name of the policy
    Example: "testPolicy"

  - `statement` (array)

  - `statement.action` (array)
    Specifies the action that is allowed or denied

  - `statement.condition` (object,null)

  - `statement.effect` (string)
    Specifies whether the statement results in an allow or deny

  - `statement.resource` (array,null)

  - `statement.sid` (string,null)
    Identifier of the statement
    Example: "bucket-policy1:readonly"

  - `systemUid` (string)
    Identifier of the storage system
    Example: "2FF70002AC0263D0"

  - `version` (string)
    Version of the policy
    Example: "2012-10-17"

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


