---
title: "POST /backup-recovery/v1beta1/protection-stores"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/protection-stores/protectionstorecreate.md"
scraped_at: "2026-06-07T06:14:05.489708+00:00Z"
---

# Create a Protection Store

Create a Protection Store.

Endpoint: POST /backup-recovery/v1beta1/protection-stores
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `displayName` (string)
    The user-defined name for the Protection Store.

  - `protectionStoreType` (string)
    Type of the Protection Store.
    Enum: "ON_PREMISES", "CLOUD"

  - `storageLocationId` (string)
    The storage location identifier for creating the cloud protection store.

  - `storageSystemId` (string)
    id of the Storage System (Protection Store Gateway or StoreOnce).
    Example: "2a1172be-4281-44f9-848b-9c3f86378b13"

  - `storageSystemType` (string)
    Type of the Storage System
    Enum: "PROTECTION_STORE_GATEWAY", "STOREONCE"

  - `region` (string)
    The region in which the cloud protection store should be created. Deprecated - use storageLocationId instead

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


