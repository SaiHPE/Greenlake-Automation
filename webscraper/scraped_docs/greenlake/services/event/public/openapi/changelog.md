---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/event/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:20.452713+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

The format is group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2025 October

### Changed

* `POST /events/v1beta1/webhooks` and `PATCH /events/v1beta1/webhooks`—Webhooks can now be configured to receive event messages in batches using the `batching` boolean in the API payload. The default is `"batching": false`, indicating that events are sent individually. Set to `"batching": true` to receive events in batches.
* The webhook verification process is now optional. However, it is strongly recommended to use webhook verification for security purposes. As a result of this change, the process for setting a rate limit was changed to use an implementation of the HTTP OPTIONS method.


## 2025-July

### Added

* The following endpoints were introduced to perform CRUD operations related to webhook:
  * `POST /events/v1beta1/webhooks`—This endpoint allows clients to create a new webhook to establish a callback mechanism for key events on GLCP services.
  * `GET /events/v1beta1/webhooks`—Retrieves a list of webhooks, organized in descending order based on their creation time.
  * `GET /events/v1beta1/webhooks/{id}`—Retrieve detailed information about a specific webhook by its unique identifier.
  * `PATCH /events/v1beta1/webhooks/{id}`—Update an existing webhook's settings, such as its name, description, destination, and so on.
  * `DELETE /events/v1beta1/webhooks/{id}`—Remove a specific webhook from the system.
  * `GET /events/v1beta1/webhooks/{id}/verify`—This endpoint is designed to ensure the webhook URL provided by the user is correct and the server is prepared to receive webhook requests.
  * `GET /events/v1beta1/webhooks/{id}/recent-deliveries`—This endpoint is dedicated to retrieve detailed information about recent deliveries for a specific webhook.
  * `POST /events/v1beta1/webhooks/{id}/delivery-failures/{failureId}/retry`—This endpoint is dedicated to retry delivery failures for a specific webhook.
* The following endpoints were introduced to perform CRUD operations related to subscriptions:
  * `POST /events/v1beta1/subscriptions`—Register a new subscription to start receiving event notifications through the configured webhook.
  * `GET /events/v1beta1/subscriptions`—Retrieves a list of subscriptions associated to webhooks, organized in descending order based on their creation time.
  * `DELETE /events/v1beta1/subscriptions`—Delete the list of subscriptions by the IDs, stopping further event notification linked to the subscriptions.
  * `PATCH /events/v1beta1/subscriptions`—Update all subscription identified by the given IDs.