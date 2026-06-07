---
title: "HPE GreenLake Audit Logs fetch logs developer guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/audit-trail-fetch-logs-guide.md"
scraped_at: "2026-06-07T05:45:56.682110+00:00Z"
---

# HPE GreenLake Audit Logs fetch logs developer guide

The details and examples in this guide will help you fetch audit logs using the HPE GreenLake Audit Logs API. It covers filtering, pagination, sorting, and how to retrieve a single audit log or its details.

## Prerequisites

### Environment

The service is hosted at the following environment:

- [https://common.cloud.hpe.com](https://common.cloud.hpe.com)


### Hostname

The hostname for the Audit Logs fetch APIs is as follows:

- [https://global.api.greenlake.hpe.com](https://global.api.greenlake.hpe.com)


### Access and permissions

You need the correct role and permissions to use the HPE GreenLake
Audit Logs API. A role is a group of permissions that you can specify
and assign to users in your HPE GreenLake workspace. There are 3 basic
role types distinguished by the privileges defined in the authorization
service:

- Administrator—has view, edit, and delete privileges in the workspace.
- Operator—has view and edit privileges in the workspace.
- Observer—has only view privileges in the workspace.


The Observer role with view permissions for Audit Trail (`ccs.audit-trail.view`) is sufficient to make the following Audit Log API calls:

- GET /audit-log/v2beta1/logs
- GET /audit-log/v2beta1/logs/{id}
- GET /audit-log/v2beta1/logs/{id}/details


You can find out more in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html). You can:

- Find a list of preconfigured roles and the permissions they have.
- Learn how to create custom roles.
- Discover how to assign roles to users.


### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Rate limits

- 100 requests per minute per user
- 300 requests per minute overall


## Making it all work

The steps to fetch audit trail logs are as follows:

- [Fetch audit logs (list)](#fetch-audit-logs-list)
- [Fetch a specific audit log](#fetch-a-specific-audit-log)
- [Fetch audit log details](#fetch-audit-log-details)


These steps are described in more detail in the following sections.

### Fetch audit logs (list)

Use the list API to retrieve audit logs across one or more services, with filtering, pagination, and sorting.

#### Endpoint


```bash
GET https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs
```

#### Required headers

- `Authorization: Bearer <YOUR_JWT_HERE>`


#### Query parameters

- `filter` (string): Filter expression using `and`, `eq`, `contains`, `in`, `lt`, `ge`.
- `select` (string): Comma-separated fields to include in each item.
- `limit` (integer): Max results per page (max 2000, default 50).
- `offset` (integer): Zero-based offset (default 0).
- `sort` (string): Sort by field with optional `asc` or `desc` (default desc).


#### Filter parameters

| Filter Parameter | Supported Operators | Type | Example |
|  --- | --- | --- | --- |
| `createdAt` | `lt`, `ge` | RFC 3339 timestamp | `createdAt ge '2024-02-16T07:54:55.0Z'` |
| `category` | `eq`, `in` | string | `category eq 'User Management'``category in ('Device Management', 'User Activity')` |
| `description` | `eq`, `contains` | string | `contains(description, 'Logged in')` |
| `ipAddress` | `eq`, `contains` | IP string | `ipAddress eq '192.168.12.12'` |
| `username` | `eq`, `contains` | email | `username eq 'test@test.com'` |
| `workspace/name` | `eq`, `contains` | string | `workspace/name eq 'Example workspace'` |
| `workspace/type` | `eq` | string | `workspace/type eq 'TENANT'` |
| `serviceOffer/id` | `eq`, `in` | UUID | `serviceOffer/id in ('902fa943-dcfc-432c-a92c-3a3a454923d9', '00000000-0000-0000-0000-000000000000')` |
| `region` | `eq` | region code | `region eq 'us-west'` |
| `hasDetails` | `eq` | boolean | `hasDetails eq 'true'` |


Maximum five `serviceOffer/id` values are allowed in a filter. If no `serviceOffer/id` is passed, only platform audit logs are returned.

#### Selectable fields

- `serviceOffer`
- `createdAt`
- `category`
- `hasDetails`
- `workspace`
- `description`
- `username`
- `ipAddress`
- `additionalInfo`


#### Examples

Platform logs only:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs?filter=serviceOffer/id%20eq%20%2700000000-0000-0000-0000-000000000000%27' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Multiple service offers:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs?filter=serviceOffer/id%20in%20(%2700000000-0000-0000-0000-000000000000%27,%20%27d46569ae-0516-4dd2-81ce-b6d645842acc%27)%20and%20region%20eq%20%27us-west%27' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Category and time range:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs?filter=category%20eq%20%27API%20Gateway%27%20and%20createdAt%20ge%20%272025-01-16T07:54:55.0Z%27%20and%20createdAt%20lt%20%272025-02-16T07:54:55.0Z%27' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Username filter:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs?filter=username%20eq%20%27test@test.com%27' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Select fields:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs?select=createdAt,username,category' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Pagination and sorting:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs?limit=100&offset=0&sort=createdAt' \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

#### Response example


```json
{
  "count": 3,
  "offset": 0,
  "total": 100,
  "remainingRecords": true,
  "items": [
    {
      "id": "8RtJaZQBITMTdBbBUxzz",
      "type": "/audit-log/log",
      "serviceOffer": {
        "id": "68067533-5764-401a-9620-24e6e2cdc574",
        "name": "Backup and Recovery",
        "region": "us-east"
      },
      "username": "testuser@test.com",
      "category": "Storage settings",
      "description": "Storage firmware updated",
      "workspace": {
        "id": "3e35c938fb5911edbb4c660832a054ff",
        "name": "workspace name",
        "type": "STANDALONE"
      },
      "createdAt": "2024-02-10T07:54:55.0Z",
      "ipAddress": "192.168.11.21",
      "additionalInfo": {
        "serverName": "test"
      },
      "hasDetails": false
    }
  ]
}
```

### Fetch a specific audit log

This API fetches Audit details for a particular audit ID. ID here refers to the unique audit ID for a particular audit log.


```bash
GET https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs/{id}
```

Request example:


```bash
curl -i -X GET \
  https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs/8RtJaZQBITMTdBbBUxzz \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Response example:


```json
{
  "id": "8RtJaZQBITMTdBbBUxzz",
  "type": "/audit-log/log",
  "serviceOffer": {
    "id": "68067533-5764-401a-9620-24e6e2cdc574",
    "name": "Backup and Recovery",
    "region": "us-east"
  },
  "username": "testuser@test.com",
  "category": "Storage settings",
  "description": "Storage firmware updated",
  "workspace": {
    "id": "3e35c938fb5911edbb4c660832a054ff",
    "name": "workspace name",
    "type": "STANDALONE"
  },
  "createdAt": "2024-02-10T07:54:55.0Z",
  "ipAddress": "192.168.11.21",
  "additionalInfo": {
    "serverName": "test"
  },
  "hasDetails": false
}
```

### Fetch audit log details

Get a specific audit log details. Provide the ID of the audit log record to fetch the audit log details. You can get the ID of the audit log while fetching all audit logs.


```bash
GET https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs/{id}/details
```

Request example:


```bash
curl -i -X GET \
  https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs/8RtJaZQBITMTdBbBUxzz/details \
  -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Response example:


```json
{
  "id": "8RtJaZQBITMTdBbBUxzz",
  "type": "/audit-log/log/details",
  "header": "Storage Firmware Update",
  "body": ["Firmware version: 1.2.3", "Update status: Successful"]
}
```