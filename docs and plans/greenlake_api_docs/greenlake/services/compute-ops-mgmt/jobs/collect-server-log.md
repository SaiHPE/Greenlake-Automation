---
title: "Collect Server log Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/collect-server-log.md"
scraped_at: "2026-06-07T05:46:00.272619+00:00Z"
---

# Collect Server log Job

## Overview

This job provides the ability to collect and download the server log for servers managed by COM.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| 2d744494-22d4-4d61-8c65-647ccadeb6b6 | compute-ops-mgmt/server | `collect_ahs_log` |


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

The server log collection can be downloaded by executing GET on `/compute-ops-mgmt/v1/servers/{server_id}/download-logs` endpoint.

## Job Parameters

This table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Values | Required? |
|  --- | --- | --- | --- |
| `collect_ahs_log` | boolean | When enabled, Active Health System (AHS) Log will be downloaded as part of collect server log job | No |


### Parameter properties

- `collect_ahs_log`: When enabled, AHS log will be downloaded as part of collect server log job .
- Default : `false`


## Examples

Here are a couple of example request payloads for creating this job.

### Example 1

Collect server log which includes AHS collection.


```json
{
   "jobTemplate": "2d744494-22d4-4d61-8c65-647ccadeb6b6",
   "resourceType": "compute-ops-mgmt/server",
   "resourceId": "868703-B21+SGH744YPVP",
   "jobParams": {
      "collect_ahs_log": true
   }
}
```

### Example 2

Collect server log without AHS collection.


```json
{
   "jobTemplate": "2d744494-22d4-4d61-8c65-647ccadeb6b6",
   "resourceType": "compute-ops-mgmt/server",
   "resourceId": "868703-B21+SGH744YPVP",
}
```