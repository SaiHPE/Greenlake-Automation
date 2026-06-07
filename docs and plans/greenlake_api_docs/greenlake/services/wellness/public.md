---
title: "HPE GreenLake for Wellness"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public.md"
scraped_at: "2026-06-07T06:13:30.261279+00:00Z"
---

# HPE GreenLake for Wellness

This page provides an introduction and quick start guide for the Wellness API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

HPE GreenLake Wellness APIs facilitate the automation of IT operations by enabling you to monitor wellness events related to your infrastructure. Wellness events provide health insights about your HPE products and services and show information about automatically created support cases.

These APIs provide various filtering options and KPI metrics to streamline integration workflows further.

### Use cases

Wellness events allow you to:

- Identify potential vulnerabilities before they affect your environment.
- Proactively monitor the health of your HPE products and services.
- View AI-powered recommendations about events.


### What's new

Date: 2024-09-19

New stable version `v2` released.

[View the changelog for more information.](/docs/greenlake/services/wellness/public/openapi/changelog)

### Related documentation

[HPE GreenLake Cloud User Guide: Wellness Dashboard](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-04AB64C2-54CD-4581-B48A-7FCF38B31F25.html)

## Developer guide

HPE GreenLake Wellness APIs facilitate the automation of IT operations by enabling you to monitor wellness events related to your infrastructure. These APIs provide various filtering options and KPI metrics to streamline integration workflows further.

### Prerequisites

#### Endpoint

An endpoint is the host URL to which you will submit your API requests.

