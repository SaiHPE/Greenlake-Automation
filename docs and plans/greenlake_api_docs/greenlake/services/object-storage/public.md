---
title: "HPE GreenLake for Object Storage"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public.md"
scraped_at: "2026-06-07T05:46:12.835441+00:00Z"
---

# HPE GreenLake for Object Storage

This page provides an introduction and quick start guide for the Object Storage API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

HPE GreenLake for Object Storage provides RESTful APIs to programmatically manage buckets, users, groups, and access policies, as well as lifecycle rules, access control, and monitoring, making integration and automation simple.

### Features

- Create, list, update and delete object storage buckets
- Configure bucket properties including versioning, object locking, and lifecycle policies
- Report bucket capacity and performance
- Manage bucket metadata
- Manage bucket access control lists (ACLs)
- Manage users and user groups


## Developer guide

HPE GreenLake for Object Storage offers RESTful APIs for Object Storage, enabling management and configuration of buckets, users, and group and access policies.

### Prerequisites

#### Endpoints

Endpoints are the host URLs that you submit your API requests to. Object Storage has unique endpoints in specific regions. Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU West: [https://eu-west.api.greenlake.hpe.com](https://eu-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


#### Authentication

The Object Storage API uses an access token for authentication. Instructions
for obtaining an access token can be found on the [Authentication](/docs/greenlake/guides/public/authentication/authentication)
page.

The HTTP Authorization request header is used to provide the access token in
all API requests as a Bearer token.

- `Authorization:Bearer <access token>`


#### Authorization

All API requests are authorized using permissions. The user owning the access
token must have the required permissions assigned for the resources being accessed
in order to be authorized.

#### Required permissions

To use the HPE GreenLake Object Storage API, you need appropriate permissions based on your role:

- `object-storage.bucket.read` for all `GET` and `LIST` requests on bucket resources
- `object-storage.bucket.create` for all `POST` requests on bucket resources
- `object-storage.bucket.update` for all `PUT` requests on bucket resources
- `object-storage.bucket.delete` for all `DELETE` requests on bucket resources
- `object-storage.object-user.read` for all `GET` and `LIST` requests for user resources
- `object-storage.object-user.create` for all `POST` requests for user resources
- `object-storage.object-user.update` for all `PUT` requests for user resources
- `object-storage.object-user.delete` for all `DELETE` requests for user resources
- `object-storage.object-group.read` for all `GET` and `LIST` requests for group resources
- `object-storage.object-group.create` for all `POST` requests for group resources
- `object-storage.object-group.update` for all `PUT` requests for group resources
- `object-storage.object-group.delete` for all `DELETE` requests for group resources
- `object-storage.object-access-policy.read` for all `GET` and `LIST` requests for access policy resources
- `object-storage.object-access-policy.create` for all `POST` requests for access policy resources
- `object-storage.object-access-policy.update` for all `PUT` requests for access policy resources
- `object-storage.object-access-policy.delete` for all `DELETE` requests for access policy resources


For more information about roles and permissions, see the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html).

### Making it all work

#### General guidelines

- For asynchronous operations that return HTTP status 201 or 202, use the Location header in the API response to track progress.
- Replace the base URL in examples with the endpoint for your region.


#### Create a new bucket

Create a bucket on an HPE Alletra Storage MP X10000 device. Provide name, optional bucketTags (array of key/value pairs), and compression (example: DISABLED). Replace {systemId} with your system identifier.


```bash
POST https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets
```

Payload:


```bash
{
  "name": "myBucketName",
  "compression": "DISABLED",
  "bucketTags": [
    {
      "key": "location",
      "value": ""
    }
  ],
  "versioning": "ENABLED",
  "objectLockConfiguration": {
    "objectLockEnabled": "ENABLED",
    "rule": {
      "defaultRetention": {
        "days": 1,
        "mode": "GOVERNANCE",
        "years": 1
      }
    }
  },
  "notificationService": "DISABLED",
  "notificationServiceConfiguration": {}
}
```

The endpoint [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com) is the endpoint for the US West application. If you are using HPE GreenLake for Object Storage in a different region, replace the endpoint with the corresponding region endpoint.

#### List all buckets

Retrieve the list of buckets for the specified HPE Alletra Storage MP X10000 device. Replace {systemId} with your system identifier.


```bash
GET https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets
```

#### Delete a bucket

Delete the specified bucket on the given HPE Alletra Storage MP X10000 device. Replace {systemId} and {bucketId} with actual IDs.


```bash
DELETE https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}
```

#### Create a new user

Create a user on an HPE Alletra Storage MP X10000 device. Provide the username in the payload. Replace {systemId} with your system identifier.


```bash
POST https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users
```

Payload:


```bash
{
  "name": "NewUser"
}
```

#### List all users

Retrieve the list of users for the specified HPE Alletra Storage MP X10000 device. Replace {systemId} with your system identifier.


```bash
GET https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users
```

#### Delete a user

Delete the specified user from the given HPE Alletra Storage MP X10000 device. Replace {systemId} and {userId} with actual IDs.


```bash
DELETE https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users/{userId}
```

#### Create a new group

Create a group on an HPE Alletra Storage MP X10000 device. Provide group name and optional users array (member names). Replace {systemId} with your system identifier.


```bash
POST https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups
```

Payload:


```bash
{
  "name": "NewGroup1",
  "users": [
    "MyUser"
  ]
}
```

#### List all groups

Retrieve the list of groups for the specified HPE Alletra Storage MP X10000 device. Replace {systemId} with your system identifier.


```bash
GET https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups
```

#### Delete a group

Delete the specified group on the given HPE Alletra Storage MP X10000 device. Replace {systemId} and {groupId} with actual IDs.


```bash
DELETE https://us-west.api.greenlake.hpe.com/object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}
```