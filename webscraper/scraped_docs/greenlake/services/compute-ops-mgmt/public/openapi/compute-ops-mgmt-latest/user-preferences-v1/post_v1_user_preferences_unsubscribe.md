---
title: "POST /compute-ops-mgmt/v1/user-preferences/unsubscribe"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1/post_v1_user_preferences_unsubscribe.md"
scraped_at: "2026-06-07T06:15:12.775964+00:00Z"
---

# Unsubscribe users

### Purpose
This endpoint allows you to unset the user preferences for other users in your workspace.
Users will be unsubscribed based on the lists in the request body.

For example, a user included in the critical list will have their preferences for 
criticalNotification, criticalNonServiceNotification, and warningNotification set to false.

Endpoint: POST /compute-ops-mgmt/v1/user-preferences/unsubscribe
Version: latest
Security: Bearer

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

## Request fields (application/json):

  - `all` (any)
    List of user emails. Each user included in this list will have all default notification preferences disabled.
    Example: ["example@email.com"]

  - `critical` (any)
    List of user emails. Each user included in this list will have their criticalNotification, criticalNonServiceNotification, and warningNotification preferences set to false.
    Example: ["example@email.com"]

  - `health` (any)
    List of user emails. Each user included in this list will have their healthNotification preference set to false.
    Example: ["example@email.com"]

  - `powerReset` (any)
    List of user emails. Each user included in this list will have their powerResetNotification preference set to false.
    Example: ["example@email.com"]

  - `disconnect` (any)
    List of user emails. Each user included in this list will have their disconnectNotification preference set to null.
    Example: ["example@email.com"]

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


