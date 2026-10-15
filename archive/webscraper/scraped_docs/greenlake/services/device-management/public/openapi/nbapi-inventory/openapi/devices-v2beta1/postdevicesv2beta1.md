---
title: "POST /devices/v2beta1/devices"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory/openapi/devices-v2beta1/postdevicesv2beta1.md"
scraped_at: "2026-06-07T06:15:17.973364+00:00Z"
---

# Add devices

Add one or more devices to a workspace. This API endpoint provides an asynchronous response and returns 202 Accepted if basic input validations are successful. The  location header in the response provides the URI to invoke to  fetch the progress of the device addition task. For details about the  status fetch URL, refer to the API endpoint Get progress or status of async operations in devices. NOTE: You need edit permissions for the Devices and Subscription service to call this API endpoint. Rate limits are enforced, and 25 requests per minute are supported per workspace. The API endpoint returns 429 if this threshold is breached.

Endpoint: POST /devices/v2beta1/devices
Version: latest
Security: Bearer

## Query parameters:

  - `dry-run` (boolean)
    The dry-run query parameter is used to perform the resource update operation (POST, PUT, PATCH, DELETE) and return a response as if the operation had completed, but without actually creating, updating, or deleting the resource. This allows you to test if the request would succeed before making the change. If set to true, the request is validated but not executed.

## Request fields (application/json):

  - `serialNumber` (string, required)
    The serial number of the device.

  - `deviceType` (string, required)
    The type of device.
    Enum: "COMPUTE", "NETWORK", "STORAGE"

  - `tags` (object)

  - `macAddress` (string)
    The media access control (MAC) address of the device. This is required for claiming NETWORK devices.

  - `partNumber` (string)
    The part number of the device. This is required for claiming COMPUTE or STORAGE devices.

  - `location` (object)
    The location ID of the device.

  - `location.id` (string)

  - `contact` (object)
    The contact information for the device.

  - `contact.type` (string, required)
    Enum: "WORKSPACE-USER", "NON-WORKSPACE-USER"

  - `contact.workspaceUser` (object)
    Details for workspace users, that is, users already added to the workspace.

  - `contact.workspaceUser.id` (string)
    The unique identifier of the workspace user.

  - `contact.nonWorkspaceUser` (object)
    Details for non-workspace users.

  - `contact.nonWorkspaceUser.email` (string, required)
    The email address of the non-workspace user.

  - `contact.nonWorkspaceUser.firstName` (string)
    The first name of the non-workspace user.

  - `contact.nonWorkspaceUser.lastName` (string)
    The last name of the non-workspace user.

  - `contact.nonWorkspaceUser.phoneNumber` (string)
    The phone number of the non-workspace user.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `badRequestErrorDetails` (array)

  - `badRequestErrorDetails.type` (string, required)
    The type of error details.

  - `badRequestErrorDetails.issues` (array, required)
    An array of request issues.

  - `badRequestErrorDetails.issues.source` (string)
    The part of the request with an issue.

  - `badRequestErrorDetails.issues.subject` (string)
    The issue key.

  - `badRequestErrorDetails.issues.description` (string)
    An explanation of the issue.

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 429 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `generalErrorDetails` (array)

  - `generalErrorDetails.type` (string, required)
    The type of error.

  - `generalErrorDetails.source` (string, required)
    The source of the error.

  - `generalErrorDetails.metadata` (object, required)
    Additional key pairs.

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error

  - `message` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `serverErrorDetails` (array)

  - `serverErrorDetails.type` (string, required)

  - `serverErrorDetails.retryAfterSeconds` (integer, required)


## Response 202 fields
