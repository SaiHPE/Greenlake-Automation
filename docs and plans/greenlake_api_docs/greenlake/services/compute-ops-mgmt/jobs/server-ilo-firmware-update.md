---
title: "Server iLO Firmware Update Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-ilo-firmware-update.md"
scraped_at: "2026-06-07T05:46:04.148370+00:00Z"
---

# Server iLO Firmware Update Job

## Overview

This job can be used to update the iLO firmware component on a server.

> **iLO Firmware Update**: Initiate an on-demand iLO firmware update when automatic iLO firmware updates are disabled.
The on-demand iLO firmware update job installs iLO versions required by Compute Ops Management.
In some cases, the iLO version installed during the on-demand update process might not be the latest iLO version available in the
Hewlett Packard Enterprise Support Center.
**Note**
Server iLO firmware update is not supported on HPE Edgeline e920 server blades.


| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 94caa4ef-9ff8-4805-9e97-18a09e673b66 | compute-ops-mgmt/server | -- |


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

This job does not require the `jobParams` property.

## Example

The following example shows a request payload for creating this job.

### Example 1

Update the iLO firmware component on a server.


```json
{
    "jobTemplate": "94caa4ef-9ff8-4805-9e97-18a09e673b66",
    "resourceType": "ccompute-ops-mgmt/server",
    "resourceId": "086856-F17+8899086856117487",
}
```