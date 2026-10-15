---
title: "POST /backup-recovery/v1beta1/volume-protection-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongroupcreate.md"
scraped_at: "2026-06-07T06:14:08.779285+00:00Z"
---

# Create a new Volume Protection Group.

Create the Volume Protection Group for data management.

Endpoint: POST /backup-recovery/v1beta1/volume-protection-groups
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `assets` (array)
    List of asset's. Required in case of custom vpg type.

  - `assets.id` (string)
    UUID string uniquely identifying the asset.

  - `description` (string)
    A brief description of the Protection Group.

  - `nativeGroupInfo` (object)

  - `nativeGroupInfo.id` (string)
    UUID string uniquely identifying the native group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `nativeGroupInfo.name` (string)
    Name of the native group.
    Example: "volume protection native group."

  - `storageSystemInfo` (object)
    Information about storage system of the volumes.

  - `storageSystemInfo.id` (string)
    UUID string uniquely identifying the storage system.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `volumeProtectionGroupType` (string)
    The type of the Protection Group. This can be Native for storage system specific constructs and Custom if its just a collection of assets (Volume).
    Enum: "NATIVE", "CUSTOM"

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


