---
title: "PATCH /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongroupupdate.md"
scraped_at: "2026-06-07T06:14:15.003046+00:00Z"
---

# Update an MSSQL database protection group.

Update attributes for an MSSQL database protection group.

Endpoint: PATCH /backup-recovery/v1beta1/mssql-database-protection-groups/{group-id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `group-id` (string, required)
    UUID string uniquely identifying the MSSQL databse protection group
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/merge-patch+json):

  - `description` (string)
    A brief description of the MSSQL database protection group.

  - `members` (array)
    Captures the list of databases that will be part of the protection group.

  - `members.resourceUri` (string)
    The uri of member database

  - `name` (string)
    A user-friendly name to identify the MSSQL database protection group.

  - `nativeAppInfo` (object)

  - `nativeAppInfo.excludeSystemDatabases` (boolean)
    True if system databases are to be excluded from native protection group of type instance

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


