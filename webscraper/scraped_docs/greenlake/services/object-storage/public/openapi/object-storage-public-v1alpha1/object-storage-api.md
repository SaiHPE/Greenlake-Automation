---
title: "HPE Greenlake For Object Storage REST APIs."
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api.md"
scraped_at: "2026-06-07T05:46:33.970630+00:00Z"
---

# HPE Greenlake For Object Storage REST APIs.

HPE Greenlake For Object Storage REST APIs.

Version: 1.1.0
License: HPE End User License Agreement

## Servers

```
https://eu1.data.cloud.hpe.com
```

```
https://us1.data.cloud.hpe.com
```

```
https://jp1.data.cloud.hpe.com
```

## Security

### bearer

Storage Fleet API uses a JWT bearer token for authentication.
An authentication token can be obtained from the HPE GreenLake console.


Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE Greenlake For Object Storage REST APIs.](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api.yaml)

## access-policies

The Access Policies API provides endpoints for creating, managing, and configuring access policies. 

### Get all access policies for HPE Alletra Storage MP X10000 ObjectStore

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/devicetype7listaccesspolicies.md): Retrieves all access policies associated with the HPE Alletra Storage MP X10000 ObjectStore identified by {systemId}. The response can be filtered, sorted, and paginated using query parameters.

### Create new access policy for HPE Alletra Storage MP X10000 ObjectStore

 - [POST /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/devicetype7createaccesspolicy.md): Create new access policy for HPE Alletra Storage MP X10000 ObjectStore identified by {systemId}

### Delete HPE Alletra Storage MP X10000 ObjectStore access policy

 - [DELETE /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/devicetype7deleteaccesspolicybyid.md): Delete HPE Alletra Storage MP X10000 ObjectStore access policy identified by {policyId}

### Get single HPE Alletra Storage MP X10000 ObjectStore access policy

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/devicetype7getaccesspolicybyid.md): Get HPE Alletra Storage MP X10000 ObjectStore access policy identified by {policyId}

### Update HPE Alletra Storage MP X10000 ObjectStore access policy

 - [PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/devicetype7updateaccesspolicybyid.md): Update HPE Alletra Storage MP X10000 ObjectStore access policy identified by {policyId}

### Apply policy to existing user or group in HPE Alletra Storage MP X10000 ObjectStore

 - [PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/apply-policy](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/access-policies/applypolicy.md): Apply policy to existing user or group in HPE Alletra Storage MP X10000 ObjectStore identified by {systemId}

## buckets

The Buckets API provides endpoints for creating, managing, and configuring storage buckets.  Buckets are containers for organizing and storing data, and this API allows full control over their  lifecycle, including creation, updates, retrieval, and deletion.

### Get all buckets for HPE Alletra Storage MP X10000 ObjectStore

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7listbuckets.md): Retrieves a list of buckets associated with a specific HPE Alletra Storage MP X10000 ObjectStore. The results can be filtered, sorted, and paginated using query parameters to customize the response based on your requirements.

### Create new bucket in HPE Alletra Storage MP X10000 ObjectStore

 - [POST /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7createbucket.md): Create new bucket in HPE Alletra Storage MP X10000 ObjectStore identified by {systemId}

### Delete bucket from HPE Alletra Storage MP X10000 ObjectStore

 - [DELETE /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7deletebucketbyid.md): Delete bucket from HPE Alletra Storage MP X10000 ObjectStore identified by {bucketId}

### Get single HPE Alletra Storage MP X10000 ObjectStore bucket

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7singlebuckets.md): Get HPE Alletra Storage MP X10000 ObjectStore bucket identified by {bucketId}

### Edit the properties of an existing bucket in HPE Alletra Storage MP X10000 ObjectStore

 - [PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/devicetype7editbucket.md): Edit bucket properties in HPE Alletra Storage MP X10000 ObjectStore identified by {systemId} and {bucketId}

### Get capacity trend data of buckets

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/buckets/{bucketId}/capacity-history](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/buckets/bucketcapacityhistory.md): Get capacity trend data of buckets

## groups

The Groups API provides endpoints for creating, managing, and configuring groups.

### Get all groups for HPE Alletra Storage MP X10000 ObjectStore

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/groups/devicetype7listgroups.md): Get all groups for HPE Alletra Storage MP X10000 ObjectStore identified by {systemId}

### Create new group in HPE Alletra Storage MP X10000 ObjectStore

 - [POST /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/groups/devicetype7creategroup.md): Create new group in HPE Alletra Storage MP X10000 ObjectStore identified by {systemId}

### Delete group from HPE Alletra Storage MP X10000 ObjectStore

 - [DELETE /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/groups/devicetype7deletegroupbyid.md): Delete group from HPE Alletra Storage MP X10000 ObjectStore identified by {groupId}

### Get single group details for HPE Alletra Storage MP X10000 ObjectStore

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/groups/devicetype7getgroupbyid.md): Get single group details for HPE Alletra Storage MP X10000 ObjectStore identified by {groupId}

### Update group details in HPE Alletra Storage MP X10000 ObjectStore

 - [PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/groups/devicetype7updategroupbyid.md): Update group details in HPE Alletra Storage MP X10000 ObjectStore identified by {groupId}

## users

The Users API provides endpoints for creating, managing, and configuring users.

### Get the properties of existing users in ObjectStore

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/users/devicetype7getuser.md): Get users properties in ObjectStore identified by {systemId}

### Create new user in HPE Alletra Storage MP X10000 device

 - [POST /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/users/devicetype7createuser.md): Create new user in HPE Alletra Storage MP X10000 device identified by {systemId}

### Delete user from HPE Alletra Storage MP X10000 ObjectStore

 - [DELETE /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users/{userId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/users/devicetype7deleteuserbyid.md): Delete user from HPE Alletra Storage MP X10000 ObjectStore identified by {bucketId}

### Get the properties of an existing user in ObjectStore

 - [GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users/{userId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/users/devicetype7getsingleuser.md): Get user properties in ObjectStore identified by {systemId} and {userId}

### Edit the properties of an existing user in HPE Alletra Storage MP X10000 ObjectStore

 - [PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/users/{userId}](https://developer.greenlake.hpe.com/docs/greenlake/services/object-storage/public/openapi/object-storage-public-v1alpha1/object-storage-api/users/devicetype7edituser.md): Edit user properties in HPE Alletra Storage MP X10000 ObjectStore identified by {systemId} and {userId}

