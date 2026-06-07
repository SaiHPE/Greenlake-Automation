---
title: "POST /virtualization/v1beta1/datastores"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/virtualization/public/openapi/virtualization-public-v1beta1/datastores/createds.md"
scraped_at: "2026-06-07T06:16:31.418013+00:00Z"
---

# Create datastore

Create datastore

Endpoint: POST /virtualization/v1beta1/datastores
Version: 1.2.0
Security: bearer

## Request fields (application/json):

  - `name` (string, required)
    Name of datastore to be created

  - `datastoreType` (string, required)
    Supported datastore types are VMFS or vVOL
    Enum: "VMFS", "VVOL"

  - `sizeInBytes` (integer, required)
    Size of the datastore in bytes

  - `targetHypervisorClusterId` (string, required)
    Target Hypervisor Cluster ID

  - `storageSystemId` (string, required)
    Storage System ID

  - `provisioningPolicyId` (string)
    Unique identifier of a provisioning policy.

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


