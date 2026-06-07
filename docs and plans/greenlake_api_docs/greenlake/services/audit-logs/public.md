---
title: "HPE GreenLake for Audit Logs"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public.md"
scraped_at: "2026-06-07T05:45:57.593176+00:00Z"
---

# HPE GreenLake for Audit Logs

This page provides an introduction and quick start guide for the Audit Logs API:

- [Overview](#overview)—See a high-level description of the service.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake for Audit Log service offers:

- A collection of RESTful APIs for publishing audit logs, managing configurations, and retrieving application-specific and overall platform logs.
- An event that provides real time notification when an audit log entry was created.


### API availability across platforms

| Endpoint | HPE GreenLake cloud | HPE GreenLake Dedicated Platform |
|  --- | --- | --- |
| `GET /audit-log/v1/logs/{id}/detail` | Yes | Yes |
| `GET /audit-log/v1/logs` | Yes | Yes |
| `GET /audit-log/v2beta1/logs/{id}/details` | Yes | Yes |
| `GET /audit-log/v2beta1/logs` | Yes | Yes |


### What's new

The following table outlines the most recent changes to the HPE GreenLake for Audit Logs service.

| Type | Date | Description | Changelog |
|  --- | --- | --- | --- |
| APIs | 2026-04-24 | A new `v2beta1` version was released. The `v1` version is not currently flagged for deprecation. | [View the changelog for more information.](/docs/greenlake/services/audit-logs/public/openapi/changelog) |
| Events | October 2024 | The **Audit Log Created** event was released. | [View the changelog for more information.](/docs/greenlake/services/audit-logs/public/catalog/changelog) |


### Related documentation

[GreenLake Cloud User Guide: Audit logs](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-3FA3DE5E-9769-4D3E-9582-097A50DA0565.html)

## Developer guide

This guide helps you get started using the Audit Logs API.

### Prerequisites

#### Environment

The audit logs service is hosted at the following environment:

- [https://common.cloud.hpe.com](https://common.cloud.hpe.com)


#### Hostname

The hostname for the Audit Logs APIs is as follows:

- [https://global.api.greenlake.hpe.com](https://global.api.greenlake.hpe.com)


#### URI

The URIs for the audit logs APIs are as follows:

- `/audit-log/v1/logs`
- `/audit-log/v1/logs/{audit-id}/detail`
- `/audit-log/v2beta1/logs`
- `/audit-log/v2beta1/logs/{id}`
- `/audit-log/v2beta1/logs/{id}/details`


#### Access and permissions

You need appropriate roles and permissions to use the HPE GreenLake Audit Logs API. Roles define sets of permissions that control user access within your workspace. There are three basic role types distinguished by the privileges defined in the authorization service:

- Administrator—Full access with view, edit, and delete privileges
- Operator—View and edit privileges
- Observer—Read-only access with view privileges only


The Observer role with view permissions for Audit Trail (`ccs.audit-trail.view`) is sufficient to make the following Audit Log API calls:

- `GET /audit-log/v1/logs`
- `GET /audit-log/v1/logs/{audit-id}/detail`
- `GET /audit-log/v2beta1/logs`
- `GET /audit-log/v2beta1/logs/{id}`
- `GET /audit-log/v2beta1/logs/{id}/details`


You can find out more in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html). You can:

- View preconfigured roles and their permissions
- Learn how to create custom roles
- Discover how to assign roles to users


#### Rate limits

| Endpoint | Rate limits |
|  --- | --- |
| `GET /audit-log/v2beta1/logs` | 100 requests per minute per user300 requests per minute overall |
| `GET /audit-log/v2beta1/logs/{id}` | 150 requests per minute per user80 requests per minute overall |
| `GET /audit-log/v2beta1/logs/{id}/details` | 150 requests per minute per user80 requests per minute overall |


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as authorization bearer tokens. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


With the client ID and client secret, the access token can be fetched programmatically. Run the CURL command to get the token from the `response["access_token"]`:

- Using CURL:

```bash
curl -X POST https://<HPE_Cloud_Base_URL>/authorization/v2/oauth2/<WORKSPACE_ID>/token -H
"Content-Type: application/x-www-form-urlencoded"
-d "grant_type=client_credentials&client_id=$YOUR_CLIENT_ID&client_secret=$YOUR_CLIENT_SECRET"
```


This access token is used as the bearer token for the authentication of the Audit Logs APIs.

- Using Python:

```python
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

client = BackendApplicationClient(YOUR_CLIENT_ID)


oauth = OAuth2Session(client=client)
auth = HTTPBasicAuth(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)


token = oauth.fetch_token(token_url='https://<HPE_Cloud_Base_URL>/authorization/v2/oauth2/<WORKSPACE_ID>/token', auth=auth)
print(token["access_token"])
```


This access token is used as the bearer token for the authentication of the Audit Logs APIs.

### Making it all Work

There are two versions of the Audit Log API, a [v2beta1 version](#v2beta1) and a [v1 version](#v1).

#### v2beta1

To fetch audit logs:

- [Fetch a specific audit log](/docs/greenlake/services/audit-logs/public#fetch-a-specific-audit-log)
- [Fetch specific audit log details](/docs/greenlake/services/audit-logs/public#fetch-specific-audit-log-details)
- [Fetch audit logs (list)](#fetch-audit-logs-list)


These steps are described in more detail in the following sections.

##### Fetch a specific audit log

Use this `GET` request to return information on a specific audit log by providing the ID of the audit log record.

Example:


```bash
curl -i -X GET \
  'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs/{id}' \
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
  "hasDetails": true
}
```

##### Fetch specific audit log details

Many audit logs will have additional information. If an audit log's `hasDetails` field is true, the details API fetches the additional details.

Sample requests:


```bash
curl -i -X GET \
 'https://global.api.greenlake.hpe.com/audit-log/v2beta1/logs/{id}/details' \
 -H 'Authorization: Bearer <YOUR_JWT_HERE>'
```

Sample response:


```json
{
  "id": "8RtJaZQBITMTdBbBUxzz",
  "type": "/audit-log/log/details",
  "header": "Storage Firmware Update",
  "body": ["Firmware version: 1.2.3", "Update status: Successful"]
}
```

##### Fetch audit logs (list)

Use the list API to retrieve audit logs across one or more services, with filtering, pagination, and sorting.

The endpoint:


```bash
curl --location --request GET '{{Hostname}}/audit-log/v2beta1/logs' --header 'Authorization: Bearer {{ACCESS_TOKEN}}'
```

###### Query parameters

This endpoint supports the following query parameters:

- `filter` (string): Filter expression using `and`, `eq`, `contains`, `in`, `lt`, `ge`.
- `select` (string): Comma-separated fields to include in each item.
- `limit` (integer): Max results per page (max 2000, default 50).
- `offset` (integer): Zero-based offset (default 0).
- `sort` (string): Sort by field with optional `asc` or `desc` (default desc).


The following table describes the supported `filter` parameters and operators:

| Filter parameter | Supported operators | Type | Example |
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

The following are the available selectable (`select`) fields:

- `serviceOffer`
- `createdAt`
- `category`
- `hasDetails`
- `workspace`
- `description`
- `username`
- `ipAddress`
- `additionalInfo`


###### Example API calls

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

###### Response example


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
      "hasDetails": true
    }
  ]
}
```

#### v1

To fetch audit logs:

- [Get all the audit logs of an application instance or platform logs](/docs/greenlake/services/audit-logs/public#get-all-the-audit-logs-of-an-application-instance-or-platform-logs)
- [Get additional details of audit log](/docs/greenlake/services/audit-logs/public#get-additional-details-of-audit-log)


These steps are described in more detail in the following sections.

##### Get all the audit logs of an application instance or platform logs

By default, the API will return the all audit logs. Run the below API with the bearer token from the previous step to get all the audit logs related to your workspace.

Audit logs for the past three months can be retrieved using this API.

Sample requests:


```bash
curl --location --request GET '{{Hostname}}/audit-log/v1/logs' --header 'Authorization: Bearer {{ACCESS_TOKEN}}'
```

Sample API response:


```json
{
  "items": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "type": "/audit-log/logs",
      "user": {
        "username": "example@test.com"
      },
      "application": {
        "id": "59812345678904f7861"
      },
      "region": "us-west",
      "category": "User Management",
      "description": "User test@dummy.com logged in via ping mode.",
      "workspace": {
        "id": "565c6efa-6276-4993-31t4-aa345h3a9803",
        "workspaceName": "HPE GreenLake"
      },
      "createdAt": "2019-08-24T14:15:22Z",
      "updatedAt": "2019-08-24T14:15:22Z",
      "additionalInfo": {
        "ipAddress": "104.36.311.11"
      },
      "hasDetails": true,
      "generation": 1
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 10,
  "remainingRecords": false
}
```

To retrieve audit logs for a particular application instance, include the application ID and region code in which application is provisioned in the API query filter parameters.

The search API supports several query parameters. Refer to the API reference for supported query parameters.

Audit logs can be filtered using `filter` query, refer to [filtering](/docs/greenlake/services/audit-logs/public/guide#filtering) for more details.

This API returns a 200 status code with a paginated response. For more details, see the **API reference**.

##### Get additional details of audit log

Many audit logs will have additional information. If an audit log's `hasDetails` field is true, the details API fetches the additional details.

Sample requests:


```bash
curl --location --request GET '{{Hostname}}/audit-log/v1/logs/{id}/detail'
```

Sample response:


```json
{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "type": "audit_details",
  "header": "configuration",
  "body": [
    "Updated configuration from level 1 to level 2"
  ]
}
```

### Filtering

Filters allow you to limit the audit logs returned by a REST API call. Use the `filter` query parameter to specify your criteria.

#### Requirements

- Queries will be separated by `and`.
- Queries will have 'equality', 'contains' and 'in' comparison.
- Each query must follow below format for different operators.
  - key eq 'value' for an equality operation.
  - contains(key, 'value') for a contains operation.
  - key in ('value1', 'value2') for an in operation.
- `createdAt` **value** should have the format **'yyyy-mm-ddTHH:mm:ssZ'**.


#### A simple example

Here is a simple example of filtering audit logs based on a category:


```bash
curl --location --request GET <URI>?filter=category eq 'User Management'
```

In this example, the API call returns the audit logs with the category User Management.

An example of filtering for a month:


```bash
curl --location --request GET <URI>?filter=createdAt ge '2023-05-01T12:00:00.00Z' and createdAt lt '2023-06-01T12:00:00.00Z'
```

In this example, the API call returns all audit logs from May 2023.

An example of filtering logs based on user/username:


```bash
curl --location --request GET <URI>?filter=user/username eq 'example@test.com'
```

In this example, the API call returns all audit logs related to '[example@test.com](mailto:example@test.com)'

#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).

### Error handling

For complete error schemas and examples, see the **API Reference**.

Common scenarios:

- **401 Unauthorized**: Access token expired or invalid. Regenerate your token.
- **403 Forbidden**: Insufficient permissions. Verify your permissions.
- **429 Too Many Requests**: Rate limit exceeded. Implement exponential backoff.
- **400 Bad Request**: Invalid filter syntax.


All errors include:

- `errorCode`: Machine-readable error identifier
- `message`: Human-readable description
- `debugId`: Unique identifier for support requests
- `httpStatusCode`: Standard HTTP status code