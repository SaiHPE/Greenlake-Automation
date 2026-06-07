---
title: "Server Restart Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-restart.md"
scraped_at: "2026-06-07T06:13:25.187534+00:00Z"
---

# Server Restart Job

## Overview

This job can be used to restart a server.

> **Restart**: Forces the server to warm-boot: CPUs and I/O resources are reset. Using
this option circumvents the graceful shutdown features of the operating system.


| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 30110551-cad6-4069-95b8-dbce9bbd8525 | compute-ops-mgmt/server | -- |


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

This job doesn't require the `jobParams` property.

## Example

Here's an example request payload for creating this job.

### Example 1

Restart a server.


```json
{
  "jobTemplate": "30110551-cad6-4069-95b8-dbce9bbd8525",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "855308-N51+8899855308351678"
}
```