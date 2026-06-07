---
title: "DELETE Service Offer Region Delete"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-registry-v1beta1/service_catalog_external_events/webhooks/paths/service%20offer%20region%20delete/delete.md"
scraped_at: "2026-06-07T06:15:45.648904+00:00Z"
---

# Service Offer Region Delete Event

A notification is sent when a service offer region has been deleted.Event type—com.hpe.greenlake.service-registry.v1.serviceofferregion.delete

Endpoint: DELETE Service Offer Region Delete
Version: 1.0.0

## Request fields (application/json):

  - `specversion` (string, required)
    The version of the CloudEvents specification the event adheres to.
    Example: 1

  - `id` (string, required)
    The unique identifier for the event.
    Example: "123e4567-e89b-12d3-a456-426614174000"

  - `source` (string, required)
    The source field is a URI reference that identifies the event producer.
    Example: "Compute"

  - `type` (string, required)
    The type of event.
    Example: "DELETE_SERVICE_OFFER_REGION"

  - `subject` (string, required)

  - `data` (object, required)
    The event payload.

  - `data.ServiceOfferID` (string)
    Service offer identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `data.ServiceOfferRegionID` (string)
    Service offer region identifier
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `data.ServiceOfferSlug` (string)
    Short identifier for a service offer. In case of an app provision, slug will be picked from service manager. If absent, slug will be picked from application.
    Example: "CENTRAL"

  - `data.AppID` (string)
    Unique application to which this service offer is associated with
    Example: "3fa85f64-5717-4562-b3fc-2c963f66afa6"

  - `data.Region` (string)
    Get service offer regions by region name
    Example: "us-east"

  - `time` (string)
    The date and time the event occurred in [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) format.
    Example: "2023-10-01T12:00:00Z"

  - `dataschema` (string)
    A URI pointing to the data property schema.

  - `datacontenttype` (string)
    The encoding of the data in the data property in [RFC 2046](https://datatracker.ietf.org/doc/html/rfc2046) format.


