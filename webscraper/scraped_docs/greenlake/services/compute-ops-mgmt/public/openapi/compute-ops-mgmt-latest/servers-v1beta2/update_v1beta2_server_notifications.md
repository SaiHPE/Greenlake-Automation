---
title: "PUT /compute-ops-mgmt/v1beta2/servers/{id}/notifications"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/servers-v1beta2/update_v1beta2_server_notifications.md"
scraped_at: "2026-06-07T06:15:11.914761+00:00Z"
---

# Update event and health notifications for a server

### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

Event notification selections are made such that each selection increases the scope
of the set of events that will be included.
The order of event selections from minimum to maximum scope are

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

Note that healthNotification is not part of the event notification set and
may be set independently.

Since each selection builds on the previous one, there exists a hierarchy
between selections that must be maintained.  The table below shows which
notification combinations are valid.  All other combinations will result in an
HTTP 400 error

| criticalNotification  | criticalNonServiceNotification  | warningNotification  |
|:---------------------:|:-------------------------------:|:--------------------:|
| False                 | False                           | False                |
| True                  | False                           | False                |
| True                  | True                            | False                |
| True                  | True                            | True                 |

### Initial values
All values are initially false with the result being that no notifications will be sent.


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: PUT /compute-ops-mgmt/v1beta2/servers/{id}/notifications
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)

## Request fields (application/json):

  - `criticalNotification` (boolean, required)

  - `criticalNonServiceNotification` (boolean,null)

  - `warningNotification` (boolean,null)

  - `healthNotification` (boolean,null)

## Response 200 fields (application/json):

  - `serverId` (string)

  - `criticalNotification` (boolean)

  - `criticalNonServiceNotification` (boolean,null)

  - `warningNotification` (boolean,null)

  - `healthNotification` (boolean,null)

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 406 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 415 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `errorDetails` (array)
    Additional detailed information about the error


