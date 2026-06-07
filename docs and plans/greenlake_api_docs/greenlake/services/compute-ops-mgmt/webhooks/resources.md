---
title: "Available Resources"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/webhooks/resources.md"
scraped_at: "2026-06-07T05:46:08.014293+00:00Z"
---

# Available Resources

## Overview

There are various event resources that webhooks can be configured to subscribe to. For a given API, there is a set of properties that can be used to trigger an event payload to be sent to the webhook endpoint. More information about these properties can be found in the related API documentation which is linked in the [Resource Types](#resource-types) table.

### Event Types

Events fall into one of three categories: `Created`, `Deleted`, or `Updated`. If a webhook filter matches a resource being `Created` or `Deleted`, the event payload will be passed to the webhook endpoint. If the resource is `Updated` and the filter matches, the event payload is sent only if the updated property is supported for the resource type. For more information, see the Monitorable Properties in the [Resource Types](#resource-types) table.

One exception to this is the job resource. Any job events that match the filter and are `Deleted` will not send an event payload to the webhook endpoint. This is due to an effort to avoid sending data that is not useful.

## Resource Types

| Resource Type | API Documentation | Monitorable Properties |
|  --- | --- | --- |
| compute-ops/server | [Get v1 server by ID](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1_server_by_id/) | `hardware`, `state`, `firmwareInventory`, `softwareInventory`, `lastFirmwareUpdate`, `tags`, `autoIloFwUpdate` |
| compute-ops/alert | [Get v1 server alerts](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1_server_alerts/) | N/A - no specific properties can be monitored. Will only send `Created` and `Deleted` events |
| compute-ops/group | [Get v1beta2 group by ID](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta2_group_by_id/) | `name`, `autoFwUpdateOnAdd`, `groupComplianceStatus`, `serverSettingsUris`, `devices`, `serverPolicies`, `autoAddServerTags` |
| compute-ops/server-setting | [Get v1beta1 server settings by ID](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta1_server_settings_by_id/) | `name`, `settings` |
| compute-ops/job | [Get v1beta3 job by ID](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta3_job_by_id/) | `state` |
| compute-ops/group/compliance | [Get v1beta2 compliance by compliance ID](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta2_compliance_by_compliance_id/#!c=200&path=id&t=response) | `complianceStatus` |
| compute-ops/firmware-bundle | [Get v1beta2 firmware bundle by id](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/openapi/compute-ops-mgmt-latest/operation/get_v1beta2_firmware_bundle_by_id/) | `advisories`, `isActive` |


## Event Arrival

When a webhook is registered, events will arrive for your resource subscriptions. Events that occurred before the webhook was registered are not included. You will receive only the events that occurred after the webhook was registered.