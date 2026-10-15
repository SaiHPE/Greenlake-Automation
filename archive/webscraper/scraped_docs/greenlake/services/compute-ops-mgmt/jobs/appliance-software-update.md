---
title: "Appliance Software Update Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/appliance-software-update.md"
scraped_at: "2026-06-07T06:13:22.406870+00:00Z"
---

# Appliance Software Update Job

## Overview

Use this job to update the appliance software.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 1c4ac4be-8eeb-49f2-a86a-fd8c9182616c | compute-ops-mgmt/oneview-appliance | See [Job Parameters](#job-parameters) section |


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

This table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `applianceFirmwareId` | string (uuid) | Appliance Firmware UUID | Yes |


### Parameter properties

- `applianceFirmwareId`: This **required** property is the appliance firmware UUID to use for the firmware update.
  - To obtain the firmware bundle UUID, use `GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles` and look at the `id` property in the response.


## Example

The following example shows a request payload for creating this job.

### Example 1

Use the specified appliance software to update an appliance.


```json
{
  "jobTemplate": "1c4ac4be-8eeb-49f2-a86a-fd8c9182616c",
  "resourceType": "compute-ops-mgmt/oneview-appliance",
  "resourceId": "oneview+76986158-9e7a-4511-86c6-24832924f0e4",
  "jobParams": {
    "applianceFirmwareId": "70366cf929f0db1ad0b06bb23f44b466"
  }
}
```