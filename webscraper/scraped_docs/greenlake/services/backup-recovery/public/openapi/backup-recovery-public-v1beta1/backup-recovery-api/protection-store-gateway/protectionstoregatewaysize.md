---
title: "POST /backup-recovery/v1beta1/protection-store-gateway-sizer"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaysize.md"
scraped_at: "2026-06-07T06:13:59.260261+00:00Z"
---

# Returns the resource requirements that would be needed for a Protection Store Gateway.

Returns the resource requirements that would be needed for a Protection Store Gateway. This API doesn't create the Protection Store Gateway. To create the Protection Store Gateway a call to POST /protection-store-gateways should be made.

Endpoint: POST /backup-recovery/v1beta1/protection-store-gateway-sizer
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `maxInCloudDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the Cloud Protection Stores.
    Example: 2

  - `maxInCloudRetentionDays` (number)
    The maximum retention period for cloud backups in days.
    Example: 2

  - `maxOnPremDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the On-Prem Protection Store.
    Example: 2

  - `maxOnPremRetentionDays` (number)
    The maximum retention period for local backups in days.
    Example: 2

## Response 200 fields (application/json):

  - `iops` (number)
    IOPs that the underlying storage system must support to achieve the desired throughput.
    Example: 2

  - `ramInGiB` (number)
    Amount of RAM in GiB required.
    Example: 2

  - `storageInTiB` (number)
    Total size (TiB) of datastores that the Protection Store Gateway requires.
    Example: 2

  - `vCpu` (number)
    Number of vCPU cores required.
    Example: 2

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

## Response 409 fields (application/json):

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

  - `invalidReasons` (array)
    Reasons why the input values are invalid.

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


