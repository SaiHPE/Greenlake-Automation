---
title: "PATCH /backup-recovery/v1alpha1/hypervisor-managers/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-public-v1alpha1/backup-recovery-api/hypervisor-managers/hypervisormanagerupdate.md"
scraped_at: "2026-06-07T06:13:58.918708+00:00Z"
---

# Update a hypervisor manager.

Update attributes for a hypervisor manager.

Endpoint: PATCH /backup-recovery/v1alpha1/hypervisor-managers/{id}
Version: 1.1.0
Security: bearer

## Path parameters:

  - `id` (string, required)
    UUID string uniquely identifying the hypervisor manager.
    Example: "9b4c14a6-3cd5-4907-97c4-cf44c5b641e4"

## Request fields (application/merge-patch+json):

  - `credentials` (object)
    Hypervisor server credentials.

  - `credentials.password` (string)
    Password used to access the hypervisor server.

  - `credentials.username` (string)
    Name of the user used to access the hypervisor server.

  - `description` (string)
    A brief description of the hypervisor manager.

  - `displayName` (string)
    User defined name for the hypervisor manager.
    Example: "myvcenter1"

  - `networkAddress` (string)
    An IP address or hostname or FQDN to address the hypervisor manager.
    Example: "192.168.0.1"

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


