---
title: "POST /backup-recovery/v1beta1/protection-stores/{id}/reattach"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/protection-stores/cloudprotectionstorereattach.md"
scraped_at: "2026-06-07T06:14:06.001878+00:00Z"
---

# Reattach a Cloud Protection Store

Reattach a Cloud Protection Store.

Endpoint: POST /backup-recovery/v1beta1/protection-stores/{id}/reattach
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Protection Store.
    Example: "c9cdeb6b-24cb-43c1-828a-e8b1b050f3f4"

## Request fields (application/json):

  - `storageSystemId` (string)
    id of the Storage System (Protection Store Gateway or StoreOnce).
    Example: "2a1172be-4281-44f9-848b-9c3f86378b13"

  - `storageSystemType` (string)
    Type of the Storage System
    Enum: "PROTECTION_STORE_GATEWAY", "STOREONCE"

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


