---
title: "POST /backup-recovery/v1beta1/application-hosts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/backup-recovery/public/openapi/backup-recovery-latest/v1beta1/backup-recovery-api/application-hosts/applicationhostcreate.md"
scraped_at: "2026-06-07T06:14:13.317996+00:00Z"
---

# Register a new Application Host.

Register the Application Host for data management.

Endpoint: POST /backup-recovery/v1beta1/application-hosts
Version: 1.1.0
Security: bearer

## Request fields (application/json):

  - `networkAddress` (string, required)
    An IP address or hostname or FQDN to address the host

  - `credentials` (object, required)
    Application host credentials.

  - `credentials.password` (string)
    Password used to access the application host

  - `credentials.username` (string)
    Name of the user used to access the application host

  - `description` (string)
    A brief description of the application host as provided by the user during registration.

  - `name` (string)
    The host name as reported by the host.

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


