---
title: "GET /audit-log/v2beta1/logs/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs-public/audit-trail-external-v2beta1/fetch-audit-logs/getauditlog.md"
scraped_at: "2026-06-07T06:13:54.455621+00:00Z"
---

# Get a specific audit log.

Endpoint: GET /audit-log/v2beta1/logs/{id}
Version: v2beta1
Security: Bearer

## Path parameters:

  - `id` (string, required)
    Provide the ID of the audit log record to fetch the audit log.

## Response 200 fields (application/json):

  - `id` (string, required)

  - `type` (string, required)

  - `category` (string, required)

  - `createdAt` (string, required)

  - `description` (string, required)

  - `username` (string, required)

  - `serviceOffer` (object, required)
    Service offer details for which this audit log is published.

  - `serviceOffer.id` (string, required)
    Service offer ID.

  - `serviceOffer.region` (string, required)
    Service offer region where it is provisioned.

  - `serviceOffer.name` (string, required)
    Service offer name.

  - `workspace` (object, required)

  - `workspace.id` (string, required)
    Unique identifier for the workspace.

  - `workspace.name` (string, required)
    Name of the workspace where the audit log event occurred.

  - `workspace.type` (string)
    Type of the workspace.
    Enum: "STANDALONE", "TENANT", "MSP"

  - `additionalInfo` (object)

  - `additionalInfo.deviceType` (string)

  - `additionalInfo.serverName` (string)

  - `additionalInfo.serverProductId` (string)

  - `additionalInfo.serverSerial` (string)

  - `hasDetails` (boolean)

  - `ipAddress` (string)
    IPv4 or IPv6 address of the user who performed the action.

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 403 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 404 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)

  - `errorDetails.type` (string, required)

  - `errorDetails.source` (string, required)

  - `errorDetails.metadata` (object, required)

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

  - `errorDetails` (array)
    Additional detailed information about the error.

  - `errorDetails.type` (string, required)

  - `errorDetails.retryAfterSeconds` (integer, required)


