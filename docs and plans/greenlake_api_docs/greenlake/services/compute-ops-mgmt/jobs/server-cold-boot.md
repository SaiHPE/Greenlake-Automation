---
title: "Server Cold Boot Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-cold-boot.md"
scraped_at: "2026-06-07T05:46:03.174318+00:00Z"
---

# Server Cold Boot Job

## Overview

This job can be used to perform a cold boot on a server.

> **Cold Boot**: Immediately removes power from the server. Processors, memory, and I/O resources lose main power. The server
will restart after approximately 8 seconds. Using this option circumvents the graceful shutdown features of the operating
system.


| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| aacfb3e0-6575-4d4f-a711-1ee1ae768407 | compute-ops-mgmt/server | -- |


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

Cold boot a server.


```json
{
  "jobTemplate": "aacfb3e0-6575-4d4f-a711-1ee1ae768407",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "859654-H12+8899859654112827"
}
```