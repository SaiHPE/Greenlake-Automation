---
title: "HPE Compute Ops Management Glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/glossary.md"
scraped_at: "2026-06-07T05:46:06.153345+00:00Z"
---

# HPE Compute Ops Management Glossary

## Acronyms

### AHS

The HPE Active Health System (AHS) monitors and records changes in the server hardware and system configuration on HPE servers.
This log acts as black box for a server and helps in diagnosing problems and delivering rapid resolution when the system failure occurs.

### iLO

Integrated Lights-Out (iLO) is an HPE remote management capability available in all HPE servers that can connect to Compute
Ops Management. The iLO processor is the compute management device that makes configuration and firmware updates possible.

### SPP

The Service Pack For ProLiant (SPP) is a comprehensive systems software and firmware update solution released by Hewlett Packard Enterprise.

## Terms

### Actions

The tasks that can be applied to a server. The list of possible actions includes:

- Power On
- Power Off
- Reset
- Cold Boot
- Manage server group membership
- Update Firmware
- Dismiss stalled state


### Activity

An action taken on a server or a server status change. The following list includes examples of activities that are reported in the Compute Ops Management activity history.

- Servers connected
- Servers disconnected
- Server added or removed from a group
- Server name was updated


### AHS log Analysis task

The AHS log analyzer allows you to upload an AHS file from an HPE Gen10 or later server. Compute Ops Management parses the file and provides a CSV or JSON file that you can use to review the server information from AHS log.

### Async-Operations

Async-operations are used to track the progress of an action that was initiated and is proceeding in the background.

### Baseline

A set of firmware updates that you can apply to managed servers. Configuring a server group firmware
baseline is an optional feature that allows you to apply the same firmware baseline to a group of servers in one step.

### External Services

Integration of external services like ServiceNow with Compute Ops Management for managing service incidents.

### Firmware

A group of software components that provides the low-level control for server hardware.

### Firmware bundle

A firmware bundle (SPP) is a tested update package of firmware, drivers, and utilities. Firmware bundles allow
you to update firmware on managed servers.

### Groups

Groups enable you to organize your devices into custom-defined sets for easier monitoring and manageability. Starting with
the v1beta3 version of groups, a group has a Type: `Server`, `OneView VM appliance`, or `OneView Synergy appliance`. The
choice impacts the type of devices that can be added to the group, and the types of settings that can be applied to the group.

### Health

- **Warning**: A condition exists that requires attention.
- **OK**: The server is healthy.
- **Critical**: A condition exists that requires immediate attention.
- **Unknown**: Health status is unavailable.


### Job

A multi-step task that is managed by Compute Ops Management.

### Job Template

A predefined job to accomplish a Compute Ops Management task.

### Metrics Configurations

A configuration for opting whether or not COM can automatically collect data from all servers.

### Schedule

The Compute Ops Management application provides a scheduling service. A schedule is defined as an REST API call to a service at a defined future time.

### Server

A supported HPE compute device. For the list of supported servers, see [HPE Compute Ops Management Getting Started Guide](http://www.hpe.com/info/com-docs).

### Server Settings

A server setting is a collection of parameters that you can apply to one or more server groups. When you select
a server setting during the server group creation or editing process, you can apply related policies to the group.

### Settings

A setting is a collection of parameters that you can apply to one or more groups. When you select a setting during
the group creation or editing process, you can apply related policies to the group.

### State

The server state helps you determine if your servers are configured and available to manage.

- Not connected
- Connected
- Reconnecting
- Not activated
- Subscription required
- Subscription expired


### Status

Refers to the status of a server. Possible status conditions are:

- **Critical**: Server health is critical. For example, a monitored subsystem failed. Lack of redundancy in any subsystem at
startup will not degrade the server health status. For information about this status, view the Health section on the server
details page or check the status in iLO.
- **Warning**: Server health is degraded. For example, a monitored component is not redundant. For information about this
status, view the Health section on the server details page or check the status in iLO.
- **Ok**: Server health is ok.
- **Unknown**: Compute Ops Management cannot determine the server status.
- **Disabled**: There is a subscription or server connection issue, or the server is not activated in iLO.


### Subscription

An active subscription is required to manage servers with the Compute Ops Management application.

### Tag

A keyword assigned to a piece of information that is used to describe a Compute Ops Management resource.

### Webhooks

A webhook is an HTTP-based callback function that allows lightweight, event-driven communication between two APIs.