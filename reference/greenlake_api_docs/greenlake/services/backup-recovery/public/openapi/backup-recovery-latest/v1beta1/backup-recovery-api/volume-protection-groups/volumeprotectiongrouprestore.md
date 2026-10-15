---
title: "POST /backup-recovery/v1beta1/volume-protection-groups/{id}/restore"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/volume-protection-groups/volumeprotectiongrouprestore.md"
scraped_at: "2026-06-07T06:14:19.676228+00:00Z"
---

# Restores a Volume Protection Group from snapshot or backup.

Restores a Volume Protection Group from selected snapshot or backup.

Endpoint: POST /backup-recovery/v1beta1/volume-protection-groups/{id}/restore
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `individualBackupIds` (array)
    UUIDs of the individual backups on volumes. Required in case of granular restore from backup.

  - `individualSnapshotIds` (array)
    UUIDs of the individual snapshots on volumes. Required in case of granular restore from snapshot.

  - `restoreType` (string)
    Specifies the type of restore to be performed. Alternate restore is only supported from backups.
    Enum: "PARENT", "ALTERNATE"

  - `targetStorageSystemId` (string)
    UUID string uniquely identifying the storage system. Applicable only in case of alternate restore.
    Example: "6a38acc7-e470-4ed7-b141-ca9509672dac"

  - `vpgBackupId` (string)
    UUID string uniquely identifying the Volume Protection Group backup.

  - `vpgSnapshotId` (string)
    UUID string uniquely identifying the Volume Protection Group snapshot.

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


