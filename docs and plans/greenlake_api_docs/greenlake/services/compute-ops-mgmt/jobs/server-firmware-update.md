---
title: "Server Firmware Update Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-firmware-update.md"
scraped_at: "2026-06-07T05:46:04.100562+00:00Z"
---

# Server Firmware Update Job

## Overview

This job can be used to update the firmware on a server.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| fd54a96c-cabc-42e3-aee3-374a2d009dba | compute-ops-mgmt/server | See [Job Parameters](#job-parameters) section |


> **Note**
Firmware update is not supported on HPE Edgeline e920 server blades.
Job parameters marked with a `*` are required.


## Create Job

A job can be created by issuing a `POST` to the `/compute-ops-mgmt/v1/jobs` endpoint with the correct payload for the job.

The following properties are used when creating a job:

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `jobTemplate` | string (id) | The durable Template ID of the job | Yes |
| `resourceType` | string (type) | The TYPE of the resource the job will operate on | Yes |
| `resourceId` | string (id) | The ID of the resource the job will operate on | Yes |
| `jobParams` | object | Any additional data required by the job | No |


If the job was created successfully, a `201 Created` response is returned. The response includes the job resource which has a
job `resourceUri` that you can use to track the progress of the job.

## Job Parameters

This table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `bundle_id` | string (uuid) | Firmware Bundle UUID | Yes |
| `downgrade` | boolean | Controls Firmware update downgrade option | No |
| `install_sw_drivers` | boolean | Controls HPE drivers and software installation | No |
| `power_off` | boolean | Power off server after firmware update | No |
| `prerequisite_check` | boolean | Prerequisites check before firmware update | No |
| `skip_blocklisted_components` | boolean | Skip component updates that are blocked by known issues. | No |
| `wait_for_power_off_or_reboot` | boolean | Firmware update wait for server power off or reboot outside Compute Ops Management | No |
| `wait_for_power_off_or_reboot_timeout` | integer | Amount of time (hours) that Compute Ops Management waits for server power off or reboot | No |


### Parameter properties

- `bundle_id`: This **required** property is the firmware bundle UUID that should be used for the firmware update.
  - The firmware bundle UUID can be obtained using `GET /compute-ops-mgmt/v1/firmware-bundles` and looking at the `id` property
in the response.
- `downgrade`: This flag allows a downgrade of the firmware as part of the firmware update.
  - Default: `false`
- `install_sw_drivers`: This flag determines if HPE drivers and software should be installed in the OS as part of the firmware update.
  - Default: `false`
- `power_off`: This flag determines if server needs to be powered off after firmware update.
  - Default: `false`
- `prerequisite_check`: This flag determines whether the prerequisites are checked before a firmware update.
  - Default: `true`
  - If the prerequisites check passed without recommendations, the firmware update proceeds.
  - If the prerequisites check failed with recommendations, fix the reported issues to continue with the firmware update.
- `skip_blocklisted_components`: This flag determines whether to skip component updates that are blocked by known issues.
  - Default: `false`
- `wait_for_power_off_or_reboot`: This flag causes the update to wait for the user to reboot or power off the server before performing the installation.
  - Default: `false`
  - Note that the server reboot or power off must be performed outside of Compute Ops Management.
- `wait_for_power_off_or_reboot_timeout`: The amount of time in hours to wait for the server to reboot or power off, when the `wait_for_power_off_or_reboot` option is set to true.
  - Supported values are 1, 2, 4, 8, 12, 24
  - Default: 4


## Example

Here's an example request payload for creating this job.

### Example 1

Use the specified firmware bundle to update a server.


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce"
  }
}
```

### Example 2

Use the specified firmware bundle to update a server and power off the server after firmware update.


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce",
    "power_off": true
  }
}
```

### Example 3

Use the specified firmware bundle to update a server including HPE drivers and software.


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce",
    "install_sw_drivers": true
  }
}
```

### Example 4

Use the specified firmware bundle to update a server and allow to downgrade the firmware


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce",
    "downgrade": true
  }
}
```

### Example 5

Use the specified firmware bundle to update a server with prerequisite check.


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce",
    "prerequisite_check": true
  }
}
```

### Example 6

Use the specified firmware bundle to perform a server firmware update that skips components with known issues. The remaining components in the selected bundle are updated.


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce",
    "skip_blocklisted_components": true
  }
}
```

### Example 7

Use the specified firmware bundle to update a server after the user powers off or reboots the server within the specified time period.


```json
{
  "jobTemplate": "fd54a96c-cabc-42e3-aee3-374a2d009dba",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856117487",
  "jobParams": {
    "bundle_id": "de600c7f01e29f793f26ad91b31d96ce",
    "wait_for_power_off_or_reboot": true,
    "wait_for_power_off_or_reboot_timeout": 8
  }
}
```