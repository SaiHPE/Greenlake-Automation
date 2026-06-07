---
title: "Refresh OneView appliance settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/refresh-oneview-appliance-settings.md"
scraped_at: "2026-06-07T06:13:23.881059+00:00Z"
---

# Refresh OneView appliance settings

## Overview

This job retrieves appliance settings data from a specified appliance to refresh the OneView appliance settings cache in Compute Ops Management.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| fc16aa48-c73c-4463-9112-e061383ebfa9 | compute-ops-mgmt/oneview-appliance | -- |


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

Refresh the OneView appliance settings cache for the specified appliance.


```json
{
 "jobTemplate": "fc16aa48-c73c-4463-9112-e061383ebfa9",
 "resourceType": "compute-ops-mgmt/oneview-appliance",
 "resourceId": "9ff60173-a32d-412e-bb52-3b49c7f878e1"
}
```