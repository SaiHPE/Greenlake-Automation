---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/devicetype7gettrustcertificates.md"
scraped_at: "2026-06-07T06:16:08.108649+00:00Z"
---

# Get all custom certificates of a HPE Alletra Storage MP X10000 system

Get all custom certificates of a HPE Alletra Storage MP X10000 system

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the storage system
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

  - `filter` (string)
    Lucene query to filter Certificate by Key.
    Example: "id eq 2a0df0fe6f7dc7bb16000000000000000000004007"

  - `sort` (string)
    Data query to sort Certificate resource by Key.
    Example: "id desc"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Identifier of the Storage system certificate. Filter, Sort
    Example: "default.trust-certificate-0"

  - `items.type` (string, required)
    Type of the resource.
    Example: "trust-certificate"

  - `items.apiVersion` (string,null)
    API version of the resource.
    Example: "sc.hpe.com/v1"

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
    Customer ID for the Storage system certificate. Filter, Sort
    Example: "ab1c23456d78901e23fghijk456lm7no"

  - `items.generation` (integer,null)
    Generation. Filter, Sort
    Example: 1692945579

  - `items.kind` (string,null)
    Kind of the resource.
    Example: "TrustCertificate"

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.status` (object,null)
    The current status of the Trust Certificate.

  - `items.status.certificate` (object,null)
    The installed Certificate.

  - `items.status.certificate.certificate` (string,null)
    The installed certificate.

  - `items.status.certificate.expirationTime` (string,null)
    Time when the certificate expires
    Example: "2025-03-11T13:17:55Z"

  - `items.status.certificate.issuer` (string,null)
    The Issuer distinguished name
    Example: "CN=S3,DC=corp,DC=company,DC=COM"

  - `items.status.certificate.name` (string,null)
    The certificate name
    Example: "certificate-1"

  - `items.status.certificate.selfSigned` (boolean,null)
    Whether it is a self-signed certificate or not.
    Example: true

  - `items.status.certificate.subject` (string,null)
    The Subject distinguished name
    Example: "CN=S3,DC=corp,DC=company,DC=COM"

  - `items.status.certificate.thumbprint` (string,null)
    Set to the hash of the leaf certificate

  - `items.status.certificate.validFrom` (string,null)
    Time from which the certificate is valid
    Example: "2025-01-11T13:17:55Z"

  - `items.status.observedGeneration` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 1692945579

  - `items.status.ready` (boolean,null)
    Used to determine when a controller has brought its resource into compliance with the specification. When a resource is created, by default, its ready attribute should be initiatlized to False, then changed to True when the current status of the resource matches its specification.
    Example: true

  - `items.status.trustStoreRef` (string,null)
    The name of the TrustStore.  Filter, Sort
    Example: "Audit-default-trust-store"

  - `items.systemId` (string,null)
    Identifier of the Storage system to which the certificate belongs. Filter, Sort
    Example: "1AB234CDEF"

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


