---
title: "HPE GreenLake for Service Catalog"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public.md"
scraped_at: "2026-06-07T06:13:28.887463+00:00Z"
---

# HPE GreenLake for Service Catalog

This page provides an introduction and quick start guide for the Service Catalog API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake for Service Catalog service offers a collection of RESTful APIs to fetch and provision service managers and delete a service manager provisioned in a workspace. It also allows service offers to be onboarded onto the HPE GreenLake cloud via APIs.

### Features

- Gather service manager details in a workspace.
- Provision a service manager to a region in a workspace.
- Delete a service manager provisioned in a workspace.
- Endpoints to manage service offers and service provision.


### What's New

Date: June 2025

The following collections of beta API endpoints were added:

- Service offers
- Service offer regions
- Service provisions


[View the Changelog for more information](/docs/greenlake/services/service-catalog/public/openapi/changelog)

#### Deprecated

The following APIs are being deprecated and removed on their end-of-life date. Use the replacement APIs.

| API | Deprecated endpoint | Deprecation date | Replacement endpoint |
|  --- | --- | --- | --- |
| Get a specific service manager | `GET /service-catalog/v1beta1/service-managers/{id}` | 2025-06-30 | `GET /service-catalog/v1/service-managers/{id}` |
| Get service manager | `GET /service-catalog/v1beta1/service-managers/{id}` | 2025-06-30 | `GET /service-catalog/v1/service-managers/{id}` |
| Get service managers by region | `GET /service-catalog/v1beta1/per-region-service-managers` | 2025-06-30 | `GET /service-catalog/v1/per-region-service-managers` |
| Get service managers deployed in a specific region | `GET /service-catalog/v1beta1/per-region-service-managers/{id}` | 2025-06-30 | `GET /service-catalog/v1/per-region-service-managers/{id}` |
| Provision a service manager in a given region | `POST /service-catalog/v1beta1/service-manager-provisions` | 2025-06-30 | `POST /service-catalog/v1/service-manager-provisions` |
| Get a specific service manager provision entry | `GET /service-catalog/v1beta1/service-manager-provisions/{id}` | 2025-06-30 | `GET /service-catalog/v1/service-manager-provisions/{id}` |
| Delete a service manager provision entry | `DELETE /service-catalog/v1beta1/service-manager-provisions/{id}` | 2025-06-30 | `DELETE /service-catalog/v1/service-manager-provisions/{id}` |
| Get service manager provisions | `GET /service-catalog/v1beta1/service-manager-provisions` | 2025-06-30 | `GET /service-catalog/v1/service-manager-provisions` |


## Developer guide

The details and examples in this guide will help you use the HPE GreenLake for Service Catalog API.

### Prerequisites

#### Environment

The Service Catalog service is hosted at the following URL:

