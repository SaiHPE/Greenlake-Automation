---
title: "POST /compute-ops-mgmt/v1/user-preferences/subscribe"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/post_v1_user_preferences_subscribe.md"
scraped_at: "2026-06-07T06:15:12.749090+00:00Z"
---

# Subscribe users

### Purpose
This endpoint allows you to set the user preferences for other users in your workspace.
This endpoint only allows subscribing, meaning configuration will only be applied for properties
set to true or a valid integer in the case of disconnectNotification.

The user preference attributes to configure should be included in requestData.
The lists in the recipients object will be used to subscribe each individual user.
For example, if healthNotification is set to true and example@email.com is included in either the all
list or the health list, the user example@email.com will end up with healthNotification set to true. If
healthNotification is set to false, or example@email.com is not included in all or health, then healthNotification
will be unaffected for example@email.com.

### Request Data
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
  or not monitored state after the configured number of hours.

Endpoint: POST /compute-ops-mgmt/v1/user-preferences/subscribe
Version: latest
Security: Bearer

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `recipients` (object, required)

  - `recipients.all` (any)
    List of user emails. Each user included in this list will have notifications enabled for any value included in requestData that is true (or a valid integer in the case of disconnectNotification)
    Example: ["example@email.com"]

  - `recipients.critical` (any)
    List of user emails. If a user is included in this list, the selections of criticalNotification, criticalNonServiceNotification, and warningNotification will be configured.
    Example: ["example@email.com"]

  - `recipients.health` (any)
    List of user emails. If a user is included in this list, the selection of healthNotification will be configured.
    Example: ["example@email.com"]

  - `recipients.powerReset` (any)
    List of user emails. If a user is included in this list, the selection of powerResetNotification will be configured.
    Example: ["example@email.com"]

  - `recipients.disconnect` (any)
    List of user emails. If a user is included in this list, the selection of disconnectNotification will be configured.
    Example: ["example@email.com"]

  - `requestData` (object, required)

  - `requestData.criticalNotification` (boolean)

  - `requestData.criticalNonServiceNotification` (boolean)

  - `requestData.warningNotification` (boolean)

  - `requestData.healthNotification` (boolean)

  - `requestData.powerResetNotification` (boolean)

  - `requestData.disconnectNotification` (any)

## Response 200 fields (application/json):

  - `successCount` (integer)

  - `errorCount` (integer)

  - `successes` (array)

  - `successes.id` (string)
    Unique user preference identifier
    Example: "36e00ac2-16fb-4dd5-8495-7e6df82fc15e"

  - `successes.type` (string)
    The type of the resource.

  - `successes.generation` (integer)
    Monotonically increasing update counter

  - `successes.createdAt` (string)
    Time of preferences creation

  - `successes.updatedAt` (string)
    Time of the last preferences update

  - `successes.criticalNotification` (boolean)
    Default notification choice for server critical notifications that are service-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `successes.criticalNonServiceNotification` (boolean)
    Default notification choice for server critical notifications that are non-service-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `successes.warningNotification` (boolean)
    Default notification choice for server warning-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `successes.healthNotification` (boolean)
    Default notification choice for daily server health notification via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `successes.powerResetNotification` (boolean)
    Default notification choice for out-of-band power operations via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `successes.disconnectNotification` (any)
    Default notification choice for server disconnect or not monitored state via email. An integer value represents the number of hours a server has to remain in the disconnected or not monitored state to notify. A null value disables disconnect or not monitored notifications. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1/servers/{id}/notifications).

  - `errors` (array)

  - `errors.httpStatusCode` (integer, required)
    HTTP equivalent status code
    Example: 400

  - `errors.errorCode` (string, required)
    Unique machine-friendly identifier for the error
    Example: "HPE-GL-COMPUTE_OPS-0500001"

  - `errors.message` (string, required)
    User-friendly error message

  - `errors.debugId` (string, required)
    Unique identifier for the instance of this error

  - `errors.errorDetails` (array)
    Additional detailed information about the error

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


