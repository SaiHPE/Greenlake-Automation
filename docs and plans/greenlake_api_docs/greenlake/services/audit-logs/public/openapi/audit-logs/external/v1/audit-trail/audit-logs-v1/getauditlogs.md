---
title: "GET /audit-log/v1/logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/external/v1/audit-trail/audit-logs-v1/getauditlogs.md"
scraped_at: "2026-06-07T06:16:49.567069+00:00Z"
---

# Get all audit logs of an application or user.

The audit logs can be filtered using a variety of parameters. Queries should be separated by and and can utilize eq, contains, and in operators to construct the final query. Each query should follow the format:
* key eq 'value' for equality operation.
* contains(key, 'value') for contains operation.
* key in ('value1', 'value2') for in operation.

| Filter parameter         | Supported Operators | Type                    | Example                                                                                         |
|--------------------------|---------------------|-------------------------|-------------------------------------------------------------------------------------------------|
| createdAt                | lt, ge              | RFC timestamp in string | createdAt ge '2024-02-16T07:54:55.0Z'                                                           |
| category                 | eq, in              | string                  | category eq 'User Management' category in ('Device Management', 'User Activity')                |
| description              | eq, contains        | string                  | contains(description, 'Logged in') description eq 'User test@test.com logged in via ping mode.' |
| additionalInfo/ipAddress | eq, contains        | IP string               | additionalInfo/ipAddress eq '192.168.12.12' contains(additionalInfo/ipAddress, '192.168')       |
| user/username            | eq, contains        | email in string         | user/username eq 'test@test.com' contains(user/username, '@gmail.com')                          |
| workspace/workspaceName  | eq, contains        | string                  | workspace/workspaceName eq 'Example workspace' contains(workspace/workspaceName, 'Example')     |
| application/id           | eq                  | UUID in string          | application/id eq '12312-123123-123123-123121'                                                  |
| region                   | eq                  | region code in string   | region eq 'us-west'                                                                             |
| hasDetails               | eq                  | boolean                 | hasDetails eq 'true'                                                                              |

Endpoint: GET /audit-log/v1/logs
Version: v1
Security: BearerAuth

## Query parameters:

  - `filter` (string)

  - `select` (string)
    Use the select query parameter to restrict the number of properties included in the audit log response.
The supported select parameters:
 * additionalInfo
 * createdAt
 * category
 * hasDetails
 * workspace/workspaceName
 * description
 * user/username

  - `all` (string)
    Provide a free-text search to perform a comprehensive search across all properties for audit logs.

  - `limit` (integer)
    How many items to return at one time (max 2000)

  - `offset` (integer)
    Specifies the zero-based resource offset to start the response from.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Unique audit log ID

  - `items.type` (string, required)
    Resource type

  - `items.application` (object)

  - `items.application.id` (string)
    Unique application ID

  - `items.region` (string)
    The region code associated with the application.

  - `items.user` (object)

  - `items.user.username` (string)
    The user who performed the action.

  - `items.category` (string)
    The category of the audit log.

  - `items.description` (string)
    A short description of the changes such as subscription assignment, firmware upgrade, and configuration updates.

  - `items.workspace` (object)

  - `items.workspace.id` (string)
    Unique workspace ID

  - `items.workspace.workspaceName` (string)
    The workspace name associated with the audit log.

  - `items.createdAt` (string)
    The time the audit log was created.

  - `items.updatedAt` (string)
    The time the audit log was updated.

  - `items.generation` (integer)
    if any update happened then field count will get increased.

  - `items.additionalInfo` (object)
    Returns additional attributes.

  - `items.hasDetails` (boolean)
    If set to true, additional details are available for the audit log.

  - `count` (integer, required)
    Number of returned items

  - `total` (integer, required)
    Total number of items in the collection.

  - `offset` (integer)
    Specifies the offset of the returned page. Only when offset based pagination is used.

  - `remainingRecords` (boolean)
    This boolean flag shows whether there are more records available.

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
    A user-friendly description of the issue.

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
    Additional detailed information about the error.

  - `errorDetails.type` (string, required)
    Error type

  - `errorDetails.source` (string, required)
    Source of the error, typically the API group

  - `errorDetails.metadata` (object, required)
    Additional key value pairs that provide information about this error.

## Response 403 fields (application/json):

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


