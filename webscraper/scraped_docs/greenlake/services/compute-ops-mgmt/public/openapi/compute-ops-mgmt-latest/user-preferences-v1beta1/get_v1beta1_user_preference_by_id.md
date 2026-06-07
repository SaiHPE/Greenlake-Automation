---
title: "GET /compute-ops-mgmt/v1beta1/user-preferences/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/user-preferences-v1beta1/get_v1beta1_user_preference_by_id.md"
scraped_at: "2026-06-07T06:15:13.214547+00:00Z"
---

# Get a specific user preference object

Retrieve a user preference object specified by its id


URI PATH PREFIX RENAME

This API now supports the URI path prefix /compute-ops-mgmt which used to be /compute-ops. The /compute-ops prefix is deprecated
and might become unresponsive after Tuesday, April 1, 2025. The Guide
provides more information about this change.

Endpoint: GET /compute-ops-mgmt/v1beta1/user-preferences/{id}
Version: latest
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Unique user preferences object identifier

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
    Default notification choice for server critical notifications that are service-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1beta2/servers/{id}/notifications).

  - `criticalNonServiceNotification` (boolean)
    Default notification choice for server critical notifications that are non-service-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1beta2/servers/{id}/notifications).

  - `warningNotification` (boolean)
    Default notification choice for server warning-level events via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1beta2/servers/{id}/notifications).

  - `healthNotification` (boolean)
    Default notification choice for daily server health notification via email. Override the default notification choice by updating the notification settings for a server (see /compute-ops-mgmt/v1beta2/servers/{id}/notifications).

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


