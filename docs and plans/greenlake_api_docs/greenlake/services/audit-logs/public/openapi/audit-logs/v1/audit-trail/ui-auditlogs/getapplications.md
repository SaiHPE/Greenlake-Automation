---
title: "GET /auditlogs/ui/v1/applications"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getapplications.md"
scraped_at: "2026-06-07T06:16:37.725053+00:00Z"
---

# Get all the application instance details.

Endpoint: GET /auditlogs/ui/v1/applications
Version: v1
Security: BearerAuth, CookieAuth

## Response 200 fields (application/json):

  - `AUTHORIZED_APPS` (array)

  - `AUTHORIZED_APPS.app_slug` (string)
    Example: "CCS"

  - `AUTHORIZED_APPS.application_customer_id` (string)
    Example: "3e35c938fb5911edbb4c660832a054ff"

  - `AUTHORIZED_APPS.application_id` (string)
    Example: "da7f1156-ddd9-41c2-8f34-64c0d0f764f7"

  - `AUTHORIZED_APPS.application_name` (string)
    Example: "App Catalog"

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


