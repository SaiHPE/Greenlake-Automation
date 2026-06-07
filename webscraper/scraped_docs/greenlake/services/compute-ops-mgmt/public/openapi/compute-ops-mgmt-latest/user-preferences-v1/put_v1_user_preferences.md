---
title: "PUT /compute-ops-mgmt/v1/user-preferences/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/put_v1_user_preferences.md"
scraped_at: "2026-06-07T06:15:12.752863+00:00Z"
---

# Update user preferences

### Purpose
When a server is added to Compute Ops Management, these attributes will be used to set the
initial email notification subscription choices for event and daily health email notifications.

For criticalNotification, criticalNonServiceNotification, and warningNotification, 
each selection increases the scope of the set of events that will be included.
The order of event selections from minimum to maximum scope are:

  * criticalNotification - Events that are marked as service events.  These events
  may have severity levels of 'warning' or 'critical'
  * criticalNonServiceNotification - Events that are not service events but have
  a severity level of 'critical'
  * warningNotification - Events that are not service events but have a
  severity level of 'warning'

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

healthNotification, powerResetNotification, and disconnectNotification do not build on each other
and may be configured independently.

  * healthNotification enables the daily summary health report for the server.
  * powerResetNotification enables notifications for out-of-band power operations.
  * disconnectNotification enables notifications to be sent when the server remains in the disconnected
  or not monitored state after the configured number of hours. A null value in this field
  disables disconnect and not monitored notifications.

### Initial values
All values are initially 'off' (false or null) with the result being that no notifications will be sent.

Endpoint: PUT /compute-ops-mgmt/v1/user-preferences/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique user preferences object identifier

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `criticalNotification` (boolean, required)

  - `criticalNonServiceNotification` (boolean)

  - `warningNotification` (boolean)

  - `healthNotification` (boolean)

  - `powerResetNotification` (boolean)

  - `disconnectNotification` (any)

## Response 200 fields (application/json):

  - `id` (string)
    Unique user preference identifier
    Example: "36e00ac2-16fb-4dd5-8495-7e6df82fc15e"

  - `type` (string)
    The type of the resource.

  - `generation` (integer)
    Monotonically increasing update counter

  - `createdAt` (string)
    Time of preferences creation

  - `updatedAt` (string)
    Time of the last preferences update

  - `criticalNotification` (boolean)
    Default notification choice for server critical notifications that are service-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `criticalNonServiceNotification` (boolean)
    Default notification choice for server critical notifications that are non-service-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `warningNotification` (boolean)
    Default notification choice for server warning-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `healthNotification` (boolean)
    Default notification choice for daily server health notification via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `powerResetNotification` (boolean)
    Default notification choice for out-of-band power operations via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `disconnectNotification` (any)
    Default notification choice for server disconnect or not monitored state via email. An integer value represents the number of hours a server has to remain in the disconnected or not monitored state to notify. A null value disables disconnect or not monitored notifications. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

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


