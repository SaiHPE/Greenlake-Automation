---
title: "HPE GreenLake for Audit Logs developer guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/audit-logs/public/guide.md"
scraped_at: "2026-06-07T06:13:20.948964+00:00Z"
---

# HPE GreenLake for Audit Logs developer guide

The details and examples in this guide will help you get started using the HPE GreenLake Audit Logs APIs.

## Prerequisites

### Environment

The audit logs service is hosted at the following environment:

- [https://common.cloud.hpe.com](https://common.cloud.hpe.com)


### Hostname

The hostname for the Audit Logs APIs is as follows:

- [https://global.api.greenlake.hpe.com](https://global.api.greenlake.hpe.com)


### URI

The URIs for the audit logs APIs are as follows:

- **Fetch all audit logs**: `/audit-log/v1/logs`
- **Fetch additional details of a specific audit log**: `/audit-log/v1/logs/{audit-id}/detail`


## Access and permissions

You need the correct role and permissions to use the HPE GreenLake
Audit Logs API. A role is a group of permissions that you can specify
and assign to users in your HPE GreenLake workspace. There are 3 basic
role types distinguished by the privileges defined in the authorization
service:

- Administrator—has view, edit, and delete privileges in the workspace.
- Operator—has view and edit privileges in the workspace.
- Observer—has only view privileges in the workspace.


The Observer role with view permissions for Audit Trail (`ccs.audit-trail.view`) is sufficient to make the following Audit Log API calls:

- GET /audit-log/v1/logs/{id}/detail
- GET /audit-log/v1/logs


You can find out more in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html). You can:

- Find a list of preconfigured roles and the permissions they have.
- Learn how to create custom roles.
- Discover how to assign roles to users.


## Making it all Work

The steps to fetch audit logs are as follows:

- [Getting an access token for APIs](/docs/greenlake/services/audit-logs/public/guide/#getting-an-access-token-for-apis) (*short lived*)
- [Get all the audit logs of an application instance or platform logs](/docs/greenlake/services/audit-logs/public/guide#get-all-the-audit-logs-of-an-application-instance-or-platform-logs)
- [Get additional details related to an audit log](/docs/greenlake/services/audit-logs/public/guide#get-additional-details-of-audit-log)
- These steps are described in more detail in the following sections.


### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Getting an access token for APIs

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

### Get all the audit logs of an application instance or platform logs

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

This API returns a 200 status code with a paginated response. For more details, see the API reference:

- [HPE GreenLake API for Audit Logs](https://api.redocly.com/registry/bundle/hpe/HPE%20GreenLake%20Audit%20Logs%20-%20V1/v1/openapi.yaml?branch=mainline)


### Get additional details of audit log

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

## Filtering

Filters allow you to limit the resources involved in a REST call. They are specified using the query parameter `filter`. In this case, `filter` filters the audit logs based on the parameters listed below.

- `category`
- `description`
- `user/username`
- `createdAt`
- `ipAddress`
- `target`
- `workspace/workspaceName`
- `application/id`
- `region`


### Requirements

- Queries will be separated by `and`.
- Queries will have 'equality', 'contains' and 'in' comparison.
- Each query must follow below format for different operators.
  - key eq 'value' for an equality operation.
  - contains(key, 'value') for a contains operation.
  - key in ('value1', 'value2') for an in operation.
- createdAt ***value*** should have the format ***'yyyy-mm-ddTHH:mm:ssZ'***.


### A simple example

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

### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).