---
title: "POST /accounts/v1alpha1/events"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/identity/public/openapi/identity-v1/event_api/other/processevent.md"
scraped_at: "2026-06-07T06:15:28.140297+00:00Z"
---

# Process event

Process an event according the data received.

Endpoint: POST /accounts/v1alpha1/events
Version: v1alpha1
Security: BearerAuth

## Request fields (application/json):

  - `id` (string, required)
    Unique identifier for the event

  - `source` (string, required)
    Source of the event
    Example: "sso-manager"

  - `type` (string, required)
    Type of the event
    Example: "hpe.greenlake.identity.v1alpha1.sso-routing-rule.update"

  - `time` (string, required)
    Timestamp when the event occurred

  - `data` (object)
    Event payload data
    Example: {"id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","domain":"example.com","newConfiguration":{"ssoMode":"authentication-only-msp-managed"},"previousConfiguration":{"ssoMode":"authentication-only"},"associatedOrganization":{"id":"3fa85f64-5717-4562-b3fc-2c963f66afa6","resourceUri":"uri.com/3fa85f64-5717-4562-b3fc-2c963f66afa6"}}

## Response 202 fields (application/json):

  - `message` (string, required)

## Response 400 fields (application/json):

  - `message` (string, required)

  - `errorCode` (string, required)

  - `debugId` (string, required)

  - `httpStatusCode` (integer, required)

## Response 401 fields (application/json):

  - `message` (string, required)

  - `errorCode` (string, required)

  - `debugId` (string, required)

  - `httpStatusCode` (integer, required)

## Response 403 fields (application/json):

  - `message` (string, required)

  - `errorCode` (string, required)

  - `debugId` (string, required)

  - `httpStatusCode` (integer, required)

## Response 500 fields (application/json):

  - `message` (string, required)

  - `errorCode` (string, required)

  - `debugId` (string, required)

  - `httpStatusCode` (integer, required)


