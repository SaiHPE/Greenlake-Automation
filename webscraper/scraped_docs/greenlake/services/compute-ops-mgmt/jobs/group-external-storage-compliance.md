---
title: "Group External Storage Compliance Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-external-storage-compliance.md"
scraped_at: "2026-06-07T05:46:01.359673+00:00Z"
---

# Group External Storage Compliance Job

## Overview

This job initiates an external storage compliance check on all servers in a group.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 7177aa6a-e8f8-4e9b-ae31-e01dafcc81df | compute-ops-mgmt/group | -- |


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

Check external storage compliance of all servers in a group.


```json
{
  "jobTemplate": "7177aa6a-e8f8-4e9b-ae31-e01dafcc81df",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "8a3a2a46-0102-48e2-bdd9-a29ee6909860"
}
```