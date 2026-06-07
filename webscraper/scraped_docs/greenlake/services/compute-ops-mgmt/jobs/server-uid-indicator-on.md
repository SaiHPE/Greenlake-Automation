---
title: "Server UID Indicator On Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-uid-indicator-on.md"
scraped_at: "2026-06-07T06:13:25.280054+00:00Z"
---

# Server UID Indicator On Job

## Overview

This job turns on the UID (Unit Identification) indicator light on a server. The UID indicator is typically a blue LED light on the front and/or back of the server that helps physically identify a specific server in a data center rack.

| Job Template ID | Resource Type | JobParams |
|  --- | --- | --- |
| a46b210a-b0c7-4223-ab43-c4c1e77e680c | compute-ops-mgmt/server | -- |


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
  "jobTemplate": "a46b210a-b0c7-4223-ab43-c4c1e77e680c",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "871940-B21+8899059826806785"
}
```