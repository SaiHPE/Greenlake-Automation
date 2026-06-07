---
title: "POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/certificates/createstorageclustercustomcertificate.md"
scraped_at: "2026-06-07T06:16:07.556613+00:00Z"
---

# Create a custom certificate for storage cluster

This API endpoint is to create a custom certificate for storage cluster

Endpoint: POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/custom-certificates
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the storage system
    Example: "2a0df0fe6f7dc7bb16000000000000000000004817"

## Request fields (application/json):

  - `name` (string, required)
    User provided name
    Example: "cert-1"

  - `customCertificatePolicyRef` (string, required)
    The name of the applicable Custom Certificate Policy.
    Example: "s3-default-certificate-policy"

  - `commonName` (string, required)
    Common name for the certificate subject.
    Example: "S3"

  - `organizationUnit` (string, required)
    Organisation unit for the certificate subject.

  - `organization` (string, required)
    Organisation for the certificate subject.
    Example: "HPE"

  - `locality` (string, required)
    Locality name for the certificate subject.
    Example: "MA"

  - `province` (string, required)
    Province/state name for the certificate subject.
    Example: "KA"

  - `country` (string, required)
    Country name for the certificate subject.
    Example: "IN"

  - `selfSigned` (boolean, required)
    Whether to create a self-signed certificate or not.
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


