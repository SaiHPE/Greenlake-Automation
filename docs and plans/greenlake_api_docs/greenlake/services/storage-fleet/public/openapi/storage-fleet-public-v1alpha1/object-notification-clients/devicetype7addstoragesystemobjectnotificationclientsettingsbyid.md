---
title: "POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/object-notification-clients/devicetype7addstoragesystemobjectnotificationclientsettingsbyid.md"
scraped_at: "2026-06-07T06:15:56.105007+00:00Z"
---

# Add Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {systemId}

Add Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {systemId}

Endpoint: POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the Storage system
    Example: "USE603C8P1"

## Request fields (application/json):

  - `identifier` (string,null, required)
    Unique identifier to represent endpoint configuration.
    Example: "kafka_buckets_fianance_topic_endpoint"

  - `hosts` (array,null, required)
    List of broker endpoints.

  - `authnType` (string,null, required)
    User should specify authentication mechanism to use.
    Enum: "SASL"

  - `tls` (boolean,null, required)
    User should specify 'true' to enable TLS connectivity to the Kafka broker(s).
    Example: true

  - `clientCert` (string,null)
    Client certificate.
    Example: "Certificate"

  - `clientType` (string,null)
    ClientType of broker. Possible values are Producer or Consumer.
    Example: "Producer"

  - `comment` (string,null)
    A comment to associate with the configuration.
    Example: "Comment"

  - `queueLimit` (integer,null)
    Specify the maximum limit for undelivered event messages for a bucket
    Example: 1000

  - `saslMechanism` (string,null)
    SASL mechanism to use for authenticating to the Kafka broker(s).
    Enum: "PLAIN", "SHA256", "SHA512"

  - `saslPassword` (string,null)
    Password for SASL authentication.
    Example: "passwrf"

  - `saslUsername` (string,null)
    User name for SASL authentication.
    Example: "kafka_admin_x"

  - `trustStore` (string,null)
    TrustStore certificate.
    Example: "Certificate"

  - `type` (string,null)
    Type of broker. We will support only Kafka for now.
    Example: "Kafka"

  - `verifyPeer` (boolean,null)
    Verify Peer.
    Example: true

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


