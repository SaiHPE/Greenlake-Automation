---
title: "POST /backup-recovery/v1beta1/mssql-databases/{db-id}/restore"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-databases/mssqldatabaserestore.md"
scraped_at: "2026-06-07T06:14:15.800913+00:00Z"
---

# Restore an MSSQL database from snapshot or backup.

Restores a virtual machine from selected snapshot.

Endpoint: POST /backup-recovery/v1beta1/mssql-databases/{db-id}/restore
Version: 1.1.0
Security: bearer

## Path parameters:

  - `db-id` (string, required)
    UUID string uniquely identifying the MSSQL Database
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `restoreType` (string, required)
    Specifies the type of restore needs to be performed.
    Enum: "PARENT", "ALTERNATE"

  - `backupId` (string)
    UUID string uniquely identifying the backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `recoveryMode` (string)
    The recovery mode the database will be in at the end of restore operation
    Enum: "WITH_RECOVERY", "NO_RECOVERY"

  - `restoreUntil` (string)
    Time in UTC upto which the recovery needs to be done. This attribute is required only if restore from log backup is intended.
    Example: "2020-03-03T06:03:08.902Z"

  - `restoreWithTailLog` (boolean)
    Flag to indicate if the backup operation should backup the tail log

  - `snapshotId` (string)
    UUID string uniquely identifying the snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `targetDatabaseInfo` (object)
    Provides the details about target VM location, compute, etc These inputs are required only if the restore type is 'ALTERNATE'.

  - `targetDatabaseInfo.databaseFilePaths` (array)
    Details of source and target mappings for restoring database files.

  - `targetDatabaseInfo.databaseFilePaths.newPath` (string)
    Path of the database file in the target host

  - `targetDatabaseInfo.databaseFilePaths.originalPath` (string)
    Path of the source database file

  - `targetDatabaseInfo.instanceId` (string)
    The target instance onto which the new mssql database is to be hosted.

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


