---
title: "Settings Update OneView Server Template"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/setting-update-oneview-server-template.md"
scraped_at: "2026-06-07T05:46:05.233536+00:00Z"
---

# Settings Update OneView Server Template

## Overview

This job updates settings of type 'OVE_SERVER_TEMPLATES_VM' and 'OVE_SERVER_TEMPLATES_SYNERGY' by dynamically fetching data from appliances for the specified OneView server templates.

| Job Template ID | Resource Type | Job Parameters |
|  --- | --- | --- |
| abfda355-6e58-4c00-be0a-af35dbd70398 | compute-ops-mgmt/setting | `templatesData*` |


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
| `templatesData` | list | Oneview Server template URIs and appliance ID | Yes |


### Parameter properties

- `templatesData`: This **required** field lists the appliance IDs and server templates to be fetched and updated.
  - `templates`: A list of URIs for OneView server templates.
  - `applianceId`: The ID of the appliance that these templates belong to.


## Examples

Here are some example request payloads for creating this job.

### Example 1

For a OneView server template setting, fetch OneView server templates from a single source appliance.


```json
{
  "jobTemplate": "abfda355-6e58-4c00-be0a-af35dbd70398",
  "resourceType": "compute-ops-mgmt/setting",
  "resourceId": "66ca162d-5ca0-4c39-909a-78ba30196c4f",
  "jobParams": {
    "templatesData": [
      {
        "applianceId": "df24164d-fb0f-445a-bcdb-f845f40019f7",
        "templates": [
          {
            "uri": "/rest/server-profile-templates/5350a573-4aeb-4af4-b967-2f4e44ba0452"
          },
          {
            "uri": "/rest/server-profile-templates/526a38f5-99c0-42ae-8dca-8f2392a59bd8"
          }
        ]
      }
    ]
  }
}
```

### Example 2

For a OneView server template setting, fetch OneView server templates from multiple appliances.


```json
{
  "jobTemplate": "abfda355-6e58-4c00-be0a-af35dbd70398",
  "resourceType": "compute-ops-mgmt/setting",
  "resourceId": "66ca162d-5ca0-4c39-909a-78ba30196c4f",
  "jobParams": {
    "templatesData": [
      {
        "applianceId": "df24164d-fb0f-445a-bcdb-f845f40019f7",
        "templates": [
          {
            "uri": "/rest/server-profile-templates/5350a573-4aeb-4af4-b967-2f4e44ba0452"
          },
          {
            "uri": "/rest/server-profile-templates/526a38f5-99c0-42ae-8dca-8f2392a59bd8"
          }
        ]
      },
      {
        "applianceId": "d42c2b9b-b366-4e40-96a2-95e1138cf968",
        "templates": [
          {
            "uri": "/rest/server-profile-templates/a56e80bc-6ee4-4414-82e7-36dc7f79a62e"
          }
        ]
      }
    ]
  }
}
```