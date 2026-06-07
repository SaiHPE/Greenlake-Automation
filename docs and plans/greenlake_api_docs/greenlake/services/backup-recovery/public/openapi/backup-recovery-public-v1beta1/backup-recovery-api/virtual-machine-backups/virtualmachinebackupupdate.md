---
title: "PATCH /backup-recovery/v1beta1/virtual-machines/{id}/backups/{backup-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1beta1/backup-recovery-api/virtual-machine-backups/virtualmachinebackupupdate.md"
scraped_at: "2026-06-07T06:14:09.553680+00:00Z"
---

# Update a virtual machine backup.

Update attributes for a virtual machine backup.

Endpoint: PATCH /backup-recovery/v1beta1/virtual-machines/{id}/backups/{backup-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the virtual machine
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

  - `backup-id` (string, required)
    UUID string uniquely identifying the backup.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/merge-patch+json):

  - `description` (string)
    Brief description about the application backup.

  - `expiresAt` (string)
    Absolute value of time in UTC when the application backup expires.

  - `lockedUntil` (string)
    Absolute value of time in UTC until which the application backup remains locked.
    Example: "2020-04-03T05:03:08.900Z"

  - `name` (string)
    Name of the application backup.
    Example: "Nimble-VM1-backup"

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