- [https://common.cloud.hpe.com](https://common.cloud.hpe.com)


#### Hostname

The hostname for the Service Catalog endpoints is:

- [https://global.api.greenlake.hpe.com](https://global.api.greenlake.hpe.com)


#### URI

The URIs for the **Service Manager** APIs are as follows:

- `GET /service-catalog/v1/service-managers`
- `GET /service-catalog/v1/service-managers/{id}`
- `GET /service-catalog/v1/per-region-service-managers`
- `GET /service-catalog/v1/per-region-service-managers/{id}`


The URIs for the **Service Manager Provision** APIs are as follows:

- `POST /service-catalog/v1/service-manager-provisions`
- `GET /service-catalog/v1/service-manager-provisions`
- `GET /service-catalog/v1/service-manager-provisions/{id}`
- `DELETE /service-catalog/v1/service-manager-provisions/{id}`


#### Access and permissions

You need the correct roles and permissions to use the HPE GreenLake
Service Catalog API. A role is a group of permissions that you can specify
and assign to users in your HPE GreenLake workspace. There are three basic
role types distinguished by the privileges defined in the authorization
service:

- Administrator—has view, edit, and delete privileges in the
workspace.
- Operator—has view and edit privileges in the workspace.
- Observer—has only view privileges in the workspace.


| Endpoint group | Endpoint | Required role | Permission |
|  --- | --- | --- | --- |
| Service Manager | `GET /service-catalog/v1/service-managers` | Observer | `ccs.app-catalog.view` |
| Service Manager | `GET /service-catalog/v1/service-managers/{id}` | Observer | `ccs.app-catalog.view` |
| Service Manager | `GET /service-catalog/v1/per-region-service-managers` | Observer | `ccs.app-catalog.view` |
| Service Manager | `GET /service-catalog/v1/per-region-service-managers/{id}` | Observer | `ccs.app-catalog.view` |
| Service Manager Provision | `GET /service-catalog/v1/service-manager-provisions` | Observer | `ccs.app-provision.view` |
| Service Manager Provision | `GET /service-catalog/v1/service-manager-provisions/{id}` | Observer | `ccs.app-provision.view` |
| Service Manager Provision | `POST /service-catalog/v1/service-manager-provisions` | Administrator, Operator | `ccs.app-provision.edit` |
| Service Manager Provision | `DELETE /service-catalog/v1/service-manager-provisions/{id}` | Administrator, Operator | `ccs.app-provision.edit` |
| Service Offer | `GET /service-catalog/v1beta1/service-offers` | Observer | `ccs.service-catalog.view` |
| Service Offer | `GET /service-catalog/v1beta1/service-offers/{id}` | Observer | `ccs.service-catalog.view` |
| Service Offer Region | `GET /service-catalog/v1beta1/service-offer-regions` | Observer | `ccs.service-catalog.view` |
| Service Offer Region | `GET /service-catalog/v1beta1/service-offer-regions/{id}` | Observer | `ccs.service-catalog.view` |
| Service Provision | `GET /service-catalog/v1beta1/service-provisions` | Observer | `ccs.service-catalog.view` |
| Service Provision | `GET /service-catalog/v1beta1/service-provisions/{id}` | Observer | `ccs.service-catalog.view` |
| Service Provision | `POST /service-catalog/v1beta1/service-provisions` | Administrator, Operator | `ccs.service-catalog.edit` |
| Service Provision | `DELETE /service-catalog/v1beta1/service-provisions/{id}` | Administrator, Operator | `ccs.service-catalog.delete` |
| Service Provision | `POST /service-catalog/v1beta1/service-provisions/{id}/retry-unprovision` | Administrator, Operator | `ccs.service-catalog.edit` |
| Service Provision | `POST /service-catalog/v1beta1/service-provisions/{id}/retry` | Administrator, Operator | `ccs.service-catalog.edit` |


You can find out more in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-06D20B01-71CE-412C-8BBA-6005ACF4EA99.html). You can:

- Find a list of preconfigured roles and the permissions that they have.
- Learn how to create custom roles.
- Discover how to assign roles to users.


#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


With the client ID and client secret, there are two ways to fetch the access token programmatically. Run the following cURL command or the Python script to get the token from the `response["access_token"]`:

- Using cURL:

```bash

curl -X POST https://sso.common.cloud.hpe.com/as/token.oauth2 -H

"Content-Type: application/x-www-form-urlencoded"

-d "grant_type=client_credentials&client_id=$YOUR_CLIENT_ID&client_secret=$YOUR_CLIENT_SECRET"
```
- Using Python:

```python

from oauthlib.oauth2 import BackendApplicationClient

from requests.auth import HTTPBasicAuth

from requests_oauthlib import OAuth2Session


client = BackendApplicationClient(YOUR_CLIENT_ID)



oauth = OAuth2Session(client=client)

auth = HTTPBasicAuth(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)



token = oauth.fetch_token(token_url='https://sso.common.cloud.hpe.com/as/token.oauth2', auth=auth)

print(token["access_token"])
```


This access token is used as the bearer token to authenticate the Service Catalog APIs.

### Making it all Work

#### Get service managers

Use this `GET` request to retrieve a list of the service managers available in your workspace.


```bash
  GET https://global.api.greenlake.hpe.com/service-catalog/v1/service-managers
```

Sample API response:


```json
{
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Aruba Central",
      "description": "Manage your wired, wireless, and WAN infrastructure",
      "createdAt": "2021-04-23T07:50:30.400Z",
      "updatedAt": "2021-04-29T07:50:30.400Z",
      "generation": 1,
      "type": "/service-catalog/service-manager"
    }
  ],
  "offset": 0,
  "count": 1,
  "total": 10
}
```

#### Get service manager details

Use this `GET` API call to retrieve details on a particular service manager in a workspace by specifying a service manager ID. The service manager ID is a 36-character alphanumeric universal unique identifier (UUID).


```bash
  GET https://global.api.greenlake.hpe.com/service-catalog/v1/service-managers/{id}
```

Sample response:


```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Aruba Central",
  "description": "Manage your wired, wireless, and WAN infrastructure",
  "createdAt": "2021-04-23T07:50:30.400Z",
  "updatedAt": "2021-04-29T07:50:30.400Z",
  "generation": 1,
  "type": "/service-catalog/service-manager"
}
```

#### Get a list of service managers by region

Return a list of all service managers in your workspace, categorized by the regions the service managers are deployed in.


```bash
GET https://global.api.greenlake.hpe.com/service-catalog/v1/per-region-service-managers
```

Sample response:


```json
{
  "items": [
    {
      "id": "us-east",
      "regionName": "US East",
      "serviceManagers": [
        {
          "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "name": "Aruba Central",
          "description": "Manage your wired, wireless, and WAN infrastructure",
          "createdAt": "2021-04-23T07:50:30.400Z",
          "updatedAt": "2021-04-29T07:50:30.400Z",
          "generation": 1,
          "type": "/service-catalog/service-manager"
        }
      ],
      "generation": 1,
      "type": "/service-catalog/service-manager"
    }
  ],
  "offset": 0,
  "count": 1,
  "total": 10
}
```

Filter this API by the `mspSupported` field using the filter query parameter, for example, `filter=mspSupported eq true` or `filter=mspSupported eq false`.

#### Get service managers in a specific region

Retrieve a list of all service managers deployed in a specified region. The available regions are:

- `ap-ausnz`
- `ap-east`
- `ap-northeast`
- `ap-south`
- `ap-southeast`
- `ca-central`
- `ca-east`
- `cn-east`
- `cn-north`
- `eu-central`
- `eu-north`
- `eu-west`
- `mea`
- `sa-east`
- `us-central`
- `us-east`
- `us-gov`
- `us-west`
- `att-mcd-us-west`
- `att-ent-us-west`
- `att-hilton-us-west`



```bash
GET https://global.api.greenlake.hpe.com/service-catalog/v1/per-region-service-managers/{id}
```

Sample response:


```json
{
  "id": "us-west",
  "regionName": "US West",
  "serviceManagers": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Aruba Central",
      "description": "Manage your wired, wireless, and WAN infrastructure",
      "createdAt": "2021-04-23T07:50:30.400Z",
      "updatedAt": "2021-04-29T07:50:30.400Z",
      "generation": 1,
      "type": "/service-catalog/service-manager"
    }
  ],
  "generation": 1,
  "type": "/service-catalog/service-manager"
}
```

#### Get a list of provisioned service managers

Retrieve a list of all service managers provisioned for your workspace.


```bash
GET https://global.api.greenlake.hpe.com/service-catalog/v1/service-manager-provisions
```

Sample response:


```json
{
  "items": [
    {
      "id": "2fa85f64-5717-4562-b3fc-2c963f66afa1",
      "resourceUri": "/service-catalog/v1/service-manager-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa1",
      "serviceManager": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6"
      },
      "region": "us-west",
      "provisionStatus": "PROVISION_INITIATED",
      "createdBy": "john@acme.com",
      "createdAt": "2021-04-23T07:50:30.400Z",
      "updatedAt": "2021-04-29T07:50:30.400Z",
      "generation": 1,
      "type": "/service-catalog/service-manager-provision"
    }
  ],
  "offset": 0,
  "count": 1,
  "total": 10
}
```

Filter this API by the `serviceManagerId`, `status`, or `region` field using the filter query parameter, for example, `serviceManagerId eq '767c0c92-5ecc-4952-85d6-06d2bcaaf050'`, `status eq 'PROVISIONED'`, `status eq 'UNPROVISIONED'`, or `region eq 'us-west'`.

#### Get a specific service manager provisioned by id for a workspace

Use this `GET` request to retrieve information on a provisioned service manager by supplying a service manager provision ID.


```bash
GET https://global.api.greenlake.hpe.com/service-catalog/v1/service-manager-provisions/{id}
```

Sample response:


```json
{
  "id": "2fa85f64-5717-4562-b3fc-2c963f66afa1",
  "resourceUri": "/service-catalog/v1/service-manager-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa1",
  "serviceManager": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6"
  },
  "region": "us-west",
  "provisionStatus": "PROVISION_INITIATED",
  "createdBy": "john@acme.com",
  "createdAt": "2021-04-23T07:50:30.400Z",
  "updatedAt": "2021-04-29T07:50:30.400Z",
  "generation": 1,
  "type": "/service-catalog/service-manager-provision",
  "reason": "Service unprovisioning failed, please retry or contact HPE services representatives."
}
```

#### Provision a service manager for a workspace

Use this `POST` API call to provision a service manager to a chosen region in your workspace. Provisioning a service manager is an asynchronous process. Check the `provisionStatus` field to see the current status.

- Delete any service manager provision entries that failed provisioning.
- If a service manager provision already exists, a conflict is reported.



```bash
POST https://global.api.greenlake.hpe.com/service-catalog/v1/service-manager-provisions
```

Payload:


```json
{
  "serviceManagerId": "{id}",
  "region": "{region}"
}
```

Sample response:


```json
{
  "id": "2fa85f64-5717-4562-b3fc-2c963f66afa1",
  "resourceUri": "/service-catalog/v1/service-manager-provisions/2fa85f64-5717-4562-b3fc-2c963f66afa1",
  "serviceManager": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "resourceUri": "/service-catalog/v1/service-managers/3fa85f64-5717-4562-b3fc-2c963f66afa6"
  },
  "region": "us-west",
  "createdBy": "john@acme.com",
  "generation": 1,
  "type": "/service-catalog/service-manager-provision"
}
```

#### Delete a service manager provisioned for a workspace

Use this `DELETE` API call to deprovision or delete a provisioned service manager. Before starting the delete operation, ensure that there are no devices associated with the workspace.


```bash
DELETE https://global.api.greenlake.hpe.com/service-catalog/v1/service-manager-provisions/{id}
```

The `DELETE` API returns a 204 status code on successful deletion.

### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the action is restricted to a response that meets the filter requirements. Filters are specified by using the query parameter `filter`.

#### A filtering example


```bash
GET <URI>?filter=status eq 'PROVISIONED'
```

This example shows a simple filter. The resources returned by the query are limited to results when the attribute `status` has the value `PROVISIONED`. Note that within the filter, the separator is a space.

#### Filtering query parameters

`filter = <property> <operation> <literal>`

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the Operation.

**Operation** is the comparison operation to be evaluated. The Service Catalog API supports the **eq** operation for filtering. The **eq** operation is used to compare the value of a property with a literal. Examples of using the **eq** operation:

- **eq**: `status eq 'UNPROVISIONED'`: The status is unprovisioned.
- **eq**: `serviceManagerId eq '5aa0d7b7-5896-4a24-9090-71334a95db38'` : Filters on a specified service manager ID.
- **eq**: `mspSupported eq false` : MSP is not supported.


**Literal** is the value the property is to be compared against. Operations compare properties against literals. For a successful matching operation, the types must match and the syntax determines the type of the literals. For example, the filter `(age eq '3')` would not work if age is an integer, and `(age eq 3)` would not work if age is a string.
Due to [URL encoding](https://en.wikipedia.org/wiki/URL_encoding), reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent encoded equivalents.

The following examples explain literals.

- **String**: 'anything in single quotes'
  - Reserved characters in string literals must be URL encoded.
- **Integer**: -100,-1,0,1,100
- **Boolean**: true, false
- **Null**: null.
  - Null is equal to itself and nothing else. Null is not greater or less than anything.


#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).