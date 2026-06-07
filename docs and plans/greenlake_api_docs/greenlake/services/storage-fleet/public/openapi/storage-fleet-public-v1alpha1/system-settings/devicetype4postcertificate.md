---
title: "POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4postcertificate.md"
scraped_at: "2026-06-07T06:16:02.450762+00:00Z"
---

# Create certificate on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Create certificate on HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `type` (string, required)
    Type of certificate to create.
    Example: "csr"

  - `service` (string, required)
    Name of service the certificate is for.
    Enum: "QW_CLIENT", "QW_SERVER", "WSAPI", "CLI", "CIM", "VASA", "EKM_CLIENT", "SYSLOG_GEN_CLIENT", "SYSLOG_SEC_CLIENT", "UNIFIED_SERVER", "EKM_SERVER"

  - `authorityChain` (string)
    The authority chain for Quorum Witness server certificate.
    Example: "-----BEGIN CERTIFICATE REQUEST-----abc----END CERTIFICATE REQUEST-----"

  - `commonName` (string)
    CommonName for the certificate.
    Example: "hpe.com CA - Intermediate"

  - `country` (string)
    Two-letter code for the country where organization is located.
    Example: "IN"

  - `days` (integer)
    Number of days valid for the certificate.
    Example: 365

  - `keyLength` (integer)
    Key length for the certificate.
    Example: 2048

  - `locality` (string)
    Locality where organization is located.
    Example: "BLR"

  - `organization` (string)
    Organization for the certificate
    Example: "HPE"

  - `organizationUnit` (string)
    Division of organization handling the certificate.
    Example: "HPE Alletra Storage MP B10000"

  - `province` (string)
    Province where organization is located.
    Example: "Karnataka"

  - `subjectAltName` (object)
    Subject Alternative Name for the certificate.

  - `subjectAltName.dns` (string)
    DNS for Subject Alternative Name for the certificate
    Example: "7CE815P2BH"

  - `subjectAltName.email` (string)
    Email for Subject Alternative Name for the certificate
    Example: "abc@hpe.com"

  - `subjectAltName.ip` (string)
    IP Address for Subject Alternative Name for the certificate
    Example: "15.213.65.129"

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


