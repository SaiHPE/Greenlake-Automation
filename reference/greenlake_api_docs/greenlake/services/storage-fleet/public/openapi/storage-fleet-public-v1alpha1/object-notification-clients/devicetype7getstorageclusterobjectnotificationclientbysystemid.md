---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/object-notification-clients/devicetype7getstorageclusterobjectnotificationclientbysystemid.md"
scraped_at: "2026-06-07T06:15:56.088411+00:00Z"
---

# Get all Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {systemId}

Get all Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the Storage system
    Example: "USE603C8P1"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `filter` (string)
    Lucene query to filter systems by Key.
    Example: "NAME eq g1a1"

  - `sort` (string)
    Lucene query to sort systems by Key.
    Example: "name desc"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique identifier for the Storage system.Filter, Sort
    Example: "ASHBFY6567YGHJ"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.apiVersion` (string,null)
    API version Details.
    Example: "sc.hpe.com/v1"

  - `items.associatedBuckets` (array,null)
    Associated Bucket detail for Storage system Object Notification Clients.

  - `items.associatedBuckets.id` (string)
    Id of the bucket associated with the object notification client.
    Example: "d17450f0-d543-47e1-a8b5-1e629726248b-100003"

  - `items.associatedBuckets.name` (string,null)
    Name of the bucket associated with the object notification client
    Example: "bucket1"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    CustomerID for the Storage system.Filter, Sort
    Example: "ASHBFDJHFB6567YGHJ"

  - `items.generation` (integer,null)
    The most recent specification that has been observed by the controller. Filter, Sort
    Example: 1690045300

  - `items.kind` (string,null)
    Kind of the resource
    Example: "smtpSettings"

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.status` (object,null)

  - `items.status.config` (object,null)

  - `items.status.config.authnType` (string,null)
    Authentication type.Possible values SASL.
    Example: "SASL"

  - `items.status.config.clientCert` (string,null)
    Client certificate.
    Example: "example cert"

  - `items.status.config.clientType` (string,null)
    Type of notification client. Values can be either Producer or Consumer.
    Example: "Producer"

  - `items.status.config.comment` (string,null)
    A comment to associate with the configuration.
    Example: "Comment"

  - `items.status.config.hosts` (array,null)
    List of broker endpoints.

  - `items.status.config.queueLimit` (integer,null)
    Specify the maximum limit for undelivered event messages for a bucket
    Example: 1000

  - `items.status.config.saslMechanism` (string,null)
    SASL mechanism to use for authenticating to the Kafka broker(s).
    Example: "PLAIN"

  - `items.status.config.saslUsername` (string,null)
    User name for SASL authentication.
    Example: "kafka_admin_x"

  - `items.status.config.tls` (boolean,null)
    TLS connectivity to the Kafka broker(s).
    Example: true

  - `items.status.config.trustStore` (string,null)
    Ca certificate.
    Example: "TrustStore"

  - `items.status.config.type` (string,null)
    Type of broker. We will support only Kafka for now.
    Example: "Kafka"

  - `items.status.config.verifyPeer` (boolean,null)
    Trust server TLS without verification
    Example: true

  - `items.status.lastModifiedTime` (string,null)
    Last Modified time
    Example: "2025-03-18T20:52:30Z"

  - `items.status.name` (string,null)
    Unique identifier to represent endpoint configuration.
    Example: "kafka_buckets_fianance_topic_endpoint"

  - `items.status.observedGeneration` (integer,null)
    observed Generation
    Example: 1234

  - `items.status.ready` (boolean,null)
    Status of the resource
    Example: true

  - `items.systemId` (string,null)
    Identifier of the Storage system. Filter, Sort
    Example: "USE603C8P1"

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


