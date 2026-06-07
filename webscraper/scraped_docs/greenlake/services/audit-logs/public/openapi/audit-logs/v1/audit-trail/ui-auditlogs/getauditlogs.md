---
title: "GET /auditlogs/ui/v1/search"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogs.md"
scraped_at: "2026-06-07T06:16:37.339240+00:00Z"
---

# Get all audit logs of an application instance or workspace.

Endpoint: GET /auditlogs/ui/v1/search
Version: v1
Security: BearerAuth, CookieAuth

## Query parameters:

  - `app_slug` (string, required)
    Application slug
    Example: "CCS"

  - `application_customer_id` (string)
    Application customer id of the application instance.

  - `start_time` (integer)
    Start time for filtering. Expects a epoch time integer value

  - `end_time` (integer)
    End time for filtering. Expects a epoch time integer value

  - `category` (string)
    Audit log category

  - `description` (string)
    Audit log description

  - `ip_address` (string)
    IP address contained within the additional details of the log.

  - `username` (string)
    User's email address

  - `account_name` (string)
    Name of the Workspace to which the audit log belong

  - `_all` (string)
    Filter for all fields

  - `offset` (integer)
    Offset for pagination

  - `limit` (integer)
    Number of items per page

  - `sort_by` (string)
    Field to sort by

  - `sort_dir` (string)
    Sort direction (asc or desc)
    Enum: "asc", "desc"

## Response 200 fields (application/json):

  - `audits` (array)

  - `audits.app_slug` (string)
    Application slug
    Example: "CCS"

  - `audits.audit_id` (string)
    Unique audit log ID
    Example: "5f7b1b3b-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `audits.app_instance_id` (string)
    Unique application instance ID
    Example: "123132-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `audits.application_customer_id` (string)
    Unique Application customer ID
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `audits.msp_application_customer_id` (string)
    MSP application customer id
    Example: "345345-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `audits.msp_id` (string)
    MSP workspace ID
    Example: "dfdgdff-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `audits.username` (string)
    The user who performed the action.
    Example: "test@test.com"

  - `audits.category` (string)
    The category of the audit log.
    Example: "User Management"

  - `audits.description` (string)
    A short description of the changes such as subscription assignment, firmware upgrade, and configuration updates.
    Example: "User logged in"

  - `audits.customer_id` (string)
    Unique workspace ID
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `audits.customer_name` (string)
    The workspace name associated with the audit log.
    Example: "Audit trail ws"

  - `audits.audit_created_at` (number)
    The time the audit log was created in epoch time.
    Example: 1630000000

  - `audits.additional_info` (object)
    Returns additional attributes.
    Example: {"ip_address":"127.0.0.1"}

  - `audits.has_details` (boolean)
    If set to true, additional details are available for the audit log.

  - `pagination` (object)

  - `pagination.count_per_page` (integer, required)
    Number of returned items

  - `pagination.offset` (integer, required)
    Specifies the offset of the returned page. Only when offset based pagination is used.

  - `pagination.total_count` (integer, required)
    Total number of items in the collection.

  - `remaining_records` (boolean)
    This boolean flag shows whether there are more records available

  - `timestamp` (object)
    The start and end time of the response

  - `timestamp.start_time` (number)
    The start time of the audit logs in epoch time

  - `timestamp.end_time` (number)
    The end time of the audit logs in epoch time

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


