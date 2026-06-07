---
title: "POST /internal-audit-log/v2/logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2/audit-trail-internal/ui-auditlogs/getauditlogs.md"
scraped_at: "2026-06-07T06:16:38.774700+00:00Z"
---

# Get all audit logs of an application instance or workspace for report generation.

API to get the audit logs of application instance or platform logs required for the export.
appSlug and applicationCustomerId are mandatory to get the application instance logs.
serviceOfferId and region are mandatory to get the service instance logs.
Audit logs can be filtered based on the following parameters:
- categories
- excludeCategories
- startTime
- endTime
- description
- username
- ipAddress
- workspaceName
- workspaceType
- target

Following are the additional filters that can be applied to external application audit logs:
- deviceType
- serverSerial
- serverName
- serverProductId

This API supports cursor based pagination to fetch the next set of audit logs.

Endpoint: POST /internal-audit-log/v2/logs
Version: v2

## Header parameters:

  - `Hpe-Username` (string, required)
    User's email address

  - `Hpe-Workspace-Id` (string, required)
    Workspace Id
    Example: "e1b852943cd911eeb8586e98c33ed4b9"

  - `CCS-Transaction-Id` (string)
    CCS Transaction Id for tracing
    Example: "dfdgdff-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

## Request fields (application/json):

  - `appSlug` (string, required)
    Application slug
    Example: "CCS"

  - `applicationCustomerId` (string, required)
    Application customer id
    Example: "e6ddab54409c11eebd5682fab5035386"

  - `serviceOfferId` (string, required)
    Service offer ID
    Example: "345345-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `region` (string, required)
    Region where service instance is provisioned
    Example: "en-US"

  - `filters` (object)

  - `filters.categories` (string)
    Example: "Alert Configuration,AW8 Migration,Client Match"

  - `filters.excludeCategories` (string)
    Exclude categories. Set categories to "_all" and provide categories to be excluded in exclude_categories field.
    Example: "Authorization,Authentication"

  - `filters.startTime` (integer)
    Start time for filtering. Expects a epoch time integer value in seconds
    Example: 1724092200

  - `filters.endTime` (integer)
    End time for filtering. Expects a epoch time integer value in seconds
    Example: 1724351399

  - `filters.description` (string)
    Audit log description
    Example: "User logged in"

  - `filters.username` (string)
    Username by which the audit log was created
    Example: "test@test.com"

  - `filters.ipAddress` (string)
    IP address contained within the additional details of the log.
    Example: "192.132.12.11"

  - `filters.workspaceName` (string)
    Name of the Workspace to which the audit log belong
    Example: "Coca cola"

  - `filters.workspaceType` (string)
    Type of the workspace
    Enum: "STANDALONE", "MSP", "TENANT"

  - `filters.deviceType` (string)

  - `filters.serverSerial` (string)
    Example: "H1YK11"

  - `filters.serverName` (string)

  - `filters.serverProductId` (string)

  - `filters.target` (string)

  - `searchString` (string)
    Search string

  - `pagination` (object)

  - `pagination.next` (string)
    Next page cursor value
    Example: "1722843946119:ki79M5ABnX-n3yuoCGwl"

  - `pagination.limit` (integer)
    Example: 5000

  - `i18nPreference` (string)
    Language preference
    Example: "en-US"

  - `queryExecutionId` (string)
    Query execution ID
    Example: 1722843946119

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of returned items
    Example: 5000

  - `next` (string, required)
    Specifies the next cursor value that can be used to fetch the next set of items.
    Example: "1722843946119:ki79M5ABnX-n3yuoCGwl"

  - `total` (integer, required)
    Total number of items in the result set.
    Example: 100000

  - `items` (array)

  - `items.type` (string, required)
    Resource type

  - `items.id` (string, required)
    Unique audit log ID
    Example: "5f7b1b3b-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.user` (string, required)
    The user who performed the action.
    Example: "test@test.com"

  - `items.category` (string, required)
    The category of the audit log.
    Example: "User Management"

  - `items.description` (string, required)
    A short description of the changes such as subscription assignment, firmware upgrade, and configuration updates.
    Example: "User logged in"

  - `items.workspace` (object, required)

  - `items.workspace.id` (string, required)
    Unique workspace ID
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `items.workspace.workspaceName` (string, required)
    The workspace name associated with the audit log.
    Example: "Audit trail ws"

  - `items.workspace.workspaceType` (string, required)
    The type of workspace.
    Example: "STANDALONE"

  - `items.serviceOffer` (object, required)

  - `items.serviceOffer.id` (string, required)
    Service offer ID
    Example: "345345-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.application` (object, required)

  - `items.application.id` (string, required)
    Unique application ID
    Example: "345345-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.region` (string, required)
    Region where service instance is provisioned
    Example: "en-US"

  - `items.generation` (integer, required)
    if any update happened then field count will get increased.

  - `items.createdAt` (number, required)
    The time the audit log was created in epoch time.
    Example: 1630000000

  - `items.updatedAt` (number, required)
    The time the audit log was updated in epoch time.
    Example: 1630000000

  - `items.mspId` (string)
    MSP workspace ID
    Example: "dfdgdff-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.additionalInfo` (object)
    Returns additional attributes.
    Example: {"ipAddress":"127.0.0.1"}

  - `items.header` (string)
    the audit details header.

  - `items.body` (string)
    The audit details body associated with the audit log.

  - `items.queryExecutionId` (string)
    Query execution ID
    Example: 1722843946119

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


