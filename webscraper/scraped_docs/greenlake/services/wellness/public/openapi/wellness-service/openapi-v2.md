---
title: "HPE GreenLake for Wellness"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2.md"
scraped_at: "2026-06-07T05:46:41.407634+00:00Z"
---

# HPE GreenLake for Wellness

The HPE GreenLake for Wellness APIs facilitates the automation of IT operations by enabling you to monitor wellness events related to your infrastructure. To further streamline integration workflows, these APIs provide various filtering options and KPI metrics.

Version: v2
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Personal access token compliant with RFC8725 issued by the HPE GreenLake platform.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake for Wellness](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/wellness/public/openapi/wellness-service/OpenApi-v2.yaml)

## Events

Wellness events provide health insights about your HPE products and services and show information about automatically created support cases. Wellness events allow you to&#58; <ul> <li>Identify potential vulnerabilities before they affect your environment.</li> <li>Proactively monitor the health of your HPE products and services.</li> <li>View AI-powered recommendations about events.</li></ul>

### Get a list of wellness events

 - [GET /wellness/v2/events](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/events/getallevents.md): Retrieves a list of wellness events, in descending order of creation time so that the most recent events are listed first.
__Pagination__&mdash; This endpoint exclusively supports cursor-based pagination, using the next query parameter. __Filtering__&mdash; The following are the supported filter parameters&#58;
* condition/severity
* status/currentState
* supportCase/caseNumber
* asset/serialNumber
* productName
* serviceName
* region
* serviceManager/id 
* flag
* archive
* read
* createdAt
* updatedAt

### Get wellness event with specific ID

 - [GET /wellness/v2/events/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/events/getevent.md): Retrieves a wellness event identified by the given ID.

### Update wellness event with specific ID

 - [PATCH /wellness/v2/events/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/events/updateevent.md): Update a wellness event identified by the given ID. Only the attributes flag, read, and archive can be updated.

## Support Cases

Create and retrieve support cases associated with wellness events.

### Create a support case

 - [POST /wellness/v2/support-cases](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/support-cases/createsupportcase.md): Create a support case for a wellness event. This is an asynchronous operation. Use the URI specified in the Location response header to retrieve the status of the case creation operation.

### Get a list of support cases

 - [GET /wellness/v2/support-cases](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/support-cases/getsupportcases.md): Retrieves a list of support cases associated with wellness events. The results are in descending order of creation time, so that the most recent support cases are listed first.
__Pagination__&#58; This endpoint exclusively supports cursor-based pagination, using the next query parameter. __Filtering__&#58; The following are the supported filter parameters&#58;
Note&#58; Using any details/* filter implicitly limits results to manual cases (source = manual).
* event/id &mdash; The event/id filter parameter only supports the eq operator and its value should be a valid wellness event ID.
* caseNumber
* status
* createdAt
* updatedAt
* source &mdash; How the case was created. Only supports the eq operator. Values&#58; manual, auto.
* details/category &mdash; Primary help category assigned to the case. Only applicable to manual cases.
* details/serialNumber &mdash; Serial number of the device associated with the case. Only applicable to manual cases.
* details/subscriptionKey &mdash; License key for the subscription associated with the case. Only applicable to manual cases.
* details/primaryContact/email &mdash; Email address of the primary contact for the case. Only applicable to manual cases.
* details/alternateContact/email &mdash; Email address of an alternate contact for the case. Only applicable to manual cases.
* event/condition/severity
* event/status/currentState
* event/productName
* event/serviceName
* event/createdAt
* event/updatedAt

### Get support case with specific ID

 - [GET /wellness/v2/support-cases/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/support-cases/getsupportcase.md): Retrieves a support case identified by the given ID.

## Async Operations

Asynchronous APIs are APIs that do not return data immediately. This means you can make multiple requests at once. A high-level overview of the asynchronous API process&#58; <ol><li>You make a request to an asynchronous API endpoint.</li> <li>HPE GreenLake returns an acknowledgment, typically a `202 Accepted`, and provides a URI to the async-operation resource in the `Location` header. <li>HPE GreenLake continues to process the request.</li> <li>When completed, HPE GreenLake returns the requested information.</li></ol>

### Get a list of asynchronous operations

 - [GET /wellness/v2/async-operations](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/async-operations/getallasyncoperations.md): Retrieves a list of all asynchronous operations organized in descending order based on their creation time. This ensures the most recent asynchronous operations are presented first.
__Pagination__&#58; This endpoint exclusively supports cursor-based pagination. __Filtering__&#58; The following are the supported filter parameters&#58;
* state&mdash; The state filter parameter only supports the eq operator and its value should be a valid string.
* createdAt
* updatedAt
* endedAt
* startedAt

### Get asynchronous operation details

 - [GET /wellness/v2/async-operations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/async-operations/getasyncoperation.md): Retrieves asynchronous operation details identified with a specific ID.

