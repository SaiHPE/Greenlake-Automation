---
title: "Group Firmware Download Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-firmware-download.md"
scraped_at: "2026-06-07T05:46:02.240878+00:00Z"
---

# Group Firmware Download Job

## Overview

This job initiates a group firmware download on selected or all devices present in a group. The firmware is downloaded and stored in the iLO repository on each selected server. For more information, see [[firmware updates](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00004003en_us&page=GUID-7CD27F0E-FA58-4761-8961-ED48544BEA67.html)].

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 0683ada8-1a89-49dd-bf04-6df715b708a6 | compute-ops-mgmt/group | See [Job Parameters](#job-parameters) section |


> **Note**
Firmware download is not supported on HPE Edgeline e920 server blades.


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
| `downgrade` | boolean | Controls Firmware download downgrade option | No |
| `installSWDrivers` | boolean | Controls HPE drivers and software download | No |
| `prerequisite_check` | boolean | Prerequisites check before firmware download | No |
| `skip_blocklisted_components` | boolean | Skip component downloads that are blocked by known issues. | No |


### Parameter properties

- `devices`: This property is a list of server IDs to include in the server group firmware download. All devices in the list must belong to the group.
  - Default: All devices currently part of the group will be included.
- `downgrade`: This flag allows a downgrade version of the firmware components as part of the firmware download.
  - Default: `false`
- `installSWDrivers`: This flag determines if HPE drivers and software components should be downloaded as part of the firmware download.
  - **Note:** When enabled, this flag stores HPE drivers and software components in the iLO repository for later use. It will not install on the system.
  - Default: `false`
- `prerequisite_check`: This flag determines whether the prerequisites are checked before a firmware download.
  - Default: `true`
  - If the prerequisites check passed without recommendations, the firmware download proceeds.
  - If the prerequisites check failed with recommendations, fix the reported issues to continue with the firmware download.
- `skip_blocklisted_components`: This flag determines whether to skip component downloads that are blocked by known issues.
  - Default: `false`


## Examples

Here are a couple of example request payloads for creating this job.

### Example 1

Download firmware for all servers in a group.


```json
{
  "jobTemplate": "a17a7aa9-4540-4c21-bbf2-31af4ff65e98",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "04460955-6038-4339-ba72-c9b05a03876e"
}
```

### Example 2

Download firmware for two servers in a group including HPE drivers and software.


```json
{
  "jobTemplate": "a17a7aa9-4540-4c21-bbf2-31af4ff65e98",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "installSWDrivers": true
  }
}
```

### Example 3

Download firmware of downgraded version of components for two servers in a group.


```json
{
  "jobTemplate": "a17a7aa9-4540-4c21-bbf2-31af4ff65e98",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "downgrade": true
  }
}
```

### Example 4

Download firmware for two servers in a group with a prerequisite check.


```json
{
  "jobTemplate": "a17a7aa9-4540-4c21-bbf2-31af4ff65e98",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "prerequisite_check": true
  }
}
```

### Example 5

Download firmware on two servers in a group and skip components that are blocked by known issues.


```json
{
  "jobTemplate": "a17a7aa9-4540-4c21-bbf2-31af4ff65e98",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "a3853ee1-da05-47d6-bcc4-d35244d59605",
  "jobParams": {
    "devices": ["063573-L08+8899063573208133", "855308-N51+8899855308351678"],
    "skip_blocklisted_components": true
  }
}
```