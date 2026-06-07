---
title: "TEMPLATE Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/template.md"
scraped_at: "2026-06-07T05:46:06.163407+00:00Z"
---

# TEMPLATE Job

## Overview

This job can be used to ...

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| ... | ... | ... |


> Job parameters marked with a `*` are required.


## Create Job

A job can be created by issuing a `POST` to the `/compute-ops-mgmt/v1beta3/jobs` endpoint with the correct payload for the job.

The following properties are used when creating a job:

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `jobTemplateUri` | string (uri) | A job-template URI with the durable Template ID of the job | Yes |
| `resourceUri` | string (uri) | A resource URI that the job will operate on | Yes |
| `data` | object | Any additional data required by the job | No |


If the job was created successfully, a `201 Created` response is returned. The response includes the job resource which has a
job `resourceUri` that you can use to track the progress of the job.

## Job Parameters

This table summarizes the supported properties in `jobParams`.

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `propertyOne` | ... | ... | Yes |


### Parameter properties

- `propertyOne`: This **required** property ...
  - Default: `""`


## Examples

Here are a couple of example request payloads for creating this job.

### Example 1


```json
{
  "jobTemplate": "Durable template ID",
  "resourceType": "The TYPE of the effected resource",
  "resourceId": "The ID of the effected resource",
  "jobParams": {
    "propertyOne": "hjk-123"
  }
}
```

### Example 2


```json
{
  "jobTemplate": "Durable template ID",
  "resourceType": "The TYPE of the effected resource",
  "resourceId": "The ID of the effected resource"
}
```