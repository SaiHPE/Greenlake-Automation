---
title: "HPE GreenLake for Locations service glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/glossary.md"
scraped_at: "2026-06-07T05:46:11.891482+00:00Z"
---

# HPE GreenLake for Locations service glossary

## Terms

### Contact types

There are four contact types:

- Operations
- Primary
- Security
- Shipping_receiving


You must assign only one primary contact for a location. You can optionally assign one or multiple security, shipping and receiving, and operations contacts.

### Location events

Location events are generated and stored in the audit logs when a location is created, updated, or deleted and provide detailed insight into the operation—view location events in the audit logs.

### Location ID

An identifier generated after a location is created that is used to fetch a specific location.

A location ID is a 32 digit auto-generated alphanumeric number, for example, `945e70ec-b043-4cad-9ed0-069c06fdb8af`.

### Location type

Defines the type of location created. The type is always set to `Building`.

### Location validation

HPE GreenLake workspace administrators can validate that location information is correct and up to date. Workspace administrators can decide on a location revalidation cycle. By default, the cycle is six months. However, 12- and 18-month revalidation cycles are possible too. Workspace administrators receive a notification in the notification center when the cycle elapses.

### Location Tags

Tags can be created for a specific location. HPE GreenLake workspace administrators can manage tags for a specific location and view all the tags associated with a specific location.