- [https://global.api.greenlake.hpe.com/](https://global.api.greenlake.hpe.com/)


#### URIs

Unique Resource Identifiers (URIs) identify a server or resource used within the Wellness API. A URI is a full API path ending with a specific endpoint. For example:

- `GET wellness/v2/events`
- `GET wellness/v2/events/{id}`
- `PATCH wellness/v2/events/{id}`
- `GET wellness/v2/support-cases`
- `POST wellness/v2/support-cases`
- `GET wellness/v2/support-cases/{id}`
- `GET wellness/v2/async-operations`
- `GET wellness/v2/async-operations/{id}`


#### Access and permissions

A user permission `ccs.wellness-dashboard.view` is required to make all API calls.

#### Generating a token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens as authorization bearer tokens. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

#### Get a list of wellness events

Retrieve a list of events organized in descending order based on their creation time.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/wellness/v2/events
```

A successful response returns:

- `items`—List of wellness events.
- `count`—Number of wellness events in the response.
- `next`—UUID of the next wellness event to be used as pagination cursor.
- `total`—Total number of wellness events for the given filters.


The following is an example response:


```json
{
    "items": [
        {
          "id": "0001b67f-9518-4d0f-9b17-70cec7763632",
          "type": "wellness/event",
          "resourceUri": "/wellness/v2/events/0001b67f-9518-4d0f-9b17-70cec7763632",
          "title": "Potential increase in the frequency of reboots on Gen 9 Servers",
          "description": {
            "mediaType": "text/plain",
            "content": "Potential increase in the frequency of reboots on Gen 9 Servers"
          },
          "asset": {
            "name": "SRBACKUP01ILO.jansen.local",
            "serialNumber": "CZ31512367G"
          },
          "condition": {
            "urn": "urn:proliant:Potential increase in the frequency of reboots on Gen 9 Servers",
            "severity": "notice",
            "name": "Potential increase in the frequency of reboots on Gen 9 Servers",
            "category": "Firmware/Drivers"
          },
          "status": {
            "currentState": "open"
          },
          "causes": [
            {
              "title": "<p>The system experienced an unexpected reset or shutdown with no errors logged.</p>"
            }
          ],
          "supportCase": {
            "id": "73695013",
            "caseNumber": "29160",
            "status": "open",
            "resourceUri": "/wellness/v2/support-cases/73695013",
            "user": "sample-user@gmail.com",
            "crm": "salesforce",
            "createdAt": "2023-01-27T18:17:37.607Z",
            "updatedAt": "2023-01-29T23:37:37.607Z",
            "generation": 2
          },
          "createdAt": "2023-01-27T18:17:37.607Z",
          "updatedAt": "2023-01-28T18:17:37.607Z",
          "generation": 2,
          "supportCaseCreationOpUri": "/wellness/v2/async-operations/78e32b66-ba3d-4723-b1d6-f48f8bf0dc47",
          "region": "us-east",
          "serviceManager": {
            "id": "0001b67f-9518-4d0f-9b17-70cec7763632",
            "resourceUri": "/wellness/v2/service-managers/0001b67f-9518-4d0f-9b17-70cec7763632"
          }
        }
    ],
    "count": 1,
    "next": "0001b67f-9518-4d0f-9b17-70cec7763632",
    "total": 300
}
```

Query parameters:

| Query parameter | Description |
|  --- | --- |
| Filter | Use the `filter` query parameter to narrow down the results returned by the GET a list of wellness events API. Read more in the filtering section or see examples of [filtering GET wellness/v2/events](#filtering-get-wellnessv2events). |
| Limit | Use `limit` to control the number of records fetched. The `limit` must be a positive integer between 1 and 200. A default of `100` is applied if no value is specified. For example, the following query parameter fetches 120 events: `/events?limit=120`. |
| Next | The next parameter represents the UUID of an event used as a pagination cursor to retrieve the next set of records. This must be a valid UUID and be a part of the response to the previous request. For example, `/events?next=00000010-7e93-4046-9adc-1397cd6ab2d1`. |
| Select | Use the select query parameter to limit the properties returned for a resource. The API only supports `total`. `total` returns a count of wellness events for a given set of filters, for example, `/events?select=total`. |
| text-search | Use the `text-search` query parameter to narrow down and retrieve only those wellness events that contain the specified search term. For example, `/events?text-search='HPE Alletra 500'`. |


Error responses:

For details, refer to the [API Error Response](#api-error-response) section.

#### Get a wellness event

Retrieve an event identified by the given ID. Only the attributes `flag`, `read`, and `archive` are supported.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/wellness/v2/events/{id}
```

A successful response returns a wellness event object. An example response follows:


```json
{
  "id": "0001b67f-9518-4d0f-9b17-70cec7763632",
  "type": "wellness/event",
  "resourceUri": "/wellness/v2/events/0001b67f-9518-4d0f-9b17-70cec7763632",
  "title": "Potential increase in the frequency of reboots on Gen 9 Servers",
  "description": {
    "mediaType": "text/plain",
    "content": "Potential increase in the frequency of reboots on Gen 9 Servers"
  },
  "asset": {
    "name": "SRBACKUP01ILO.jansen.local",
    "serialNumber": "CZ31512367G"
  },
  "condition": {
    "urn": "urn:proliant:Potential increase in the frequency of reboots on Gen 9 Servers",
    "severity": "notice",
    "name": "Potential increase in the frequency of reboots on Gen 9 Servers",
    "category": "Firmware/Drivers"
  },
  "status": {
    "currentState": "open"
  },
  "causes": [
    {
      "title": "<p>The system experienced an unexpected reset or shutdown with no errors logged.</p>"
    }
  ],
  "supportCase": {
    "id": "73695013",
    "caseNumber": "29160",
    "type": "wellness/support-case",
    "resourceUri": "/wellness/v2/support-cases/73695013",
    "createdAt": "2023-01-27T18:17:37.607Z",
    "updatedAt": "2024-01-09T23:37:37.607Z",
    "generation": 1
  },
  "createdAt": "2023-01-27T18:17:37.607Z",
  "updatedAt": "0001-01-01T00:00:00Z",
  "generation": 0,
  "supportCaseCreationOpUri": "/wellness/v2/async-operations/78e32b66-ba3d-4723-b1d6-f48f8bf0dc47",
  "flag": true,
  "read": true,
  "region": "us-east",
  "serviceManager": {
    "id": "0001b67f-9518-4d0f-9b17-70cec7763632",
    "resourceUri": "/wellness/v2/service-managers/0001b67f-9518-4d0f-9b17-70cec7763632"
  }
}
```

Error responses:

For details, refer to the [API Error Response](#api-error-response) section.

#### Update a wellness event

Update specific attributes of a wellness event identified by the given ID.

The endpoint:


```sh
PATCH https://global.api.greenlake.hpe.com/wellness/v2/events/{id}
```

Examples of valid request payloads:

- Request payload to mark a wellness event as flagged:



```json
{
  "flag": true
}
```

- Request payload to mark a wellness event as read:



```json
{
  "read": true
}
```

- Request payload to mark a wellness event as flagged and read but not archived:



```json
{
  "flag": true,
  "read": true,
  "archive": false
}
```

A successful response returns the following fields:

- `resourceUri`
- `id` of the given wellness event.
- `status` of the update operation.


Sample response follows:


```json
{
  "event": {
    "resourceUri": "/wellness/v2/events/00000010-7e93-4046-9adc-1397cd6ab2d1",
    "id": "00000010-7e93-4046-9adc-1397cd6ab2d1"
  },
  "success": true
}
```

Error responses:

For details, refer to the [API Error Response](#api-error-response) section.

#### Asynchronous operations

Support case creation requests are asynchronous operations in the wellness service. Asynchronous operations do not return information immediately. Initially, a successful API returns `202 Accepted`, and an asynchronous operation resource is created to represent the operation's progress. A resource URI is returned in the `Location` header in the response. You can use the URI to poll the asynchronous operation endpoint at the interval specified in the resource.

- List all async-operation resources.



```sh request
/wellness/v2/async-operations
```

- Get an async-operation resource by ID.



```sh request
/wellness/v2/async-operations/a1639bae-b060-4d15-85da-a9b51e84a266
```

The GET `wellness/v2/async-operations` supports the following filter parameters:

- `state`
- `createdAt`
- `updatedAt`
- `startedAt`
- `endedAt`


### Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

#### Filtering example

In this example of filtering, the query's resources are limited to results with the attribute flag and the value true. Within the filter, the separator is a Space.

#### Filtering on a single property


```sh
filter = <propertyName> <comparison operation> <literal>
```

`GET <URI>?filter=flag eq true`

**Property** is the name of an attribute in the requested resource type, for example, flag. The property name is always to the left of the operation. Specify nested property names with the `/` separator.

**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

Examples of operations:

| Operation | Example | Description |
|  --- | --- | --- |
| eq | `flag eq true` | Flag equals true |
| ne | `casenumber ne '1’` | Casenumber not equal to 1 |
| gt | `createdAt gt 2021-05-12T07:20:00.00Z` | Resource created after 2021-05-12T07:20:00.00Z |
| lt | `createdAt lt 2021-05-12T07:20:00.00Z` | Resource created before 2021-05-12T07:20:00.00Z |
| in | `casenumber in [3,4,5]` | Casenumber must equal one of the literals 3,4,5 |


Special case operations:

| Operation | Example | Description |
|  --- | --- | --- |
| in | `3 in casenumber` | Retrieves case numbers that contain the value 3. |


A **Function** can be used to extract information. A function is a block of reusable code that performs a single action. You pass a value into the function, which returns a value. These functions can be used in a filter:

| Function | Example | Description |
|  --- | --- | --- |
| Contains | `contains(caseNumber, '523')` | Checks if a string value is inside the source string, in this example, `'523'`. |
| EndsWith | `endswith(productName, 'test')` | Assesses if a string value ends with the characters of a specified string, in this example, `'test'`. |
| StartsWith | `startswith(productName, 'test')` | Assesses if a string value begins with the characters of a specified string, in this example, `'test'`. |


#### Filtering on multiple properties

Logical operations facilitate filtering using multiple queries. Combine multiple operations using the operator `and`, for example:

**Require both (and):** `caseNumber eq '123' and productName eq 'test'`

#### Filtering GET wellness/v2/events

The `GET` `wellness/v2/events` supports the following filter parameters:

- `condition/severity`
- `status/currentState`
- `supportCase/caseNumber`
- `asset/serialNumber`
- `productName`
- `serviceName`
- `region`
- `serviceManager/id`
- `flag`
- `archive`
- `read`
- `createdAt`
- `updatedAt`
- Filter with the severity of the condition.



```sh request
/events?filter=condition/severity eq 'warning'
```

- Filter with the serial number of the asset.



```sh request
/events?filter=asset/serialNumber eq 'CZ31512367G'
```

- Filter with product.



```sh request
/events?filter=productName eq 'HPE Alletra 9000'
```

- Filter with multiple services.



```sh request
/events?filter=serviceName in ('Storage', 'Networking')
```

- Filter with flag.



```sh request
/events?filter=flag eq true
```

- Filter with archive.



```sh request
/events?filter=archive ne true
```

- Filter with case number of the support case.



```http request
/events?filter=contains(supportCase/caseNumber, '523')
```

- Filter with timestamp (less than).



```sh request
/events?filter=createdAt lt 2021-05-12T07:20:00.00Z
```

- Filter with timestamp (between).



```sh request
/events?filter=createdAt gt 2021-05-12T07:20:00.00Z and createdAt lt 2022-05-12T07:20:00.00Z
```

- Filter with the severity of the condition and product.



```sh request
/events?filter=condition/severity eq 'warning' and productName eq 'HPE Alletra 9000'
```

- Filter with Service Manager and Region.



```sh request
/events?filter=region eq 'us-east' and serviceManager/id eq '0001b67f-9518-4d0f-9b17-70cec7763632'
```

#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).

### Error response and response attributes

#### API Error Response

All API errors have a common response format. The information included in an error response:

- `httpStatusCode`—HTTP status code returned by the API, which represents the error category.
- `message`—A human-readable message describing the error.
- `debugId`—A unique identifier that helps to identify the error.
- `errorCode`—A unique machine-friendly but human-readable identifier for the error.


The following is a sample error response when an invalid limit is provided:


```json
{
    "httpStatusCode": 400,
    "message": "Integer value within 1 and 200 is expected for limit query param",
    "debugId": "cml8v1dt4uq2va605780",
    "errorCode": "HPE_GL_WELLNESS_GET_EVENTS_INVALID_LIMIT"
}
```

#### Response Attributes

Any attribute that does not have a value is not returned in the response. For example, if a wellness event does not have a case number, the case number attribute is not returned in the response. Some boolean attributes like wellness event's `flag`, `read`, and `archive` are only returned when their value is set to `true`.