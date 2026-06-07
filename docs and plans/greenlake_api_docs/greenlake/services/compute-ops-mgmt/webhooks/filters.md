---
title: "Webhook Filters"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/webhooks/filters.md"
scraped_at: "2026-06-07T06:13:25.986911+00:00Z"
---

# Webhook Filters

## Overview

Filters are necessary when registering for webhooks since they will control what event payloads are sent to the webhook's endpoint using the `eventFilter` property. Webhooks use an opt-in style, where only events matching the configured `eventFilter` will be sent to the destination. If there is only interest in events related to groups and servers, the filter would need to specify just those two resource types.

Each resource can be filtered. For more information, see [Available Resources](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources).

Beyond opting in, filters can be used to limit what kinds of events are received from that resource. For example, if there is only interest in `Delete` operations related to groups, a filter can be created to only receive those events.

## Filtering Rules

- A given webhook must have one non-empty filter.
- Use ODATA style filters. This is consistent with the [HPE GreenLake specification](https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/guide/#filtering).
- See the following table for different filtering operations.


| Property | Description | Example Values | Example *eventFilter* | Result |
|  --- | --- | --- | --- | --- |
| `type` | Allows matching on [resource types](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources#resource-types) | `compute-ops/job`, `compute-ops/server` | `type eq 'compute-ops/job'` | Match all events related to jobs |
| `operation` | Allows matching on different operations | `Created`, `Deleted`, `Updated` | `type eq 'compute-ops/alert' and operation eq 'Created` | Match all events related to created alerts |
| `changed` | Allows matching on [monitorable properties](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources#resource-types) if the value has changed | `changed/name`, `changed/state` | `type eq 'compute-ops/group' and changed/name eq True` | Match any events related to groups whose `name` property changed |
| `new` | Allows matching on [monitorable properties](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources#resource-types) of the current state of the resource | `new/complianceStatus`, `new/isActive` | `type eq 'compute-ops/group' and new/groupComplianceStatus ne 'Compliant'` | Match any events related to groups whose `groupComplianceStatus` is not currently `Compliant` |
| `old` | Allows matching on [monitorable properties](/docs/greenlake/services/compute-ops-mgmt/webhooks/resources#resource-types) of the previous state of the resource | `old/devices`, `old/settings` | `type eq 'compute-ops/group' and old/name eq 'Group Name'` | Match any events related to a group whose previous `name` was "Group Name" until the group's name is changed again |
| `name` | Alias for `new/name` |  | `type eq 'compute-ops/group' and name ne 'New Group'` | Match any events related to groups whose current `name` is not "New Group" |


### `new` vs `old`

In most cases, `new` will accomplish the goals of a filter that matches a specific event property. There is some nuance between how `new` and `old` work, but they match similar sets of events. For example, consider if a group is created with the `name` "Group1" (event 0) and then is updated to be named "Group2" after *n* events. The filter `type eq 'compute-ops/group' and new/name eq 'Group1'` will match events 0 through *n*-1, whereas if we change the filter to use `old/name` it will match events 1 through *n*.

## Filter examples

| Filter | Description |
|  --- | --- |
| `type eq 'compute-ops/job'` | Match all `compute-ops/job` events |
| `type eq 'compute-ops/group' and operation eq 'Deleted'` | Match only `compute-ops/group` deletion events |
| `type eq 'compute-ops/groups' and contains(name, 'exemplar')` | Match all `compute-ops/group` events which have a `name` containing "exemplar" |
| `type eq 'compute-ops/firmware-bundle' and new/isActive eq True` | Match all firmware bundle events that have `isActive` currently set to `True` |
| `type eq 'compute-ops/server' and old/hardware/health/summary eq 'OK' and changed/hardware/health/summary eq True` | Match any server events whose health summary transitions out of an `OK` state |
| `type eq 'compute-ops/server' or type eq 'compute-ops/job' or type eq 'compute-ops/alert' or type eq 'compute-ops/group' or type eq 'compute-ops/server-setting' or type eq 'compute-ops/group/compliance' or type eq 'compute-ops/firmware-bundle'` | Match every event |