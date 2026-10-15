---
title: "POST /backup-recovery/v1beta1/mssql-database-protection-groups"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/mssql-database-protection-groups/mssqldatabaseprotectiongroupcreate.md"
scraped_at: "2026-06-07T06:14:15.023048+00:00Z"
---

# Create a new MSSQL Database Protection Group.

Create an MSSQL Database Protection Group for data management.

Endpoint: POST /backup-recovery/v1beta1/mssql-database-protection-groups
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `name` (string, required)
    A user-friendly name to identify the MSSQL database protection group.

  - `protectionGroupType` (string, required)
    The type of the protection group. This can be 'NATIVE' for MSSQL application specific constructs such as an Availability Group, or 'CUSTOM' if its just a user provided collection of databases.
    Enum: "NATIVE", "CUSTOM"

  - `description` (string)
    A brief description of the MSSQL database protection group.

  - `members` (array)
    Captures the list of databases that will be part of the protection group.

  - `members.resourceUri` (string)
    The uri of member database

  - `nativeAppInfo` (object)
    Native group information for creating a native protection group

  - `nativeAppInfo.excludeSystemDatabases` (boolean)
    True if system databases are to be excluded from native protection group of type instance
    Example: true

  - `nativeAppInfo.id` (string)
    Unique identifier of the mssql native group when type is MSSQL_INSTANCE.

  - `nativeAppInfo.type` (string)
    Type of the native protection group.
    Enum: "AVAILABILITY_GROUP", "MSSQL_INSTANCE"

  - `nativeAppInfo.uid` (string)
    Unique identifier of the mssql native group when type is AVAILABILITY_GROUP.

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


