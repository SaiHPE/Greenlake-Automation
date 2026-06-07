---
title: "vCenter Firmware Bundles Sync Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/vcenter-firmware-bundles-sync.md"
scraped_at: "2026-06-07T05:46:06.101462+00:00Z"
---

# vCenter Firmware Bundles Sync Job

## Overview

Use this job to synchronize firmware bundles from a VMware vCenter external service.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 0fe73adb-9d52-4f00-9540-6ec82f265d82 | compute-ops-mgmt/external-service | See [Job Parameters](#job-parameters) section |


> Job parameters marked with a `*` are required.


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

This job does not require any additional job parameters. The synchronization is performed based on the external service resource specified in the request.

## Example

The following example shows a request payload for creating this job.

### Example 1

Synchronize firmware bundles from a vCenter external service.


```json
{
  "jobTemplate": "0fe73adb-9d52-4f00-9540-6ec82f265d82",
  "resourceId": "6581a59f-c188-4dfc-bc35-7732f72f25bc",
  "resourceType": "compute-ops-mgmt/external-service"
}
```