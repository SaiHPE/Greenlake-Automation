---
title: "Server External Storage Details Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-external-storage-details.md"
scraped_at: "2026-06-07T05:46:03.247436+00:00Z"
---

# Server External Storage Details Job

## Overview

This job initiates the collection of external storage details for a server.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 9310319e-7b7f-41ba-8b24-8b34eed1ca62 | compute-ops-mgmt/server | -- |


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

Here is an example request payload for creating this job.

### Example 1

Collect external storage details for a server.


```json
{
  "jobTemplate": "9310319e-7b7f-41ba-8b24-8b34eed1ca62",
  "resourceType": "ccompute-ops-mgmt/server",
  "resourceId": "814199-O78+8899814199378993"
}
```