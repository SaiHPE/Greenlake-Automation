---
title: "GET /auditlogs/ui/v1/count"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/getauditlogscount.md"
scraped_at: "2026-06-07T06:16:37.981785+00:00Z"
---

# Get the number of audit logs in the system for the current customer-id from given timestamp

Endpoint: GET /auditlogs/ui/v1/count
Version: v1
Security: BearerAuth, CookieAuth

## Query parameters:

  - `start_time` (number, required)
    Start time for filtering. Expects a epoch time integer value

  - `end_time` (number, required)
    End time for filtering. Expects a epoch time integer value

  - `app_slug` (string, required)
    Application slug

  - `application_customer_id` (string)
    Application customer id of the application instance.

## Response 200 fields (application/json):

  - `total` (number)

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


