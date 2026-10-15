---
title: "API and Event Catalog | HPE GreenLake Developer Portal"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services.md"
scraped_at: "2026-06-07T06:13:19.782042+00:00Z"
---

# HPE GreenLake cloud APIs and events catalog

HPE GreenLake cloud is a secure, cloud-based platform that allows you to view and control your hybrid cloud estate. HPE GreenLake provides an extensive catalog of APIs and events. By providing both API and event functionality, the platform offers a comprehensive developer toolkit that meets the diverse needs and use cases of platform administrators.

[APIs](/docs/greenlake/services#api-catalog) allow you to request and retrieve data on demand, initiating and executing operations programmatically, granting access to the functionalities available through the platform UI. You can manage devices and subscriptions through these APIs, view audit logs, and perform various other tasks.

HPE GreenLake APIs:

- Conform to the OpenAPI 3.0 specification.
- Use a single endpoint.
- Use a single OAuth token to access all APIs.
- Are built to be secure and highly available.
- Are RESTful for flexible implementation.


With [events](/docs/greenlake/services#event-catalog), you can receive close to real-time notifications when specific actions or changes happen within your HPE GreenLake infrastructure.

Getting help from the HPE Developer Community
The HPE Developer Community provides resources like community events, blogs, and hands-on labs to help you get started and make the most out of HPE GreenLake APIs.

- [Community Overview](/docs/greenlake/community) gives quick access to all sections of the HPE Developer Community.
- [Community Resources](/docs/greenlake/community/resources) curates getting started events, blogs, and labs for HPE GreenLake cloud API catalog.


## API catalog

Browse the API catalog.

| Service | Description |
|  --- | --- |
| [API Client Credentials](/docs/greenlake/services/credentials/public) | HPE GreenLake for API Client Credentials  allows programmatic access to manage workspace credentials. You can create, delete, update, and check workspace credentials. |
| [Audit Logs](/docs/greenlake/services/audit-logs/public) | The HPE GreenLake for Audit Log service offers a collection of RESTful APIs for publishing audit logs, managing configurations, and retrieving application-specific and overall platform logs. |
| [Authorization](/docs/greenlake/services/authorization/public) | The HPE GreenLake for Authorization service enables you to programmatically manage access control within your HPE GreenLake environment. |
| [Backup and Recovery](/docs/greenlake/services/backup-recovery/public) | HPE GreenLake for Backup and Recovery is a data protection service that is part of the Data Services Cloud Console application on the HPE GreenLake cloud. |
| [Block Storage](/docs/greenlake/services/block-storage/public) | HPE GreenLake for Block Storage provides RESTful APIs to manage the lifecycle of Block Storage resources. |
| [Compute Ops](/docs/greenlake/services/compute-ops-mgmt/public) | HPE Compute Ops Management offers a RESTful API to customers who want to manage their devices programmatically or through a command-line. The API enables customers to initiate any operation or task that is available through the UI web interface. |
| [Consumption Analytics](/docs/greenlake/services/consumption-analytics/public) | The HPE GreenLake Consumption Analytics API provides read-only access to reporting data for cloud consumption. It enables authenticated clients to retrieve available report definitions, view their structure, and download report results as CSV files. |
| [Data Services](/docs/greenlake/services/data-services/public) | HPE GreenLake for Data Services offers a RESTful API for capabilities common to the following APIs: Backup Recovery, Public Cloud Business Edition and Virtualization. |
| [Devices](/docs/greenlake/services/device-management/public) | With the HPE GreenLake for Device Management API, you can view, manage, and onboard devices in your workspace. The API allows you to initiate any operation or task that is available through the HPE GreenLake UI. |
| [Flex](/docs/greenlake/services/flex/public) | With the HPE Flex Solutions API you can view and manage Flex orders and devices in your workspace. |
| [Webhooks and events](/docs/greenlake/services/event/public) | The HPE GreenLake for Webhooks API allows you to programmatically register a webhook, update a webhook, verify a webhook, and subscribe to events. The webhook and events capability facilitates integrating automation into your workflows. |
| [Locations](/docs/greenlake/services/location-management/public) | HPE GreenLake for Locations is a collection of RESTful APIs for creating and managing location services. The APIs initiate any Locations service operation or task available through the HPE GreenLake UI. HPE GreenLake uses the collected information to automate service delivery and to create automated support cases. |
| [Object Storage](/docs/greenlake/services/object-storage/public) | HPE GreenLake for Object Storage provides RESTful APIs to manage the lifecycle of Object Storage resources. |
| [Private Cloud Business Edition](/docs/greenlake/services/private-cloud-business/public) | HPE GreenLake for Private Cloud Business Edition provides global lifecycle management of infrastructure and virtualization resources. |
| [Reporting](/docs/greenlake/services/reporting/public) | HPE GreenLake for Reporting provides access to reports on your HPE GreenLake workspace in an efficient and programmatic way. |
| [SCIM](/docs/greenlake/services/scim) | SCIM User and Group Management APIs compliant with the SCIM 2.0 specification. |
| [Service Catalog](/docs/greenlake/services/service-catalog/public) | The HPE GreenLake for Service Catalog service offers a collection of RESTful APIs to fetch, provision service managers and to delete a service manager provisioned in a workspace. |
| [Storage Fleet](/docs/greenlake/services/storage-fleet/public) | HPE GreenLake for Storage Fleet provides RESTful APIs to manage the Storage Fleet resources. |
| [Subscriptions](/docs/greenlake/services/subscription-management/public) | With the HPE GreenLake for Subscriptions APIs, you can onboard and manage subscriptions in your workspace. |
| [Sustainability Insight Center](/docs/greenlake/services/sustainability/public) | HPE Sustainability Insight Center APIs allow developers to access HPE Sustainability Insight Center features and data programmatically. With these APIs, you can get the total energy consumption across your IT infrastructure, information about greenhouse gas emissions, and costs associated with your energy consumption. |
| [Tags](/docs/greenlake/services/tags/public) | With the HPE GreenLake for Tags APIs, you can view and filter all tags and all supported tagged resources in a workspace. |
| [User Management](/docs/greenlake/services/identity/public) | HPE GreenLake for User Management API allows programmatic methods to invite or delete users and to check user information. |
| [Virtualization](/docs/greenlake/services/virtualization/public) | The HPE GreenLake for Virtualization API provides management of virtual machines and other virtual resources in public clouds and on-premises systems. |
| [Wellness](/docs/greenlake/services/wellness/public) | The HPE GreenLake for Wellness APIs allow programmatic access to view and manage wellness events and insights. The APIs facilitate integrating wellness events into existing workflows. |
| [Workspaces](/docs/greenlake/services/workspace/public) | The HPE GreenLake for Workspace Management APIs allow programmatic access to the records of workspaces and workspace-user relationships. |


## Event catalog

Browse the events catalog. To learn more, see the [webhook and events documentation](/docs/greenlake/services/event/public).

| API group | Event description | Event type |
|  --- | --- | --- |
| [Audit Logs](/docs/greenlake/services/audit-logs/public/catalog/audit-log-event-latest/audit-trail-event) | The **Audit Log Created** event notifies you when an audit log has been created. | `com.hpe.greenlake.audit-log.v1.logs.created` |
| [Subscriptions](/docs/greenlake/services/subscription-management/public/catalog/subscriptions-unified-events-glcp-v1/unifiedevents) | The **Expiring Subscriptions** event notifies you when a subscription is expiring in 1, 30, 60, and 90 days. | `com.hpe.greenlake.subscriptions.v1.expiring-subscriptions` |