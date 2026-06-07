---
title: "Server Firmware Download Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-firmware-download.md"
scraped_at: "2026-06-07T05:46:03.394492+00:00Z"
---

# Server Firmware Download Job

## Overview

This job initiates a server firmware download. The firmware is downloaded and stored in the iLO repository on the selected server. For more information, see [[firmware updates](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00004003en_us&page=GUID-7CD27F0E-FA58-4761-8961-ED48544BEA67.html)].

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 0683ada8-1a89-49dd-bf04-6df715b708a6 | compute-ops-mgmt/server | See [Job Parameters](#job-parameters) section |


> **Note**
Firmware download is not supported on HPE Edgeline e920 server blades.
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
| `downgrade` | boolean | Controls Firmware download downgrade option | No |
| `install_sw_drivers` | boolean | Controls HPE drivers and software installation | No |
| `prerequisite_check` | boolean | Prerequisites check before firmware download | No |
| `skip_blocklisted_components` | boolean | Skip component downloads that are blocked by known issues. | No |


### Parameter properties

- `bundle_id`: This **required** property is the firmware bundle UUID that should be used for the firmware download.
  - The firmware bundle UUID can be obtained using `GET /compute-ops-mgmt/v1/firmware-bundles` and looking at the `id` property
in the response.
- `downgrade`: This flag allows a downgrade of the firmware as part of the firmware download.
  - Default: `false`
- `install_sw_drivers`: This flag determines if HPE drivers and software should be downloaded as part of the firmware download.
  - **Note:** When enabled, this flag stores HPE drivers and software components in the iLO repository for later use. It will not install on the system.
  - Default: `false`
- `prerequisite_check`: This flag determines whether the prerequisites are checked before a firmware download.
  - Default: `true`
  - If the prerequisites check passed without recommendations, the firmware download proceeds.
  - If the prerequisites check failed with recommendations, fix the reported issues to continue with the firmware download.
- `skip_blocklisted_components`: This flag determines whether to skip component downloads that are blocked by known issues.
  - Default: `false`


## Example

Here's an example request payload for creating this job.

### Example 1

Use the specified firmware bundle to download components to the iLO repository on the selected server.


```json
{
  "jobTemplate": "0683ada8-1a89-49dd-bf04-6df715b708a6",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856227007",
  "jobParams": {
    "bundle_id": "5cda1141c85546319d00df4de60e6f72"
  }
}
```

### Example 2

Use the specified firmware bundle to download components to the iLO repository on the selected server including HPE drivers and software.


```json
{
  "jobTemplate": "0683ada8-1a89-49dd-bf04-6df715b708a6",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856227007",
  "jobParams": {
    "bundle_id": "5cda1141c85546319d00df4de60e6f72",
    "install_sw_drivers": true
  }
}
```

### Example 3

Use the specified firmware bundle to download downgrade components to the iLO repository on the selected server.


```json
{
  "jobTemplate": "0683ada8-1a89-49dd-bf04-6df715b708a6",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856227007",
  "jobParams": {
    "bundle_id": "5cda1141c85546319d00df4de60e6f72",
    "downgrade": true
  }
}
```

### Example 4

Use the specified firmware bundle to download components to the iLO repository on the selected server with prerequisite check.


```json
{
  "jobTemplate": "0683ada8-1a89-49dd-bf04-6df715b708a6",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856227007",
  "jobParams": {
    "bundle_id": "5cda1141c85546319d00df4de60e6f72",
    "prerequisite_check": true
  }
}
```

### Example 5

Use the specified firmware bundle to perform a server firmware download that skips components with known issues. The remaining components in the selected bundle are downloaded to the iLO repository on selected server.


```json
{
  "jobTemplate": "0683ada8-1a89-49dd-bf04-6df715b708a6",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "086856-F17+8899086856227007",
  "jobParams": {
    "bundle_id": "5cda1141c85546319d00df4de60e6f72",
    "skip_blocklisted_components": true
  }
}
```