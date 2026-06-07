---
title: "Group Firmware Update Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-firmware-update.md"
scraped_at: "2026-06-07T05:46:02.290929+00:00Z"
---

# Group Firmware Update Job

## Overview

This job initiates a server group firmware update that will affect some or all of the
server group members.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 91159b5e-9eeb-11ec-a9da-00155dc0a0c0 | compute-ops-mgmt/group | See [Job Parameters](#job-parameters) section |


> **Note**
Firmware update is not supported on HPE Edgeline e920 server blades.


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

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `devices` | array | List of server IDs | No |
| `parallel` | boolean | Perform server firmware updates in parallel | No |
| `stopOnFailure` | boolean | Stop after the first server firmware update failure | No |
| `downgrade` | boolean | Controls Firmware update downgrade option | No |
| `installSWDrivers` | boolean | Controls HPE drivers and software installation | No |
| `powerOff` | boolean | Power off server after firmware update | No |
| `prerequisite_check` | boolean | Prerequisites check before firmware update | No |
| `skip_blocklisted_components` | boolean | Skip component updates that are blocked by known issues. | No |
| `wait_for_power_off_or_reboot` | boolean | Firmware update wait for server power off or reboot outside Compute Ops Management | No |
| `wait_for_power_off_or_reboot_timeout` | integer | Amount of time (hours) that Compute Ops Management waits for server power off or reboot | No |


### Parameter properties

- `devices`: This property is a list of server IDs to include in the server group firmware update. All devices in the list must belong to the group.
- `parallel`: This flag determines if the firmware updates to each device in the group should occur in parallel or not.
  - Default: `false`
- `stopOnFailure`: This flag is applicable for serial firmware updates (i.e. `parallel: false`). It determines if the group
firmware update process will continue after the first failure. If the flag is `false`, the update continues after a failure. If
the flag is `true`, the update stops after a failure and the remaining devices in the group will not be updated.
  - Default: `false`
- `downgrade`: This flag allows a downgrade of the firmware as part of the firmware update.
  - Default: `false`
- `installSWDrivers`: This flag determines if HPE drivers and software should be installed in the OS as part of the firmware update.
  - Default: `false`
- `powerOff`: This flag determines if server needs to be powered off after firmware update.
  - Default: `false`
- `prerequisite_check`:This flag determines whether the prerequisites are checked before a firmware update.
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


## Patch Job

A job can be patched by issuing a `PATCH` to the `/compute-ops-mgmt/v1/jobs/<job-id>` endpoint with the correct payload for the job.

The following property is used when patching a job:

| Property | JSON Type | Description |
|  --- | --- | --- |
| `input` | object | Any input data required by the job. |


If the job was patched successfully, a `200` response is returned. The response includes the job resource which has a
job `resourceUri` that you can use to track the progress of the job.

## Input

This table summarizes the supported properties for `input`.

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `stopOnRequest` | boolean | To cancel the serial firmware update | No |


### Input properties

- `stopOnRequest`: This flag is applicable for serial firmware updates (i.e. `parallel: false`). It determines whether the firmware update
has to be cancelled. If the flag is `true`, the ongoing firmware update will run to complete, however, the update is cancelled on all
servers that have not started the update.


## Examples

Here are a couple of example request payloads for creating this job.

### Example 1

Update firmware for all servers in a group.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "04460955-6038-4339-ba72-c9b05a03876e"
}
```

### Example 2

Update firmware for two servers in a group in parallel.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "parallel": true
  }
}
```

### Example 3

Update firmware for two servers in a group and power off them after firmware update.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "parallel": true,
    "powerOff": true
  }
}
```

### Example 4

Update firmware for two servers in a group including HPE drivers and software.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "installSWDrivers": true
  }
}
```

### Example 5

Update firmware for two servers in a group and allow to downgrade the firmware.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "downgrade": true
  }
}
```

### Example 6

Update firmware for two servers in a group after the user powers off or reboots the servers within the specified time period.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "wait_for_power_off_or_reboot": true,
    "wait_for_power_off_or_reboot_timeout": 8
  }
}
```

### Example 7

Update firmware for two servers in a group with a prerequisite check.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "prerequisite_check": true
  }
}
```

### Example 8

Update firmware on two servers in a group and skip components that are blocked by known issues.


```json
{
  "jobTemplate": "91159b5e-9eeb-11ec-a9da-00155dc0a0c0",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "skip_blocklisted_components": true
  }
}
```

An example of patching this job

### Example 9

Cancel the ongoing group firmware update job triggered with the serial option.

Patch the ongoing group firmware update job triggered with serial option (ie parallel=false)
with the following option.


```json
{
  "input": {
    "stopOnRequest": true
  }
}
```