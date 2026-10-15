---
title: "POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/remove"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public/openapi/block-storage-public-v1alpha1/volume-sets/devicetype4removeprotectionpolicies.md"
scraped_at: "2026-06-07T06:14:26.648218+00:00Z"
---

# Remove protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

Remove protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}

Endpoint: POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/remove
Version: 1.0.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    ID of the applicationset
    Example: "e9d353bf98fc1a6bdb90b824e3ca14b5"

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Request fields (application/json):

  - `policies` (array, required)
    List of protection policies to be removed

  - `policies.remote` (object)
    Remote protection to be removed

  - `policies.remote.partnerId` (string, required)
    Replication partner ID where remote protection is created
    Example: "29ee132316dc4b05a4805dba13e495ab"

  - `policies.removeOnlySchedules` (boolean)
    Remove only schedules and retain remote protection
    Example: true

  - `policies.removeSchedules` (array)
    List of protection schedules to be removed

  - `policies.removeSchedules.id` (string, required)
    Protection schedule ID
    Example: "12ab132316dc4b05a4805dba13e495xy"

  - `policies.secondaryRemote` (object)
    Secondary remote protection to be removed

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


