---
title: "Server Enable Maintenance Mode Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-enable-maintenance-mode.md"
scraped_at: "2026-06-07T05:46:03.247296+00:00Z"
---

# Server Enable Maintenance Mode Job

## Overview

This job enables maintenance mode on a server. Enable maintenance mode on a server to suspend automatic support case creation, ServiceNow incident creation, and email notifications during planned maintenance.

| Job Template ID | Resource Type | JobParams |
|  --- | --- | --- |
| 4eb92af1-1ce4-4cb0-8581-fb5a7dcdbf2b | compute-ops-mgmt/server | -- |


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

This job does not require any job parameters.

## Examples

Here is an example request payload for creating this job.

### Example


```json
{
  "jobTemplate": "4eb92af1-1ce4-4cb0-8581-fb5a7dcdbf2b",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "048157-C87+8899048157087839"
}
```