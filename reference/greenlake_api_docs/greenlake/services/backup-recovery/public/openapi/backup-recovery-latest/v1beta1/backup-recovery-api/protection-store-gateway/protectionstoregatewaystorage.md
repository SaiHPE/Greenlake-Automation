---
title: "POST /backup-recovery/v1beta1/protection-store-gateways/{id}/resize"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/protection-store-gateway/protectionstoregatewaystorage.md"
scraped_at: "2026-06-07T06:14:11.951053+00:00Z"
---

# Reconfigures the CPU, memory and storage requirements of the Protection Store Gateway.

Reconfigure the CPU, memory and storage requirements of the Protection Store Gateway.

Endpoint: POST /backup-recovery/v1beta1/protection-store-gateways/{id}/resize
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    The UUID of the object
    Example: "c1a0eb78-41a0-4151-93b2-f057ffeca3f3"

## Request fields (application/json):

  - `datastoreIds` (array)
    IDs of datastores PSG should use. Including existing ones
    Example: ["aaaaaaa8-aaa4-aaa4-aaa4-aaaaaaaaaa12","aaaaaaa8-aaa4-bbb4-aaa4-aaaaaaaaaa12"]

  - `override` (object)
    Override automatic VM resource configuration with a fixed configuration.

  - `override.cpu` (number)
    Number of vCPU cores.
    Example: 8

  - `override.ramInGiB` (number)
    Amount of RAM in GiB.
    Example: 24

  - `override.storageInTiB` (number)
    Total storage capacity (TiB) of the Protection Store Gateway.
    Example: 2

  - `maxInCloudDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the Cloud Protection Stores.
    Example: 3

  - `maxInCloudRetentionDays` (number)
    The maximum retention period for cloud backups in days.
    Example: 5

  - `maxOnPremDailyProtectedDataInTiB` (number)
    The maximum total size of the assets that is expected to be protected each day in the On-Prem Protection Store.
    Example: 5

  - `maxOnPremRetentionDays` (number)
    The maximum retention period for local backups in days.
    Example: 5

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

## Response 412 fields (application/json):

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


