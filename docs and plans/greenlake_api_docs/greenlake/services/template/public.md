---
title: "HPE GreenLake for {Service Name}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/template/public.md"
scraped_at: "2026-06-07T05:46:15.818822+00:00Z"
---

# HPE GreenLake for {Service Name}

{This is a template for creating API documentation for HPE GreenLake services. Follow these guidelines when filling out this template:

PLACEHOLDER REPLACEMENT RULES:

- {Service Name} → Use the API title
- {api_base_url} → Use the actual base URL from the servers section
- {endpoint} → Use actual endpoint paths from the paths section
- {property_name} → Use actual property names from schema definitions
- {example_value} → Use realistic values based on the property types and descriptions. If example are provided in the reference, use those.
- {YYYY-MM-DD} → Use current date or most recent API version date


CONTENT QUALITY STANDARDS:

- Write clear, concise descriptions that help developers understand the API's purpose
- Include realistic code examples with actual parameter values
- Ensure all HTTP methods, endpoints, and response formats match the API specification
- Use consistent formatting and follow the existing structure
- If the API doesn't support certain features (like filtering), omit those sections entirely


SECTION-SPECIFIC GUIDANCE:

- Overview: Focus on what the API does and who would use it
- Features: List concrete capabilities, not generic statements
- Use cases: Provide specific scenarios where customers would use this API
- Making it all work: Choose examples that demonstrate real workflows
- Filtering: Only include if the API actually supports OData-style filtering


VALIDATION CHECKLIST:

- All placeholders replaced with actual content
- All instructional text removed
- Code examples use correct endpoints and realistic data
- No references to "example" or placeholder values in final content
- Formatting follows markdown best practices
- Writing reviewed to adhere to HPE writing style guide.


}

This page provides an introduction and quick start guide for the {Service name} API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

{Write a one to three-paragraph introduction describing what the API does, its audience, and how it fits into the GreenLake ecosystem.}

### Features

{List up to a maximum of eight key features of the API. Each feature should be a single bullet point.}

### Use cases

{List one to three realistic scenarios where a customer would use this API. Use bold for scenario titles.}

### What's new

Date: {YYYY-MM-DD}

{Summarize the most recent significant API change in a paragraph or bullet list.}

[View the changelog for more information](/docs/greenlake/services/template/public/openapi/changelog)

#### Deprecated

{If applicable, list deprecated APIs in a table. The preferred format is :

| API | Deprecated endpoint | Deprecation date | Replacement endpoint |
|  --- | --- | --- | --- |
| {Name of the endpoint} | `GET example/v2beta2/example` | 2024-12-19 | `GET example/v2/example` |


Otherwise, state "No endpoints are currently scheduled for deprecation." }

### Related documentation

- [HPE GreenLake cloud](https://www.hpe.com/ie/en/greenlake.html)
- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-8E53E955-6C1F-4006-8923-B06CA5E727A8.html)


## Developer guide

{Briefly describe what this section covers.}

### Prerequisites

- {List all prerequisites as bullet points.}


#### Hostname

- {Insert unified endpoint}


#### URIs

- {List example URIs for the API.}


#### Access and permissions

| Endpoint | Permission | Resource |
|  --- | --- | --- |
| `GET {endpoint}` | View | {resource} |
| ... | ... | ... |


:::info
Learn more about configuring roles and permissions in the [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-FF77BFEC-79AB-4FBC-8684-FADB9FAE138A.html).
:::

#### Rate limits

| Description | HTTP method and path | Limit |
|  --- | --- | --- |
| {Name of the endpoint} | `POST /example/v1alpha1/example` | {number} request per {time unit} |
| {Name of the endpoint} | `GET /example/v1alpha1/example` | {number} requests per {time unit} |
| {Name of the endpoint} | `GET /example/v1alpha1/example/{Id}` | {number} requests per {time unit} |
| {Name of the endpoint} | `PATCH /example/v1alpha1/example/{Id}` | {number} requests per {time unit} |


