---
title: "POST /backup-recovery/v1beta1/datastores/{id}/restore"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/datastores/datastorerestorefromcopy.md"
scraped_at: "2026-06-07T06:14:02.757636+00:00Z"
---

# Restore a datastore from snapshot or a backup.

Restores a datastore from selected snapshot or backup.

Endpoint: POST /backup-recovery/v1beta1/datastores/{id}/restore
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the datastore
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `restoreType` (string, required)
    Specifies the type of restore that needs to be performed.
    Enum: "PARENT", "ALTERNATE"

  - `snapshotId` (string, required)
    UUID string uniquely identifying the snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `backupId` (string, required)
    UUID string uniquely identifying the backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `targetDatastoreInfo` (object)
    Provides the details about the target datastore location and other inputs to create a new datastore in case of an alternate restore. These inputs are required only if the restore type is 'ALTERNATE'. Parameters are optional and values default to parent datastore details.

  - `targetDatastoreInfo.clusterId` (string)
    The target hypervisor cluster onto which the new datastore is hosted.
Either hostId or clusterId has to be provided as input.
Both can not be specified at the same time.

  - `targetDatastoreInfo.description` (string)
    Description for the new datastore.

  - `targetDatastoreInfo.folderId` (string)
    The identifier of the folder into which the datastore needs to be placed.

  - `targetDatastoreInfo.hostId` (string)
    The target hypervisor host onto which the new datastore is hosted.

  - `targetDatastoreInfo.hypervisorManagerId` (string)
    Specifies the destination hypervisor manager.

  - `targetDatastoreInfo.name` (string)
    The name of the new datastore. If this is no specific
name given a default unique name would be assigned.
    Example: "snap-ae36"

  - `targetDatastoreInfo.powerOnVmsAfterRestore` (boolean)
    Specifies whether to power on VMs after restore.

  - `targetDatastoreInfo.storageInfo` (object)
    Target storage information required to provision the new storage,
required only in case of alternate datastore restore.

  - `targetDatastoreInfo.storageInfo.storageSystemId` (string, required)
    Target storage system where the new volumes will be provisioned
in case of alternate restore.

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


