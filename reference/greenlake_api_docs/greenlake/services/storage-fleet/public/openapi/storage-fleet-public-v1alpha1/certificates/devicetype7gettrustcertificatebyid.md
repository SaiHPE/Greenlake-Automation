---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates/{certificateId}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/certificates/devicetype7gettrustcertificatebyid.md"
scraped_at: "2026-06-07T06:15:54.427627+00:00Z"
---

# Get Trust Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID

Get Trust Certificate of a HPE Alletra Storage MP X10000 system identified by certificateID

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/trust-certificates/{certificateId}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the Storage system
    Example: "USE603C8P1"

  - `certificateId` (string, required)
    ID unique to certificate created in objectstore
    Example: "certificate-1"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Identifier of the Storage system certificate.
    Example: "default.trust-certificate-0"

  - `type` (string, required)
    Type of the resource.
    Example: "trust-certificate"

  - `apiVersion` (string,null)
    API version of the resource.
    Example: "sc.hpe.com/v1"

  - `associatedLinks` (array,null)
    Associated Links Details

  - `associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `associatedLinks.type` (string)
    Resource Name

  - `commonResourceAttributes` (object,null)

  - `commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `customerId` (string,null)
    Customer ID for the Storage system certificate.
    Example: "ab1c23456d78901e23fghijk456lm7no"

  - `generation` (integer,null)
    Generation.
    Example: 1692945579

  - `kind` (string,null)
    Kind of the resource.
    Example: "TrustCertificate"

  - `resourceUri` (string,null)
    Link to the object URI

  - `status` (object,null)
    The current status of the Trust Certificate.

  - `status.certificate` (object,null)
    The installed Certificate.

  - `status.certificate.certificate` (string,null)
    The installed certificate.

  - `status.certificate.expirationTime` (string,null)
    Time when the certificate expires
    Example: "2025-03-11T13:17:55Z"

  - `status.certificate.issuer` (string,null)
    The Issuer distinguished name
    Example: "CN=S3,DC=corp,DC=company,DC=COM"

  - `status.certificate.name` (string,null)
    The certificate name
    Example: "certificate-1"

  - `status.certificate.selfSigned` (boolean,null)
    Whether it is a self-signed certificate or not.
    Example: true

  - `status.certificate.subject` (string,null)
    The Subject distinguished name
    Example: "CN=S3,DC=corp,DC=company,DC=COM"

  - `status.certificate.thumbprint` (string,null)
    Set to the hash of the leaf certificate

  - `status.certificate.validFrom` (string,null)
    Time from which the certificate is valid
    Example: "2025-01-11T13:17:55Z"

  - `status.observedGeneration` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 1692945579

  - `status.ready` (boolean,null)
    Used to determine when a controller has brought its resource into compliance with the specification. When a resource is created, by default, its ready attribute should be initiatlized to False, then changed to True when the current status of the resource matches its specification.
    Example: true

  - `status.trustStoreRef` (string,null)
    The name of the TrustStore.
    Example: "Audit-default-trust-store"

  - `systemId` (string,null)
    Identifier of the Storage system to which the certificate belongs.
    Example: "1AB234CDEF"

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


