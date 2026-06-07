---
title: "POST /audit-log/v2beta1/logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/openapi/audit-logs/v2beta1/audit-trail-publish-logs/publish-logs/publishserviceauditlog.md"
scraped_at: "2026-06-07T06:16:39.495625+00:00Z"
---

# Publish an audit log event.

This API facilitates the publication of audit logs by external and internal services that are part of the HPE GreenLake platform. 
It accepts detailed information regarding the audit log event, encompassing the service name, category, description, username, IP address, and any supplementary data. This operation is asynchronous, and the status of the publish operation can be monitored at the URI specified in the Location Response Header.
All the onboarded service offers on the GreenLake Platform must include the serviceOffer details in the audit log payload. Other core services that are part of the GreenLake platform can skip this field or set the serviceOffer.id to 00000000-0000-0000-0000-000000000000

A valid Service Identity workspace-scoped access token is required. For logs not tied to a workspace, use a token scoped to the Audit trail Undercloud workspace ID.

Rate Limits:

 - 3,000 requests per minute per service.
 - 9,000 requests per minute overall.

Endpoint: POST /audit-log/v2beta1/logs
Version: v2beta1
Security: Bearer

## Header parameters:

  - `Idempotency-key` (string)
    Optional unique identifier to ensure idempotency.
If the same key is received within 24 hours, it replaces the existing audit log. Prevents duplicate entries.

## Request fields (application/json):

  - `category` (string, required)
    Category of the audit event.

  - `description` (string, required)
    Description of the audit event.

  - `username` (string, required)
    Username of the user who performed the action. Set "System" for system events and "Internal" for the logs which should not be visible to the normal users. The internal logs are only visible to the Support engineers.

  - `createdAt` (integer, required)
    Unix epoch time in milliseconds when the event occurred.

  - `source` (string, required)
    Source of the audit event. Service name or component name

  - `ipAddress` (string)
    IPv4 and IPv6 address of the user who performed the action.

  - `slug` (string)
    Service slug code.

  - `serviceOffer` (object)
    Service offer details for which this audit log is published.

  - `serviceOffer.id` (string, required)
    Service offer ID.

  - `serviceOffer.region` (string, required)
    Service offer region where it is provisioned.

  - `auditDetails` (object)
    Additional details related to the event.

  - `auditDetails.header` (string)
    Heading of the audit details.

  - `auditDetails.body` (array)
    Actions performed in the audit event.

  - `additionalInfo` (object)
    Additional information for the audit event. Fields added in the additionalInfo can be made available in the UI by updating the platform audit configs.

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


## Response 202 fields
