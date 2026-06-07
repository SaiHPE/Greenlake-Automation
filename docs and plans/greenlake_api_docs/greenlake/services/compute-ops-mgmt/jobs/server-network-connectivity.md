---
title: "Collect Server Network Connectivity"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-network-connectivity.md"
scraped_at: "2026-06-07T06:13:24.602671+00:00Z"
---

# Collect Server Network Connectivity

## Overview

This job initiates a server network connectivity collection on directly managed servers.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| b21ca9e2-8a1b-11ee-b9d1-0242ac120002 | compute-ops-mgmt/server | -- |


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

Collect server network connectivity of a server.


```json
{
  "jobTemplate": "b21ca9e2-8a1b-11ee-b9d1-0242ac120002",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "P06760-B21+2M212504P8"
}
```