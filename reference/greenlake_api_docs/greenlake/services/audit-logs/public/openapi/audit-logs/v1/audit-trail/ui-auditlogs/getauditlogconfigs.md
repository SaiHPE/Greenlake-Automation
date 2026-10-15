---
title: "GET /auditlogs/ui/v1/{application-id}/configs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogconfigs.md"
scraped_at: "2026-06-07T06:16:37.778994+00:00Z"
---

# Get the audit log configurations related to an application

Endpoint: GET /auditlogs/ui/v1/{application-id}/configs
Version: v1
Security: BearerAuth, CookieAuth

## Path parameters:

  - `application-id` (string, required)
    Application id

## Response 200 fields (application/json):

  - `configs` (object)

  - `configs.AUDIT_EXPORT_FIELDS` (object)

  - `configs.AUDIT_EXPORT_FIELDS.CSV` (object)
    Example: {"Category":"category","Description":"description","IP Address":"ip_address","Target":"target","Source":"tenant_name","Username":"username","Device Type":"device_type","Time":"audit_created_at","Customer Name":"customer_name","Group ID":"group_id"}

  - `configs.AUDIT_EXPORT_FIELDS.PDF` (object)
    Example: {"Category":"category","Description":"description","IP Address":"ip_address","Target":"target","Source":"tenant_name","Username":"username","Device Type":"device_type","Time":"audit_created_at","Customer Name":"customer_name","Group ID":"group_id"}

  - `configs.CATEGORIES` (array)
    Example: ["Alert Configuration","API Gateway","Augmentation Method","Authentication and Policy","AW8 Migration","Backup Restore","Classification Precedence","CLI Access","Client Match","Collector","Configuration"]

  - `configs.DASHBOARD_COLUMNS` (object)

  - `configs.DASHBOARD_COLUMNS.ALL` (object)
    Example: {"Customer Name":"customer_name","Category":"category","Description":"description","Time":"audit_created_at","Username":"username","Device Type":"device_type","IP Address":"ip_address","Target":"target","Source":"tenant_name","Workspace Name":"account_name"}

  - `configs.DASHBOARD_COLUMNS.DEFAULT` (object)
    Example: {"Category":"category","Description":"description","Target":"target","Source":"tenant_name","Time":"audit_created_at","Username":"username"}

  - `configs.DASHBOARD_COLUMNS.FIXED` (object)
    Example: {"Category":"category","Time":"audit_created_at","Description":"description"}

  - `configs.ORDER` (object)
    Example: {"Customer Name":2,"Category":0,"Description":1,"Time":8,"Username":7,"Device Type":3,"IP Address":4,"Target":6,"Source":5}

  - `configs.UI_SEARCH_FIELDS` (object)
    Example: {"Description":"description","IP Address":"ip_address","Target":"target","Username":"username","Workspace Name":"account_name"}

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


