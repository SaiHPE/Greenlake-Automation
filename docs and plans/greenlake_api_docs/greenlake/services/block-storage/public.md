---
title: "HPE GreenLake for Block Storage"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/block-storage/public.md"
scraped_at: "2026-06-07T06:13:21.762801+00:00Z"
---

# HPE GreenLake for Block Storage

This page provides an introduction and quick start guide for the Block Storage API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake for Block Storage REST APIs let you programmatically create, manage, and monitor block storage resources to support integration and automation.
Block Storage is a service in Data Services Cloud Console that handles volume lifecycle management, native replication, and snapshot-based data protection.
Using these APIs, you can provision, protect, and operate volumes and volume sets to enable automated workflows for provisioning, replication, snapshots, and monitoring of block storage resources.

### Features

- Create, list, update, and delete volumes
- Create, manage, and delete snapshots and snapshot schedules
- Create, manage, and delete volume sets
- Attach and detach volumes to/from hosts and host groups
- Manage initiators and initiator groups
- Configure and manage QoS policies
- Enable/disable volume encryption and integrate with key management
- Perform space reclamation and thin provisioning management
- Monitor capacity, health, and performance for volumes and pools
- Manage replication relationships and protection policies


### Related documentation

- [HPE GreenLake for Block Storage Articles](https://www.hpe.com/support/GLBlockStorageArticles)
- [Block Storage Release Notes](https://www.hpe.com/support/BlockStorageReleaseNotes)


## Developer guide

HPE GreenLake for Block Storage provides RESTful APIs to programmatically create, manage, and monitor block storage resources, enabling seamless integration and automation.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API requests to. Block Storage has unique endpoints in specific regions. Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU West: [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


#### Authentication

The Block Storage API uses an access token for authentication. Instructions
for obtaining an access token can be found on the [Authentication](/docs/greenlake/guides/public/authentication/authentication)
page.

The HTTP Authorization request header is used to provide the access token in
all API requests as a Bearer token.

- `Authorization:Bearer <access token>`


#### Authorization

All API requests are authorized using permissions. The user owning the access
token must have the required permissions assigned for the resources being accessed
in order to be authorized. The required permissions are documented in the
following guide pages.

#### Required permissions

To use the HPE GreenLake Block Storage API, you need appropriate permissions based on your role:

- `block-storage.host-initiator-group.read` for all `GET` and `LIST` requests on host initiator group resources
- `block-storage.host-initiator-group.create` for all `POST` requests on host initiator group resources
- `block-storage.host-initiator-group.update` for all `PUT` requests on host initiator group resources
- `block-storage.host-initiator-group.delete` for all `DELETE` requests on host initiator group resources
- `block-storage.host-initiator.read` for all `GET` and `LIST` requests on host initiator resources
- `block-storage.host-initiator.create` for all `POST` requests on host initiator resources
- `block-storage.host-initiator.update` for all `PUT` requests on host initiator resources
- `block-storage.host-initiator.delete` for all `DELETE` requests on host initiator resources
- `block-storage.performance-template.read` for all `GET` and `LIST` requests on performance template resources
- `block-storage.performance-template.create` for all `POST` requests on performance template resources
- `block-storage.performance-template.update` for all `PUT` requests on performance template resources
- `block-storage.performance-template.delete` for all `DELETE` requests on performance template resources
- `block-storage.protection-template.read` for all `GET` and `LIST` requests on protection template resources
- `block-storage.protection-template.create` for all `POST` requests on protection template resources
- `block-storage.protection-template.update` for all `PUT` requests on protection template resources
- `block-storage.protection-template.delete` for all `DELETE` requests on protection template resources
- `block-storage.bucket.read` for all `GET` and `LIST` requests on bucket resources


For more information about roles and permissions, see the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html).

### Making it all work

#### General guidelines

- For asynchronous operations that return HTTP status 201 or 202, use the Location header in the API response to track progress.
- Replace the base URL in examples with the endpoint for your region.


#### Create a new volume

Create a volume on an HPE Alletra Storage MP B10000 device.


```bash
POST https://us-west.api.greenlake.hpe.com/block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes
```

Payload:


```json
{
  "comments": "test",
  "count": 2,
  "dataReduction": true,
  "name": "<resource_name>",
  "ransomware": true,
  "sizeMib": 16384,
  "snapshotAllocWarning": 5,
  "userAllocWarning": 5,
  "userCpg": "SSD_r6"
}
```

The endpoint [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com) is the endpoint for the US West application. If you are using HPE GreenLake for Block Storage in a different region, replace it with the endpoint for the corresponding region.

#### Listing all volumes

Retrieve the list of volumes for the specified HPE Alletra Storage MP B10000 device. Replace {systemId} with your system identifier.


```bash
GET https://us-west.api.greenlake.hpe.com/block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes
```

#### GET with filtering, pagination, and field selection

Use query parameters to filter results, paginate large datasets, and return only the fields you need.
Parameter names may vary by endpoint, so refer to the API reference for the specific resource.


```bash
GET https://us-west.api.greenlake.hpe.com/block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volumes?name=prod-vol&limit=50&offset=0&select=id,name,sizeMib
```

Query parameters:

- `name=prod-vol`—Filters results to a specific name (example filter).
- `limit=50`—Limits the number of returned records (pagination control).
- `offset=0`—Skips a number of records before returning results (pagination control).
- `select=id,name,sizeMib`—Limits the response fields to reduce payload size.


#### Update a volume's properties

Update the properties of a volume on an HPE Alletra Storage MP B10000 device. Replace {systemId} and {volumeId} with actual IDs.


```bash
PUT https://us-west.api.greenlake.hpe.com/block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volume/{volumeId}
```

Payload:


```json
{
  "dataReduction": true,
  "name": "volume_Name",
  "ransomware": true,
  "sizeMib": 1,
  "snapshotAllocWarning": 1,
  "userAllocWarning": 1,
  "userCpgName": "cpg_1"
}
```

#### Delete a volume

Delete the specified volume on the given HPE Alletra Storage MP B10000 device. Replace {systemId} and {volumeId} with actual IDs.


```bash
DELETE https://us-west.api.greenlake.hpe.com/block-storage/v1alpha1/devtype4-storage-systems/{systemId}/volume/{volumeId}
```