#### Getting an access token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#generating-an-access-token)
  - [View code samples for generating an access token.](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication/#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


{Provide a code sample.}

### Making it all work

{Consider the total number of endpoints in the API specification and follow these guidelines:

- If the API has 4 or fewer endpoints you can provide a complete code example for each endpoint
- If the API has more than 4 endpoints: choose one of these approaches:
  1. Create a step-by-step scenario demonstrating a typical workflow (for example, create → retrieve → update → delete)
  2. Provide one representative code example for each HTTP method used (GET, POST, PUT, PATCH, DELETE)
  3. If the API has a dependency on another service or implements or relies on an external standard or technology, the examples should describe these as a priority.


For each endpoint example, include:

- Descriptive heading with the endpoint purpose
- The complete endpoint URL with realistic parameters
- The HTTP method
- Sample request payload (if applicable) with realistic data
- Sample response payload with realistic data
- Brief description of what the example demonstrates
- Any relevant query parameters or special considerations


Use the following format examples as a guide:}

#### {Name of the API endpoint}

{Insert introduction}

Example API call:


```sh
GET '{HOSTNAME}/example/v1alpha1/example
```

Sample API response:


```json
  {
  "items": [
    {
      "id": "COMPUTE1234567",
      "type": "sustainability-insight-ctr/cloud-entities",
      "serviceProvider": "aws",
      "serviceName": "s3",
      "serviceRegion": "us-east",
      "serviceAccount": "123456789012",
      "name": "",
      "co2eMetricTon": 0.6
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
  }
```

{Add a description of the results, including whatever technical information is useful for end users.}

#### {Name of another API endpoint}

{Insert introduction}

Example API call:


```sh
GET '{HOSTNAME}/example/v1alpha1/example
```

Sample API response:


```json
  {
  "items": [
    {
      "id": "COMPUTE1234567",
      "type": "sustainability-insight-ctr/cloud-entities",
      "serviceProvider": "aws",
      "serviceName": "s3",
      "serviceRegion": "us-east",
      "serviceAccount": "123456789012",
      "name": "",
      "co2eMetricTon": 0.6
    }
  ],
  "count": 1,
  "offset": 0,
  "total": 1
  }
```

{Add a description of the results, including whatever technical information is useful for end users.}

### Filtering

{Only include this section if the API supports filtering parameters. If no filtering is available, omit this entire section.}

#### Filtering example

{Provide a realistic filtering example using actual property names from the API specification.}


```bash
GET {api_base_url}/v1/{resource}?filter={property_name} eq {example_value}
```

#### Filtering on a single property


```bash
filter = {property_name} {comparison_operation} {literal_value}
```

{Provide an actual example from the API:}


```bash
GET {api_base_url}/v1/{resource}?filter={property_name} eq {example_value}
```

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the operation. Specify nested property names with the `/` separator.

{Create a table with actual filterable properties from the API specification:}

| **Filter** | **Example** | **Description** |
|  --- | --- | --- |
| {property_name} | `{property_name} eq {example_literal}` | {One to two sentence explanation describing what this property filters.} |
| {property_name} | `{property_name} eq {example_literal}` | {One to two sentence explanation describing what this property filters.} |
| {property_name} | `{property_name} eq {example_literal}` | {One to two sentence explanation describing what this property filters.} |
| {property_name} | `{property_name} eq {example_literal}` | {One to two sentence explanation describing what this property filters.} |
| {property_name} | `{property_name} le {example_literal}` | {One to two sentence explanation describing what this property filters.} |
| {property_name} | `{property_name} in ({example_literal})` | {One to two sentence explanation describing what this property filters.} |


**Operation** evaluated. Operations compare properties against literals, for example, `eq`. All parameters except `in` require the property on the left and the literal on the right. The `in` parameter allows the property on either side.

Examples of operations:

| Operation | Example | Description |
|  --- | --- | --- |
| eq | `{property_name} eq {example_value}` | {Explain what this equality comparison does} |
| ne | `{Property} ne '1’` | {explain the example} |
| gt | `{Property} gt '1’` | {explain the example} |
| ge | `{property_name} ge {example_value}` | {Explain what this greater-than-or-equal comparison does} |
| lt | `{property_name} lt {example_value}` | {Explain what this less-than comparison does} |
| le | `{property_name} le {example_value}` | {Explain what this less-than-or-equal comparison does} |
| in | `{property_name} in [{example_value1},{example_value2},{example_value3}]` | {Explain what this in-list comparison does} |


Special case operations:

| Operation | Example | Description |
|  --- | --- | --- |
| in | `{property_name} in {example_substring}` | Retrieves resources that contain the value {example_substring}. |


A **Function** can be used to extract information. A function is a block of reusable code that performs a single action. You pass a value into the function, which returns a value. These functions can be used in a filter:

| Function | Example | Description |
|  --- | --- | --- |
| Contains | `contains({property_name}, '{example_value}')` | Checks if a string value is inside the source string, in this example, `'{property_name}'`. Returns boolean true or false as appropriate. |
| StartsWith | `startswith({property_name}, '{example_value}')` | Assesses if a string value begins with the characters of a specified string, in this example, `'{example_value}'`. Returns boolean true or false as appropriate. |


A **literal**, for example, true, is what an operation compares a property to. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Due to URL encoding, reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent-encoded equivalents.

The following are examples of literals.

- **String**: Anything in 'single quotes'. Reserved characters in string literals must be URL encoded.
- **Integer**: -100, -1, 0, 1, 100
- **Decimal**: -3.14, -2.71, 2.71, 3.14
- **Timestamp**: 2019-10-12T07:20:50.52934852Z. The timestamp format is [RFC3339]
- **Boolean**: true, false
- **Null**: null. Null is equal to itself and nothing else. Null is not greater or less than anything.


#### Filtering on multiple properties

Logical operations facilitate filtering using multiple queries. Combine multiple operations using the operator `and`, for example:

**Require both (and):** `{property_name1} eq {example_value1} and {property_name2} eq {example_value2}`

#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).