---
title: "GET /audit-log/v2beta1/logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-fetch-logs/fetch-audit-logs/getauditlogs.md"
scraped_at: "2026-06-07T06:16:38.989539+00:00Z"
---

# Retrieves audit logs of one or more services.

The audit logs can be filtered using a variety of parameters. Queries should be separated by and and can utilize eq, contains, and in operators to construct the final query. Each query should follow the format:
 * key eq 'value' for equality operation.
 * contains(key, 'value') for contains operation.
 * key in ('value1', 'value2') for in operation.

| Filter Parameter | Supported Operators | Type                | Example |
|-----------------------|-------------------------|--------------------------|--------------|
| createdAt         | lt, ge              | RFC timestamp (string)   | createdAt ge '2024-02-16T07:54:55.0Z' |
| category          | eq, in              | string                   | category eq 'User Management'category in ('Device Management', 'User Activity') |
| description       | eq, contains        | string                   | contains(description, 'Logged in')description eq 'User test@test.com logged in via ping mode.' |
| ipAddress         | eq, contains        | IP string                | ipAddress eq '192.168.12.12'contains(ipAddress, '192.168') |
| username          | eq, contains        | email (string)           | username eq 'test@test.com'contains(username, '@gmail.com') |
| workspace/name    | eq, contains        | string                   | workspace/name eq 'Example workspace'contains(workspace/name, 'Example') |
| workspace/type    | eq                    | string                   | workspace/type eq 'TENANT'workspace/type eq 'MSP' |
| serviceOffer/id   | eq, in              | UUID (string)            | serviceOffer/id eq '902fa943-dcfc-432c-a92c-3a3a454923d9'serviceOffer/id in ('902fa943-dcfc-432c-a92c-3a3a454923d9', '00000000-0000-0000-0000-000000000000') |
| region            | eq                    | region code (string)     | region eq 'us-west' |
| hasDetails        | eq                    | boolean                  | hasDetails eq 'true' |

 Note: Maximum five serviceOffer/id can be passed in the filter. If no serviceOffer/id is passed, only platform audit logs will be fetched.
 Note: Maximum five serviceOffer/id can be passed in the filter. If no serviceOffer/id is passed, only HPE GreenLake Platform Audit logs will be fetched.

 The API supports pagination and sorting options to efficiently retrieve large datasets

 Rate limits:
 - 100 requests per minute per user.
 - 300 requests per minute overall.

Endpoint: GET /audit-log/v2beta1/logs
Version: v2beta1
Security: Bearer

## Query parameters:

  - `filter` (string)

  - `select` (string)
    Use the select query parameter to restrict the number of properties included in the audit log response.
Specify as comma-separated values. The supported select parameters are:
 * serviceOffer
 * createdAt
 * category
 * hasDetails
 * workspace
 * description
 * username
 * ipAddress
 * additionalInfo

  - `limit` (integer)
    How many items to return at one time (max 2000)

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from.

  - `sort` (string)
    Sort the results based on the specified field. The default sort order is descending. Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc (descending).

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items returned in the response.

  - `offset` (integer, required)
    Zero-based offset of the first item in the response.

  - `total` (integer, required)
    Total number of items matching the query. Maximum value is 10,000. If more than 10,000 items match the query, then remainingRecords is set to true.

  - `remainingRecords` (boolean, required)
    Boolean value indicating if there are more than 10,000 records available that match the query. Client can apply filters to narrow down the results.

  - `items` (array, required)

  - `items.id` (string, required)

  - `items.type` (string, required)

  - `items.category` (string, required)

  - `items.createdAt` (string, required)

  - `items.description` (string, required)

  - `items.username` (string, required)

  - `items.serviceOffer` (object, required)
    Service offer details for which this audit log is published.

  - `items.serviceOffer.id` (string, required)
    Service offer ID.

  - `items.serviceOffer.region` (string, required)
    Service offer region where it is provisioned.

  - `items.serviceOffer.name` (string, required)
    Service offer name.

  - `items.workspace` (object, required)

  - `items.workspace.id` (string, required)
    Unique identifier for the workspace.

  - `items.workspace.name` (string, required)
    Name of the workspace where the audit log event occurred.

  - `items.workspace.type` (string)
    Type of the workspace.
    Enum: "STANDALONE", "TENANT", "MSP"

  - `items.additionalInfo` (object)

  - `items.additionalInfo.deviceType` (string)

  - `items.additionalInfo.serverName` (string)

  - `items.additionalInfo.serverProductId` (string)

  - `items.additionalInfo.serverSerial` (string)

  - `items.hasDetails` (boolean)

  - `items.ipAddress` (string)
    IPv4 or IPv6 address of the user who performed the action.

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


