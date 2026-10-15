---
title: "Group Appliance Update Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/group-appliance-update.md"
scraped_at: "2026-06-07T06:13:22.513255+00:00Z"
---

# Group Appliance Update Job

## Overview

This job updates specified OneView appliances in a group. The group must have a configured setting with category 'OVE_SOFTWARE_SYNERGY' or 'OVE_SOFTWARE_VM'.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| f69f553a-5004-4a08-9283-5b60abd9eb4a | compute-ops-mgmt/group | `targetApplianceIds*` |


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

The following table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `targetApplianceIds` | array | List of appliance IDs | Yes |


### Parameter properties

- `targetApplianceIds`: This **required** field is a list of appliance IDs to include in the group update. If specified, this non-empty list of appliance IDs limits the scope of the operation to the specified appliance group members. If unspecified, an exception will be raised.


## Example

Here is an example request payload for creating this job.

### Example 1

Update OneView appliances in a group. The 'resourceUri' identifies the group and 'targetApplianceIds' specifies IDs of the appliances to be updated.


```json
{
  "jobTemplate": "f69f553a-5004-4a08-9283-5b60abd9eb4a",
  "resourceType": "compute-ops-mgmt/group",
  "resourceId": "213e7c32-3046-4419-95dc-cc816adb95e9",
  "jobParams": {
    "targetApplianceIds": [
      "oneview+2ec6bdbf-59e2-4d1c-b59e-8147927321fd",
      "oneview+5819ccbc-8be6-4c99-a497-cec22c7a6ca2"
    ]
  }
}
```