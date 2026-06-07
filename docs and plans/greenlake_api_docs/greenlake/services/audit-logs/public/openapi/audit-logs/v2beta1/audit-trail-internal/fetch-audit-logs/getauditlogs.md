---
title: "POST /audit-log/v2beta1/logs-search"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-internal/fetch-audit-logs/getauditlogs.md"
scraped_at: "2026-06-07T06:16:39.417688+00:00Z"
---

# Retrieves audit logs of one or more services.

This API facilitates to search and retrieve audit logs for one or more services based on a flexible filters. It supports filtering by service offer ID, region, time range, and many other fields. 
- To retrieve the logs of HPE GreenLake service the region field is not required. Use 00000000-0000-0000-0000-000000000000 as the service offer ID.
- For external services such as Computes Ops Manager, Aruba central and others specifying a valid region is required along with service offer id.

This API supports cursor based pagination to fetch the next set of audit logs.

Rate limits:
- 100 requests per minute per user.
- 300 requests per minute overall.

Endpoint: POST /audit-log/v2beta1/logs-search
Version: v2beta1

## Header parameters:

  - `Hpe-Username` (string)
    User's email address

  - `Hpe-Workspace-Id` (string)
    Workspace Id
    Example: "e1b852943cd911eeb8586e98c33ed4b9"

  - `CCS-Transaction-Id` (string)
    CCS Transaction Id for tracing
    Example: "1775cd77-37fc-4ee7-8ef2-7098bb09089f"

## Request fields (application/json):

  - `serviceOffers` (array, required)

  - `filters` (object)

  - `filters.categories` (string)

  - `filters.startTime` (string)

  - `filters.endTime` (string)

  - `filters.description` (string)

  - `filters.username` (string)

  - `filters.workspace` (object)

  - `filters.workspace.name` (string)
    Workspace name. This is used to filter the audit logs by workspace name.

  - `filters.workspace.type` (string)
    Workspace type. This is used to filter the audit logs by workspace type.
    Enum: "STANDALONE", "TENANT", "MSP"

  - `filters.hasDetails` (boolean)

  - `filters.ipAddress` (string)

  - `filters.additionalInfo` (object)

  - `filters.additionalInfo.serverName` (string)

  - `searchString` (string)

  - `pagination` (object)

  - `pagination.next` (string)
    Next page cursor value

  - `pagination.limit` (integer)

  - `select` (string)
    Use the select query parameter to restrict the number of properties included in the audit log response.

  - `sortBy` (string)
    Field to sort by.

  - `sortDir` (string)
    Sort direction (asc or desc).
    Enum: "asc", "desc"

## Response 200 fields (application/json):

  - `count` (integer, required)

  - `total` (integer, required)

  - `remainingRecords` (boolean, required)

  - `items` (array, required)

  - `items.additionalInfo` (object)

  - `items.additionalInfo.deviceType` (string)

  - `items.additionalInfo.serverName` (string)

  - `items.additionalInfo.serverProductId` (string)

  - `items.additionalInfo.serverSerial` (string)

  - `items.id` (string)

  - `items.category` (string)

  - `items.createdAt` (string)

  - `items.description` (string)

  - `items.hasDetails` (boolean)

  - `items.serviceOffer` (object)
    Service offer details for which this audit log is published.

  - `items.serviceOffer.id` (string, required)
    Service offer ID.

  - `items.serviceOffer.region` (string, required)
    Service offer region where it is provisioned.

  - `items.serviceOffer.resourceUri` (string, required)
    URI reference to the service offer resource.

  - `items.serviceOffer.name` (string)
    Service offer name.

  - `items.type` (string)

  - `items.username` (string)

  - `items.workspace` (object)

  - `items.workspace.id` (string, required)
    Unique identifier for the workspace.
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `items.workspace.name` (string, required)
    Name of the workspace where the audit log event occurred.
    Example: "Audit trail ws"

  - `items.workspace.type` (string)
    Type of the workspace.
    Enum: "STANDALONE", "TENANT", "MSP"

  - `items.workspace.resourceUri` (string)
    URI reference to the workspace resource.

  - `items.ipAddress` (string)

  - `next` (string)
    Specifies the next cursor value that can be used to fetch the next set of items.
    Example: "1722843946119:ki79M5ABnX-n3yuoCGwl"

## Response 400 fields (application/json):

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
    Error type

  - `errorDetails.issues` (array, required)
    List of bad request issues

  - `errorDetails.issues.source` (string, required)
    The part of the request with an issue.

  - `errorDetails.issues.subject` (string, required)
    The specific issue key. For example, if the source property is field, the subject is the dot-separated property name the issue is about

  - `errorDetails.issues.description` (string)
    A human-readable description of the issue.

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

## Response 429 fields (application/json):

  - `errorCode` (string, required)
    Unique machine-friendly identifier for the error.

  - `message` (string, required)
    User-friendly error message.

  - `debugId` (string, required)
    Unique identifier for the instance of this error.

  - `httpStatusCode` (integer, required)
    HTTP status code for the error.

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


