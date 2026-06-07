---
title: "Server Power Off Job"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/jobs/server-power-off.md"
scraped_at: "2026-06-07T05:46:04.282301+00:00Z"
---

# Server Power Off Job

## Overview

This job can be used to power off a server in one of several ways.

> **Graceful Shutdown**: The same as pressing the physical power button. If the server
is powered off, a momentary press will turn on the server power.
Some operating systems might be configured to initiate a graceful shutdown after a momentary press, or to ignore this event.
Hewlett Packard Enterprise recommends using system commands to complete a graceful operating system shutdown before you
attempt to shut down by using the virtual power button.
**Force Off**: The same as pressing the physical power button for 5 seconds and then
releasing it.
The server is powered off as a result of this operation. Using this option might
circumvent the graceful shutdown features of the operating system.
This option provides the ACPI functionality that some operating systems implement.
These operating systems behave differently depending on a short press or long press.


| Job Template ID | Resource Type | JobParams |
|  --- | --- | --- |
| d0c13b58-748c-461f-9a61-c0c5c71f1bb4 | compute-ops-mgmt/server | `operationType` |


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

This table summarizes the supported properties in `JobParams`.

| Property | JSON Type | Description | Required? |
|  --- | --- | --- | --- |
| `operationType` | string (enum) | Type of power off operation | No |


### Parameter properties

- `operationType`: This property is an enumeration with two possible values:
  - `ForceOff`: Force the server to power off without waiting for a graceful shutdown of the OS.
  - `GracefulShutdown`: Request a graceful shutdown of the OS before powering off the server. If the OS does not shut down,
then this job will power off the server using the force off option.
  - Default: `ForceOff`


## Examples

Here are a couple of example request payloads for creating this job.

### Example 1

Power off a server using the graceful shutdown option.


```json
{
  "jobTemplate": "d0c13b58-748c-461f-9a61-c0c5c71f1bb4",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "814199-O78+8899814199378993",
  "jobParams": {
    "operationType": "GracefulShutdown"
  }
}
```

### Example 2

Power off a server using the default option (force off).


```json
{
  "jobTemplate": "d0c13b58-748c-461f-9a61-c0c5c71f1bb4",
  "resourceType": "compute-ops-mgmt/server",
  "resourceId": "059826-706+8899059826806785"
}
```