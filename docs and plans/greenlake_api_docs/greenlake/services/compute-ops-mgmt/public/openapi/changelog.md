---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/changelog.md"
scraped_at: "2026-06-07T05:46:19.437217+00:00Z"
---

# Changelog

All notable changes to the public APIs are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

Group changes to describe their impact on the project, as follows:

* `Added` for new features.
* `Changed` for changes in existing functionality.
* `Deprecated` for once-stable features removed in upcoming releases.
* `Removed` for deprecated features removed in this release.
* `Fixed` for any bug fixes.
* `Security` to invite users to upgrade in case of vulnerabilities.


## 2025-06-09

### Added

The following public APIs were added.

* GET  /compute-ops-mgmt/v1beta1/utilization-over-time
* GET  /compute-ops-mgmt/v1beta1/utilization-by-entity


## 2025-05-20

### Deprecated

The following public APIs were deprecated.

* POST /compute-ops-mgmt/v1beta1/metrics-configurations
* GET /compute-ops-mgmt/v1beta1/metrics-configurations
* GET /compute-ops-mgmt/v1beta1/metrics-configurations/{id}
* PATCH /compute-ops-mgmt/v1beta1/metrics-configurations/{id}
* DELETE /compute-ops-mgmt/v1beta1/metrics-configurations/{id}


## 2025-04-17

### Added

The following public APIs were added.

* GET  /compute-ops-mgmt/v1beta1/energy-over-time
* GET  /compute-ops-mgmt/v1beta1/energy-by-entity


## 2025-03-20

### Added

The following public APIs were added.

* POST  /compute-ops-mgmt/v1beta1/ahs-files
* PATCH /compute-ops-mgmt/v1beta1/ahs-files/{id}
* POST  /compute-ops-mgmt/v1beta1/ahs-files/{id}/parse
* GET   /compute-ops-mgmt/v1beta1/ahs-files
* GET   /compute-ops-mgmt/v1beta1/ahs-files/{id}


## 2024-12-11

### Deprecated

