---
title: "POST /backup-recovery/v1beta1/volume-protection-groups/{id}/backups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/volume-protection-group-backups/vpgbackupcreate.md"
scraped_at: "2026-06-07T06:14:10.167910+00:00Z"
---

# Create a backup copy of a Volume Protection Group.

Create a backup copy of a Volume Protection Group.

Endpoint: POST /backup-recovery/v1beta1/volume-protection-groups/{id}/backups
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the Volume Protection Group.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `name` (string, required)
    Name of the application backup.
    Example: "vpg-backup"

  - `backupType` (string, required)
    Enum: "BACKUP", "CLOUD_BACKUP"

  - `sourceCopyInfo` (object, required)

  - `sourceCopyInfo.id` (string, required)
    A UUID string uniquely identifying the source copy
from which the backup will be performed.
    Example: "d0e48314-730a-11ea-b496-48452098762c"

  - `sourceCopyInfo.type` (string, required)
    The type of resource
    Enum: "SNAPSHOT", "BACKUP"

  - `protectionStoreId` (string, required)
    UUID string uniquely identifying the protection store object.
    Example: "2a1172be-4281-44f9-848b-9c3f86378b13"

  - `description` (string)
    Brief description about the application backup.

  - `expireAfter` (object)
    Copy expiration attribute, which specifies the expiration for the artifacts created.

  - `expireAfter.unit` (string)
    Accepted units
    Enum: "HOURS", "DAYS", "WEEKS", "MONTHS", "YEARS"

  - `expireAfter.value` (integer)
    Expiration value

  - `lockFor` (object)
    Retention attribute, which specifies the retention period for the artifacts created. Artifacts are locked for deletion for the specified period of time.

  - `lockFor.value` (integer)
    Retention value

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


