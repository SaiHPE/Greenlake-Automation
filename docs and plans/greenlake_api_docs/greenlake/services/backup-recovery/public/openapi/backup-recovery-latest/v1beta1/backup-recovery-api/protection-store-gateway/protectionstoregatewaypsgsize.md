---
title: "POST /backup-recovery/v1beta1/protection-store-gateways/{id}/sizer"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaypsgsize.md"
scraped_at: "2026-06-07T06:14:12.601176+00:00Z"
---

# Returns the resource requirements that would be needed to resize an existing Protection Store Gateway.

Returns the resource requirements that would be needed to resize an existing Protection Store Gateway. This API doesn't perform any modifications to the Protection Store Gateway. To implement the modifications a call to POST /backup-recovery/v1beta1/protection-store-gateways/{id}/resize should be made.

Endpoint: POST /backup-recovery/v1beta1/protection-store-gateways/{id}/sizer
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the object
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

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