Compute Ops Management is completing the process of renaming the URI path prefix from `/compute-ops` to `/compute-ops-mgmt`.
The `/compute-ops` prefix is deprecated and might become unresponsive after Tuesday, April 1, 2025.
The [Guide](/docs/greenlake/services/compute-ops-mgmt/public/guide#uri-path-prefix-rename) provides more information about this change.

## 2024-11-07

### Deprecated

The following public APIs were deprecated.

* GET /compute-ops-mgmt/v1/servers/{id}/raw-inventory
* GET /compute-ops-mgmt/v1beta2/servers/{id}/raw-inventory


## 2024-10-30

### Added

The following public APIs were added.

* POST /compute-ops-mgmt/v1beta1/activation-keys
* GET  /compute-ops-mgmt/v1beta1/activation-keys
* DELETE /compute-ops-mgmt/v1beta1/activation-keys/{activation_key}


## 2024-09-16

Added the new version of public API (version v1) for Compute Ops Management `groups`, `settings` and `async-operations` for managing groups and settings.

### Added

The following public APIs were added.

* GET compute-ops-mgmt/v1/async-operations
* GET compute-ops-mgmt/v1/async-operations/{id}
* GET compute-ops-mgmt/v1/groups
* POST compute-ops-mgmt/v1/groups
* GET compute-ops-mgmt/v1/groups/{group-id}
* DELETE compute-ops-mgmt/v1/groups/{group-id}
* PATCH compute-ops-mgmt/v1/groups/{group-id}
* GET compute-ops-mgmt/v1/groups/{group-id}/compliance
* GET compute-ops-mgmt/v1/groups/{group-id}/compliance/{compliance-id}
* GET compute-ops-mgmt/v1/groups/{group-id}/devices
* POST compute-ops-mgmt/v1/groups/{group-id}/devices
* POST compute-ops-mgmt/v1/groups/{group-id}/devices/unassign
* GET compute-ops-mgmt/v1/groups/{group-id}/external-storage-compliance
* GET compute-ops-mgmt/v1/settings
* POST compute-ops-mgmt/v1/settings
* GET compute-ops-mgmt/v1/settings/{id}
* DELETE compute-ops-mgmt/v1/settings/{id}
* PATCH compute-ops-mgmt/v1/settings/{id}


## 2024-09-02

Added the new version of public API (version v1) for Compute Ops Management `metrics-configurations` for managing the metrics data collection setting.

### Added

The following public APIs were added.

* POST /compute-ops-mgmt/v1/metrics-configurations
* GET /compute-ops-mgmt/v1/metrics-configurations
* GET /compute-ops-mgmt/v1/metrics-configurations/{id}
* PATCH /compute-ops-mgmt/v1/metrics-configurations/{id}
* DELETE /compute-ops-mgmt/v1/metrics-configurations/{id}


## 2024-08-14

Added the initial public API (version v1beta1) for Compute Ops Management `oneview-server-templates`. These APIs can be used to manage the OneView server profile template inventory.

### Added

The following public APIs were added.

* GET /compute-ops-mgmt/v1beta1/oneview-server-templates
* GET /compute-ops-mgmt/v1beta1/oneview-server-templates/{id}


### Changed

v1beta1/settings
Added the request and response specific to OneView Server Template settings.

## 2024-08-13

One of the main drivers for the Group v1beta3 API and the Settings v1beta1 API (derived from "server-settings") is the redesign of server-centric routes and attributes to support OneView appliance groups. Besides the general renaming of `server` to `device` across resources, the old `platformFamily` attribute for the Group resource was replaced by an immutable `deviceType` attribute which must be supplied at create time with one of the following values: `DIRECT_CONNECT_SERVER`, `OVE_APPLIANCE_SYNERGY`, `OVE_APPLIANCE_VM`.

Another significant change for the Group v1beta3 API is the introduction of an asynchronous approach for adding and removing devices from a group. The asynchronous operations can be tracked through the new async-operations v1beta1 API.

Note that all of these new endpoints utilize the new public URI path prefix for Compute Ops Management which is `compute-ops-mgmt`.

### Added

The following public APIs were added.

* GET /compute-ops-mgmt/v1beta1/async-operations
* GET /compute-ops-mgmt/v1beta1/async-operations/{id}
* GET /compute-ops-mgmt/v1beta3/groups
* POST /compute-ops-mgmt/v1beta3/groups
* GET /compute-ops-mgmt/v1beta3/groups/{group-id}
* DELETE /compute-ops-mgmt/v1beta3/groups/{group-id}
* PATCH /compute-ops-mgmt/v1beta3/groups/{group-id}
* GET /compute-ops-mgmt/v1beta3/groups/{group-id}/compliance
* GET /compute-ops-mgmt/v1beta3/groups/{group-id}/compliance/{compliance-id}
* GET /compute-ops-mgmt/v1beta3/groups/{group-id}/devices
* POST /compute-ops-mgmt/v1beta3/groups/{group-id}/devices
* POST /compute-ops-mgmt/v1beta3/groups/{group-id}/devices/unassign
* GET /compute-ops-mgmt/v1beta3/groups/{group-id}/external-storage-compliance
* GET /compute-ops-mgmt/v1beta1/oneview-settings
* GET /compute-ops-mgmt/v1beta1/settings
* POST /compute-ops-mgmt/v1beta1/settings
* GET /compute-ops-mgmt/v1beta1/settings/{id}
* DELETE /compute-ops-mgmt/v1beta1/settings/{id}
* PATCH /compute-ops-mgmt/v1beta1/settings/{id}


## Removed

The following public APIs were removed.

* POST /compute-ops/v1beta1/oneview-appliances/{id}/compliance
* GET /compute-ops/v1beta1/oneview-appliances/{id}/compliance/{sub-id}
* GET /compute-ops/v1beta1/oneview-settings-templates
* GET /compute-ops/v1beta1/oneview-settings-templates/{id}
* POST /compute-ops/v1beta1/oneview-settings-templates
* POST /compute-ops/v1beta1/oneview-settings-templates/{id}/apply
* DELETE /compute-ops/v1beta1/oneview-settings-templates/{id}


## 2024-06-04

### Added

The following public API was added.

* POST /compute-ops-mgmt/v1beta1/activation-tokens


## 2024-05-27

### Deprecated

The following public APIs were deprecated.

* GET /compute-ops/v1beta1/reports
* GET /compute-ops/v1beta1/reports/{id}
* GET /compute-ops/v1beta1/reports/{id}/data
* GET /compute-ops-mgmt/v1beta1/reports
* GET /compute-ops-mgmt/v1beta1/reports/{id}
* GET /compute-ops-mgmt/v1beta1/reports/{id}/data


## 2024-05-15

### Deprecated

The following public APIs were deprecated.

* POST /compute-ops/v1beta1/oneview-appliances/{id}/compliance
* GET /compute-ops/v1beta1/oneview-appliances/{id}/compliance/{sub-id}
* GET /compute-ops/v1beta1/oneview-settings-templates
* GET /compute-ops/v1beta1/oneview-settings-templates/{id}
* POST /compute-ops/v1beta1/oneview-settings-templates
* POST /compute-ops/v1beta1/oneview-settings-templates/{id}/apply
* DELETE /compute-ops/v1beta1/oneview-settings-templates/{id}


## 2024-05-01

### Changed

The URI path prefix is in the process of being renamed from `/compute-ops` to `/compute-ops-mgmt` for all API endpoints.
During the transition period the majority of APIs will be available on both the old and new URI path prefixes. The
[Guide](/docs/greenlake/services/compute-ops-mgmt/public/guide#uri-path-prefix-rename) contains more information about this change.

## 2024-03-14

Added the initial public API (version v1beta1) for Compute Ops Management `appliance-firmware-bundles`. These APIs can be used
to view firmware bundles for HPE OneView appliances in Compute Ops Management. Note: These APIs follow the new public API path
for Compute Ops Management which is `compute-ops-mgmt`, not `compute-ops`.

### Added

The following public APIs were added.

* GET compute-ops-mgmt/v1beta1/appliance-firmware-bundles
* GET compute-ops-mgmt/v1beta1/appliance-firmware-bundles/{id}


## 2024-02-27

Added the initial public API (version v1beta1) for Compute Ops Management `server-locations`. These APIs can be used to manage
the location of HPE OneView managed servers in Compute Ops Management. Note: These APIs follow the new public API path for
Compute Ops Management which is `compute-ops-mgmt`, not `compute-ops`. To manage the location of directly managed servers, use
the HPE GreenLake APIs.

### Added

The following public APIs were added.

* POST compute-ops-mgmt/v1beta1/server-locations/{location_id}/servers
* GET compute-ops-mgmt/v1beta1/server-locations/{location_id}
* DELETE compute-ops-mgmt/v1beta1/server-locations/{location_id}/servers


## 2024-02-21

### Removed

* The direct endpoints `<region>-api.compute.cloud.hpe.com` were removed. Use the HPE GreenLake API endpoints `<region>.api.greenlake.hpe.com` instead.


## 2024-02-02

### Changed

* HPE GreenLake API endpoints `<region>.api.greenlake.hpe.com` were added alongside the direct endpoints `<region>-api.compute.cloud.hpe.com`.
The [Guide](/docs/greenlake/services/compute-ops-mgmt/public/guide#endpoint-changes) contains more information about this change.


## 2023-11-27

The initial public API (version v1beta1) was added for Compute Ops Management `webhooks`. Note that these follow the new
public URI path prefix for Compute Ops Management which is `compute-ops-mgmt`, not `compute-ops`.

### Added

The following public APIs were added.

* GET compute-ops-mgmt/v1beta1/webhooks
* POST compute-ops-mgmt/v1beta1/webhooks
* GET compute-ops-mgmt/v1beta1/webhooks/{webhook_id}
* PATCH compute-ops-mgmt/v1beta1/webhooks/{webhook_id}
* DELETE compute-ops-mgmt/v1beta1/webhooks/{webhook_id}
* GET compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries
* GET compute-ops-mgmt/v1beta1/webhooks/{webhook_id}/deliveries/{delivery_id}


## 2023-10-26

Introduced v1beta2 for the `reports` resource to adjust the structure of the response. The `data` property is newly introduced
to support different report types. Added a new public option for configuring the Metrics data collection setting (v1beta1).

### Added

The following public APIs and top level resource was added.

* GET compute-ops/v1beta2/reports
* POST compute-ops/v1beta2/reports
* GET compute-ops/v1beta2/reports/{id}
* GET compute-ops/v1beta2/reports/{id}/data
* metrics-configurations


## 2023-08-17

Added the initial public API (version v1beta1) for Compute Ops Management `user-preferences`. These APIs can be used to manage
alert email user preferences in Compute Ops Management.

### Added

The following public APIs were added.

* GET compute-ops/v1beta1/user-preferences
* POST compute-ops/v1beta1/user-preferences
* GET compute-ops/v1beta1/user-preferences/{id}
* PUT  compute-ops/v1beta1/user-preferences/{id}


## 2023-06-07

### Added

The initial public API (version v1beta1) was added for the following top-level resource:

* external-services


## 2023-01-11

Introduced version v1beta3 for the `jobs` resource. The v1beta3 jobs resource has a new `resultCode` field and the `state` field meaning and values have changed.
For more information about this change see the **Monitoring Jobs** section on the Job Definitions [Overview](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/) page.

### Added

The following public APIs were added.

GET compute-ops/v1beta3/jobs
POST compute-ops/v1beta3/jobs
GET compute-ops/v1beta3/jobs/{id}
PATCH compute-ops/v1beta3/jobs/{id}

## 2022-12-13

### Changed

v1beta2/groups

* Changed existing/default value for the optional `platformFamily` property to `ANY`


v1beta1/server-settings

* Changed existing/default value for the optional `platformFamily` property to `ANY`


## 2022-11-30

### Changed

v1beta2/groups

* properties added:
  * `serverPolicies.onServerAdd.biosApplySettings`


## 2022-10

### Added

The initial public API (version v1beta1) was added for the following top-level resources:

* filters
* reports


### Removed

The v1beta1 version for the following resources has been removed:

* servers
* jobs
* job-templates
* activities
* firmware-bundles
* schedules


## 2022-09

Introduced version v1beta2 for the groups resource.

### Added

The initial public API (version v1beta1) was added for the following top-level resource:

* server-settings


The following public APIs were added:

* PATCH v1beta2/servers
* PATCH v1beta2/servers/{id}
* GET v1beta2/servers/{id}/notifications
* PUT v1beta2/servers/{id}/notifications


### Changed

v1beta2/groups

* properties added:
  * `platformFamily`
* properties removed:
  * `firmwareBaseline`
  * `autoIloFwUpdateEnabled`
  * `policyUri`
  * `tags`
* properties renamed:
  * From `deviceSettingsUris` to `serverSettingsUris`


v1beta2/servers

* properties added:
  * `autoIloFwUpdate`


### Removed

Version v1beta1 for the groups resource has been removed.

## 2022-08

Introducing version v1beta2 with the following changes. All properties listed
as removed have a replacement property in the new version.

| Removed property | Replaced by |
|  --- | --- |
| `selfUri` | `resourceUri` |
| `displayName` | `name` |
| `modifiedAt` | `updatedAt` |
| `start` | `offset` |


> Note: The replacement properties were added in v1beta1 and are not new in v1beta2.


### Added

* GET v1beta2/servers/{id}/raw-inventory


### Changed

* v1beta2/servers
  * `filter` query parameter added
  * properties removed:
    * Renamed `resourceType` to `type`
    * `selfUri`
    * `displayName`
    * `modifiedAt`
    * `start` parameter for pagination
* v1beta2/job-templates properties removed:
  * `selfUri`
  * `displayName`
  * `start` parameter for pagination
* v1beta2/jobs properties removed:
  * `selfUri`
  * `displayName`
  * `modifiedAt`
  * `start` parameter for pagination
* v1beta2/activities properties removed:
  * `selfUri`
  * `displayName`
  * `modifiedAt`
  * `start` parameter for pagination
* v1beta2/firmware-bundles properties changed:
  * `selfUri`
  * `displayName`
  * `start` parameter for pagination
  * Renamed `type` to `bundleType`
  * Renamed `resourceType` to `type`
  * v1beta1 properties example:

```json
{
  "type": "HOTFIX",
  "resourceType": "compute-ops/firmware-bundle"
}
```
  * v1beta2 properties example:

```json
{
  "bundleType": "HOTFIX",
  "type": "compute-ops/firmware-bundle"
}
```
* v1beta2/schedules properties removed:
  * `start` parameter for pagination
* v1beta2/schedules/{schedule-id}/history properties removed:
  * `start` parameter for pagination


## 2022-06

### Added

The initial public API was added with the following top-level resources:

* activities
* firmware-bundles
* groups
* job-templates
* jobs
* servers
* schedules