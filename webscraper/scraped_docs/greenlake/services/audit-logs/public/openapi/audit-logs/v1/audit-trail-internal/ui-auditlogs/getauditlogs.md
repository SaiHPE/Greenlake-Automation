---
title: "POST /auditlogs/internal/v1/logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail-internal/ui-auditlogs/getauditlogs.md"
scraped_at: "2026-06-07T06:16:37.227198+00:00Z"
---

# Get all audit logs of an application instance or workspace for report generation.

API to get the audit logs of application instance or platform logs required for the export.
app_slug and application_customer_id are mandatory to get the application instance logs.
service_offer_id and region are mandatory to get the service instance logs.
Audit logs can be filtered based on the following parameters:
- categories
- exclude_categories
- start_time
- end_time
- description
- username
- ip_address
- workspace_name
- workspace_type
- target

Following are the additional filters that can be applied to external application audit logs:
- device_type
- server_serial
- server_name
- server_product_id

This API supports cursor based pagination to fetch the next set of audit logs.

Endpoint: POST /auditlogs/internal/v1/logs
Version: v1
Security: BearerAuth, CookieAuth

## Header parameters:

  - `username` (string, required)
    User's email address

  - `workspace_id` (string, required)
    Workspace Id
    Example: "e1b852943cd911eeb8586e98c33ed4b9"

  - `ccs-transaction-id` (string)
    CCS Transaction Id for tracing
    Example: "dfdgdff-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

## Request fields (application/json):

  - `app_slug` (string, required)
    Application slug
    Example: "CCS"

  - `application_customer_id` (string, required)
    Application customer id
    Example: "e6ddab54409c11eebd5682fab5035386"

  - `service_offer_id` (string, required)
    Service offer ID
    Example: "345345-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `region` (string, required)
    Region where service instance is provisioned
    Example: "en-US"

  - `filters` (object)

  - `filters.categories` (string)
    Example: "Alert Configuration,AW8 Migration,Client Match"

  - `filters.exclude_categories` (string)
    Exclude categories. Set categories to "_all" and provide categories to be excluded in exclude_categories field.
    Example: "Authorization,Authentication"

  - `filters.start_time` (integer)
    Start time for filtering. Expects a epoch time integer value in seconds
    Example: 1724092200

  - `filters.end_time` (integer)
    End time for filtering. Expects a epoch time integer value in seconds
    Example: 1724351399

  - `filters.description` (string)
    Audit log description
    Example: "User logged in"

  - `filters.username` (string)
    Username by which the audit log was created
    Example: "test@test.com"

  - `filters.ip_address` (string)
    IP address contained within the additional details of the log.
    Example: "192.132.12.11"

  - `filters.workspace_name` (string)
    Name of the Workspace to which the audit log belong
    Example: "Coca cola"

  - `filters.workspace_type` (string)
    Type of the workspace
    Enum: "STANDALONE", "MSP", "TENANT"

  - `filters.device_type` (string)

  - `filters.server_serial` (string)
    Example: "H1YK11"

  - `filters.server_name` (string)

  - `filters.server_product_id` (string)

  - `filters.target` (string)

  - `search_string` (string)
    Search string

  - `pagination` (object)

  - `pagination.next` (string)
    Next page cursor value
    Example: "1722843946119:ki79M5ABnX-n3yuoCGwl"

  - `pagination.limit` (integer)
    Example: 5000

  - `i18n_preference` (string)
    Language preference
    Example: "en-US"

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

  - `items.app_slug` (string)
    Application slug
    Example: "CCS"

  - `items.audit_id` (string)
    Unique audit log ID
    Example: "5f7b1b3b-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.app_instance_id` (string)
    Unique application instance ID
    Example: "123132-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.application_customer_id` (string)
    Unique Application customer ID
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `items.msp_application_customer_id` (string)
    MSP application customer id
    Example: "345345-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.msp_id` (string)
    MSP workspace ID
    Example: "dfdgdff-4b3b-4b3b-4b3b-4b3b4b3b4b3b"

  - `items.username` (string)
    The user who performed the action.
    Example: "test@test.com"

  - `items.category` (string)
    The category of the audit log.
    Example: "User Management"

  - `items.description` (string)
    A short description of the changes such as subscription assignment, firmware upgrade, and configuration updates.
    Example: "User logged in"

  - `items.workspace_id` (string)
    Unique workspace ID
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `items.workspace_name` (string)
    The workspace name associated with the audit log.
    Example: "Audit trail ws"

  - `items.audit_created_at` (number)
    The time the audit log was created in epoch time.
    Example: 1630000000

  - `items.additional_info` (object)
    Returns additional attributes.
    Example: {"ip_address":"127.0.0.1"}

  - `items.has_details` (boolean)
    If set to true, additional details are available for the audit log.

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


