---
title: "Server Power On Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-power-on.md"
scraped_at: "2026-06-07T05:46:05.203720+00:00Z"
---

# Server Power On Job

## Overview

This job can be used to power on a server.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 0cbb2377-1834-488d-840c-d5bf788c34fb | compute-ops-mgmt/server | -- |


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

Power on a server.


```json
{
  "jobTemplate": "0cbb2377-1834-488d-840c-d5bf788c34fb",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "063573-L08+8899063573208133"
}
```