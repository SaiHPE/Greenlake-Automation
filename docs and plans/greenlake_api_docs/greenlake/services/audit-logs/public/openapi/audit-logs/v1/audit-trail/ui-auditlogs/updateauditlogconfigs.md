---
title: "PUT /auditlogs/ui/v1/configs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v1/audit-trail/ui-auditlogs/updateauditlogconfigs.md"
scraped_at: "2026-06-07T06:16:37.895562+00:00Z"
---

# Update external application audit logs specific configurations.

Endpoint: PUT /auditlogs/ui/v1/configs
Version: v1
Security: BearerAuth, CookieAuth

## Request fields (application/json):

  - `audit_id` (string)
    Existing audit id of the configuration
    Example: "eUmWt44B1k6acmrQBqvH"

  - `config` (object)

  - `config.app_id` (string)
    Application id
    Example: "373b7710-cd79-4a22-b583-bc4aa7e42fcd"

  - `config.app_customer_id` (string)
    Application customer id
    Example: "e6ddab54409c11eebd5682fab5035386"

  - `config.platform_customer_id` (string)
    Platform customer id
    Example: "e1b852943cd911eeb8586e98c33ed4b9"

  - `config.app_slug` (string)
    Application slug
    Example: "HPECC"

  - `config.app_name` (string)
    Application name
    Example: "COMPUTE App (US West)"

  - `config.app_instance_id` (string)
    Application instance id
    Example: "da7f1156-ddd9-41c2-8f34-64c0d0f764f7"

  - `config.app_audit_info` (object)

  - `config.app_audit_info.app_type` (string)
    Type of an external application.
    Example: "COMPUTE"

  - `config.app_audit_info.categories` (array)
    Example: ["Alert Configuration","API Gateway","Augmentation Method","Authentication and Policy","AW8 Migration","Backup Restore","Classification Precedence","CLI Access","Client Match","Collector","Configuration"]

  - `config.app_audit_info.dashboard_columns` (object)

  - `config.app_audit_info.dashboard_columns.all` (object)
    Example: {"Customer Name":"customer_name","Category":"category","Description":"description","Time":"audit_created_at","Username":"username","Device Type":"device_type","IP Address":"ip_address","Target":"target","Source":"tenant_name","Workspace Name":"account_name"}

  - `config.app_audit_info.dashboard_columns.fixed` (object)
    Example: {"Category":"category","Description":"description","Target":"target","Source":"tenant_name","Time":"audit_created_at","Username":"username"}

  - `config.app_audit_info.dashboard_columns.default` (object)
    Example: {"Category":"category","Time":"audit_created_at","Description":"description"}

  - `config.app_audit_info.order` (object)
    Example: {"Customer Name":2,"Category":0,"Description":1,"Time":8,"Username":7,"Device Type":3,"IP Address":4,"Target":6,"Source":5}

## Response 200 fields (application/json):

  - `message` (string)
    Audit Id.
    Example: "eUmWt44B1k6acmrQBqvH"


