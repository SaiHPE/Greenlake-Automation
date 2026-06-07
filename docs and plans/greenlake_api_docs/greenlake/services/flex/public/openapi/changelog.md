---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/flex/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:20.558791+00:00Z"
---

# Changelog

All notable changes to the APIs are documented in this file.

## Legend

The format is group changes to describe their impact on the project, as follows:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for once-stable features removed in upcoming releases.
- `Removed` for deprecated features removed in this release.
- `Fixed` for any bug fixes.
- `Security` to invite users to upgrade in case of vulnerabilities.


## May 1, 2026 - v1beta1

### Added

- Initial release of the HPE Flex Solutions API (`v1beta1`).
- `GET /flex/v1beta1/orders` — Retrieve and search for Flex orders with filtering, sorting, and pagination.
- `GET /flex/v1beta1/orders/transform` — Retrieve distinct transformative data for orders (group by SOW ID, customer, partner, etc.).
- `GET /flex/v1beta1/devices` — Retrieve and search for Flex devices with filtering, sorting, and pagination.
- `GET /flex/v1beta1/devices/{id}` — Retrieve a single device by resource ID.