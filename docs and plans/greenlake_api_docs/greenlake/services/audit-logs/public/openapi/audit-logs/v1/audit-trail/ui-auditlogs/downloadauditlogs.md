---
title: "GET /auditlogs/ui/v1/download"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/downloadauditlogs.md"
scraped_at: "2026-06-07T06:16:38.001812+00:00Z"
---

# Download audit logs in CSV or PDF format.

Endpoint: GET /auditlogs/ui/v1/download
Version: v1
Security: BearerAuth, CookieAuth

## Query parameters:

  - `app_slug` (string, required)
    Application slug

  - `columns` (array, required)
    The columns which are to be present in the requested file.
    Example: ["category","description","ip_address","target","tenant_name","username"]

  - `file_extension` (string, required)
    The file extension implying the format in which the audit-trail has to be downloaded
    Enum: "csv", "pdf"


