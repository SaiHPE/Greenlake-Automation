---
title: "GET /compute-ops-mgmt/v1/user-preferences/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-remote/openapi/user-preferences-v1/get_v1_user_preference_by_id.md"
scraped_at: "2026-06-07T06:14:54.806729+00:00Z"
---

# Get a specific user preference object

Retrieve a user preference object specified by its id

Endpoint: GET /compute-ops-mgmt/v1/user-preferences/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique user preferences object identifier

## Header parameters:

  - `Tenant-Acid` (string)
    Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.

In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the /compute-ops-mgmt/v1beta1/accounts API to determine the application customer IDs for your tenant accounts.

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


