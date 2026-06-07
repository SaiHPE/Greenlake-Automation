---
title: "POST /backup-recovery/v1beta1/virtual-machines/{id}/restore-disks"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machines/virtualmachinedisksrestore.md"
scraped_at: "2026-06-07T06:14:07.796282+00:00Z"
---

# Restore one or more disks of a virtual machine from snapshot or backup.

Restore one or more disks of a virtual machine.

Endpoint: POST /backup-recovery/v1beta1/virtual-machines/{id}/restore-disks
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the virtual machine
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/json):

  - `snapshotId` (string, required)
    UUID string uniquely identifying the snapshot. Mandatory if the restore if from snapshot.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `restoreType` (string, required)
    Specifies the type of restore that needs to be performed.
    Enum: "PARENT", "ALTERNATE"

  - `backupId` (string, required)
    UUID string uniquely identifying the backup. Mandatory if the restore is from a backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `restoreDiskDetails` (array)

  - `restoreDiskDetails.recoveryPointDiskDetails` (object)

  - `restoreDiskDetails.recoveryPointDiskDetails.diskLabel` (string)
    Label of the disk in the recovery point.
    Example: "Hard disk 1"

  - `restoreDiskDetails.vmDiskDetails` (object)

  - `restoreDiskDetails.vmDiskDetails.diskLabel` (string)
    Label of the source disk.
    Example: "Hard disk 1"

  - `targetVmId` (string)
    Identifier of the target VM where disks needs to be restored to.
This is optional. By default restores are performed to the original VM.
This provides an option to the user to restore disks to a different VM.
This identifier can not be a id of deleted VM.

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


