---
title: "Changelog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/changelog.md"
scraped_at: "2026-06-07T06:13:22.457097+00:00Z"
---

# Changelog

All notable changes to the Job definitions are documented in this file.

## Legend

Based on: [https://keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/)

Group changes to describe their impact on the project, as follows:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for once-stable features removed in upcoming releases.
- `Removed` for deprecated features removed in this release.
- `Fixed` for any bug fixes.
- `Security` to invite users to upgrade in case of vulnerabilities.


## 2026-06-01

### Added

The following job definitions were added:

- Server Enable Maintenance Mode
- Server Disable Maintenance Mode


These jobs control enabling maintenance mode on selected servers to suspend automatic support case creation, ServiceNow incident creation, and email notifications during planned maintenance.

## 2026-02-05

### Added

The following job definitions were added:

- vCenter Firmware Bundles Sync
- Delete vCenter


These jobs manage VMware vCenter external service integrations for firmware bundle synchronization and service deletion.

## 2025-12-05

### Added

The following job definitions were added:

- Server UID Indicator On
- Server UID Indicator Off


These jobs control the UID (Unit Identification) indicator light on servers to help physically identify specific servers in a data center.

## 2025-10-16

### Changed

The following job definitions were added:

- Server firmware download
- Group firmware download


## 2025-08-12

### Changed

Updated internal storage job definitions.

## 2025-07-14

### Removed

`Carbon Footprint Report` job template with ID `b0001d36-6490-48ac-93af-a87adfb997ed` is removed. Use Compute Ops Management Create report API for report creation.

## 2025-04-17

### Changed

Job Definition documentation updated to match the V1 API version.

## 2025-04-16

### Added

- Added a section on migrating to the stable `v1` API.
- Included an example of monitoring a job using the `v1` API.


### Changed

- Updated the job overview page to reflect the new stable `v1` API.
- Replaced `jobTemplateUri` with `jobTemplate`.
- Split `resourceUri` into `resourceType` and `resourceId`.
- Replaced `data` with `jobParams`.


## 2025-02-06

### Added

The following job definitions were added:

- Group Appliance Update


### Changed

The following job definitions were changed:

- Appliance Firmware Update was renamed to Appliance Software Update.


## 2024-08-14

### Added

The following job definitions were added:

- Group Apply OneView Server Templates
  - This job copies the server templates in the configured setting to the selected target appliance group members.
- Settings Update OneView Server Template
  - This job updates selected server templates within the OneView server template setting.


## 2024-08-13

### Added

The following job definitions were added:

- Group Apply OneView appliance settings
  - This job applies OneView appliance settings to specified OneView appliances in the group.
- Refresh OneView appliance settings
  - This job retrieves appliance settings data from a specified appliance to refresh the OneView appliance settings cache in Compute Ops Management.


## 2024-05-01

### Changed

All jobs were updated to reflect the new URI path prefix `/compute-ops-mgmt`. The [Guide](/docs/greenlake/services/compute-ops-mgmt/public/guide#uri-path-prefix-rename)
contains more information about this change.

## 2024-04-30

### Added

The following job definitions were added:

- Group Apply External Storage Settings
  - This job applies external storage settings to all servers in a group.
- Group External Storage Compliance
  - This job initiates an external storage compliance check on all servers in a group.
- Server External Storage Details
  - This job initiates the collection of external storage details for a server.


## 2024-04-04

### Changed

The following Job definitions were changed:

- Group OS Installation


## 2024-03-07

### Added

The following job definition was added:

- Appliance Firmware Update
  - This job can be used to update an HPE OneView appliance.


## 2024-01-25

### Added

The following job definitions were added:

- Configure ignore iLO security risk settings


## 2023-12-21

### Added

The following job definition was added:

- Server Network Connectivity
  - This job can be used to collect server network connectivity information for directly managed servers.


## 2023-10-17

### Added

The following job definition was added:

- Server Inventory
  - This job can be used to collect complete or filtered server inventory information from directly managed and OneView managed servers.


## 2023-09-14

### Added

The following job definition was added:

- Group OS installation
  - This job can be used to install operating system that will affect some or all of the server group members.


## 2023-04-20

### Added

The following job definition was added:

- Carbon Footprint Report
  - This job can be used to generate the Carbon Footprint Report.


## 2023-04-03

### Changed

The following job definitions were Changed:

- Group Firmware Update
  - Added the ability to do a prerequisites check before a firmware update using the `prerequisite_check` attribute
- Server Firmware Update
  - Added the ability to do a prerequisites check before a firmware update using the `prerequisite_check` attribute


## 2023-02-01

### Changed

The following job definition was added:

- Server iLO firmware update
  - This job can be used to update the iLO firmware component on a server.


## 2023-1-11

Introduced version v1beta3 for the jobs resource. The v1beta3 jobs resource has a new `resultCode` field and the `state` field meaning and values have changed.
For more information about this change see the **Monitoring Jobs** section on the Job Definitions [Overview](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/) page.

### Added

The following public APIs were added.

GET compute-ops/v1beta3/jobs
POST compute-ops/v1beta3/jobs
GET compute-ops/v1beta3/jobs/{id}
PATCH compute-ops/v1beta3/jobs/{id}

## 2022-12-16

### Changed

The following job definitions was Changed:

- Group Firmware Update
  - Added the ability to power off the server after a firmware update using the `powerOff` attribute
- Server Firmware Update
  - Added the ability to power off the server after a firmware update using the `powerOff` attribute
  - Added the ability to install HPE drivers and software as part of firmware update using the `install_sw_drivers` attribute


## 2022-12-08

### Changed

The following job definition was changed:

- Group Firmware Update
  - Devices field is optional for this job


## 2022-12-05

### Added

The following job definitions were added:

- Group Apply Server Setting Job
  - Currently this job supports BIOS server setting


## 2022-12-02

### Added

The following job definitions were added:

- Group Apply Internal Storage Configuration


## 2022-09-01

### Added

The following Job definitions were added:

- Server Power Off
- Server Power On
- Server Restart
- Server Cold Boot
- Server Firmware Update
- Group Firmware Update
- Group Firmware Compliance