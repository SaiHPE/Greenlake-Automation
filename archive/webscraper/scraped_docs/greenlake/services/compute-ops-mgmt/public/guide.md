---
title: "HPE Compute Ops Management Developer Guide"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/compute-ops-mgmt/public/guide.md"
scraped_at: "2026-06-07T06:13:25.837723+00:00Z"
---

# HPE Compute Ops Management Developer Guide

The examples in this guide help you get started using the Compute Ops Management API to do common tasks.

## Prerequisites

### Endpoints

Endpoints are the host URLs that you will submit your API requests to. Compute Ops Management has unique endpoints in specific regions.
Use the following list to identify your application endpoint.

- US West: [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com)
- EU Central: [https://eu-central.api.greenlake.hpe.com](https://eu-central.api.greenlake.hpe.com)
- AP NorthEast: [https://ap-northeast.api.greenlake.hpe.com](https://ap-northeast.api.greenlake.hpe.com)


#### Endpoint changes

Compute Ops Management now supports the HPE GreenLake API endpoints `<region>.api.greenlake.hpe.com`. This change was made to
align with other HPE GreenLake services.

### URIs

Unique Resource Identifiers (URIs) are used to identify a server or resource used within the Compute Ops Management application.
A URI is a full API path ending in an identification number. For example:

- `/compute-ops-mgmt/v1beta1/servers/{serverId}`
- `/compute-ops-mgmt/v1beta1/groups/{groupId}`


URI path prefix rename
Compute Ops Management is completing the process of renaming the URI path prefix from `/compute-ops` to `/compute-ops-mgmt`.
The `/compute-ops` prefix is deprecated and might become unresponsive after Tuesday, April 1, 2025. The [next section](#uri-path-prefix-rename)
provides more information about this change.

### Configuring API client credentials

To configure API client credentials to use an API with Compute Ops Management, see the
[HPE GreenLake access token instructions](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client).

## URI path prefix rename

Compute Ops Management is completing the process of renaming the URI path prefix from `/compute-ops` to `/compute-ops-mgmt` for
all API endpoints. Each API endpoint will clearly indicate if one or both of the URI path prefixes are supported. This change
was made to align with the HPE GreenLake API gateway (see [Endpoint changes](#endpoint-changes)).

### Deprecation and sunset

HPE recommends transitioning to the new URI path prefix as soon as possible. The `/compute-ops` prefix is deprecated and
might become unresponsive after Tuesday, April 1, 2025.

### Breaking changes

There are some breaking changes to the response for API endpoints with new URI `/compute-ops-mgmt` prefix. The `resourceUri` and
`type` properties were updated to reflect the new URI path prefix.

Calling the old API endpoint `GET /compute-ops/v1beta1/servers/875765-S01+1M512501AB`, the response will be:


```json
{
  "resourceUri": "/compute-ops/v1beta1/servers/875765-S01+1M512501AB",
  "type": "compute-ops/server",
  "name": "server1",
  "...": "..."
}
```

Calling the new API endpoint `GET /compute-ops-mgmt/v1beta1/servers/875765-S01+1M512501AB`, the response will be:


```json
{
  "resourceUri": "/compute-ops-mgmt/v1beta1/servers/875765-S01+1M512501AB",
  "type": "compute-ops-mgmt/server",
  "name": "server1",
  "...": "..."
}
```

## Making It All Work

### Obtain the list of servers in your account

Without knowing specific server identifiers, you can use the following command to list all the servers assigned to your account:


```curl
GET https://us-west.api.greenlake.hpe.com/compute-ops-mgmt/v1beta1/servers
```

The endpoint [https://us-west.api.greenlake.hpe.com](https://us-west.api.greenlake.hpe.com) is the endpoint for the US West application. If you are using Compute Ops Management in a different region, replace with the endpoint for that region.

Information included in the response:

- resourceUri: Uri for the server. This is needed to invoke other actions on the server.
- Current health state
- Hardware status
- Firmware inventory
- Network information
- and more


### Obtain the list of firmware bundles

Firmware bundles are the firmware collections for the components that comprise an HPE server. They are required to upgrade your server firmware. To obtain a list of available firmware bundles, submit the following request:


```curl
GET https://us-west.api.greenlake.hpe.com/compute-ops-mgmt/v1beta1/firmware-bundles
```

Generally, the most recent bundle is used to conduct an upgrade.
Information included in the response:

- Firmware bundle name
- Resource URI: needed to utilize the firmware bundle in an update
- Created at timestamp
- Supported OS list
- Firmware bundle support status
- and more


### Obtain the list of job templates

Job templates are predefined sets of tasks that enables you to perform various server actions. Possible actions include power-on, power-off, and firmware update. To obtain a list of available job templates, submit the following request:


```curl
GET https://us-west.api.greenlake.hpe.com/compute-ops-mgmt/v1beta1/job-templates
```

Information included in the response:

- descriptive job template name
- description: text description of the action provided by this template
- id - the job template identifier that is needed to create a job of this type


### Perform a firmware download

A firmware download uses information from the previous API calls. To perform a firmware download, you need the server URI, the firmware bundle URI, and the firmware download job template URI. The API call to invoke a firmware download is a POST to the 'jobs' resource to create a job for the download. To start a firmware download, submit:


```curl
POST https://us-west.api.greenlake.hpe.com/compute-ops-mgmt/v1beta1/jobs
```

Payload:


```json
{
  "jobTemplateUri": "{job-template Uri for firmware-download}",
  "resourceUri": "{server to download Uri}",
  "data": {
    "bundle_id": "{firmware-bundle Id}"
  }
}
```

### Perform a firmware update

A firmware update uses information from the previous API calls. To perform a firmware update, you need the server URI, the firmware bundle URI, and the firmware update job template URI. The firmware update can be performed either on previously downloaded firmware or as a new update that automatically downloads and updates the firmware in one operation. The API call to invoke a firmware update is a POST to the 'jobs' resource to create a job for the update. To start a firmware update, submit:


```curl
POST https://us-west.api.greenlake.hpe.com/compute-ops-mgmt/v1beta1/jobs
```

Payload:


```json
{
  "jobTemplateUri": "{job-template Uri for firmware-update}",
  "resourceUri": "{server to update Uri}",
  "data": {
    "bundle_id": "{firmware-bundle Id}"
  }
}
```

## Filtering

Filters provide the ability to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET or DELETE action is restricted to a response that meets the filter requirements. Filters are specified by using the query parameter 'filter'.

### A simple example

A simple example of filtering follows:


```curl
GET <URI>?filter=powerState eq 'Off'
```

This example shows a simple filter. The resources returned by the query are limited to results with the attribute powerState and the value Off. Note that within the filter, the separator is a space ' '.


```curl
filter = <propertyName> <comparison operation> <literal>
```

### Filtering Primitives

The filter query syntax supports a richer set of filters than the single operation in the previous example. Filtering syntax is broken down by Operations, Logic, and Types. In the previous example the operation was 'eq' for equality. Most comparison operations require the evaluated property name to the left of the operator, and a literal to the right.

| CLASS | EXAMPLES |
|  --- | --- |
| Comparison Operations | eq, ne, gt, ge, lt, le, in, contains() |
| Modifying Operations | toupper(), tolower() |
| Nesting separator | / |
| Data types | integer, decimal, timestamp, string, boolean, null |
| Logic and grouping | (), not, and, or |


### Filtering on a single property


```curl
filter = <property> <operation> <literal>
```

**Property** is the name of an attribute in the requested resource type. The property name is always to the left of the Operation. Nested property names can be specified with the '/' separator.

- topLevelProperty
- topLevelProperty/2ndLevelProperty
- topLevelProperty/2ndLevelProperty/3rdLevelProperty


**Operation** evaluated. All parameters except 'in' require the property on the left and literal on the right. The 'in' parameter allows the property on either side.:

- **eq**: `age eq 3`: age equals 3
- **ne**: `age ne 3`: age does not equal 3
- **gt**: `age gt 3`: age is greater than 3
- **ge**: `age ge 3`: age is greater than or equal to 3
- **lt**: `age lt 3`: age is less than 3
- **le**: `age le 3`: age is less than or equal to 3
- **in**: `age in [3,4,5]`: age must equal one of the literals 3,4,5


-special case operations-

- **in**: `3 in childAges`: childAges must be a collection that must contain the value 3
  - In's 2nd form. Primitive on the left. Attribute w/ collection of values on the right.
- **contains(property,literal)**: `contains(name,'ob')`: name must have substring 'ob'
  - Matches strings containing 'ob' such as: Robin, Roberta, Bob, Koby
- **toupper(property)**: `toupper(name) eq 'ROBIN'`: name is case insensitive of robin
  - Converts to uppercase string for case insensitivity
- **tolower(property)**: `tolower(name) eq 'robin'`: name is case insensitive of robin
  - Converts to lowercase string for case insensitivity


**Literal** the property is to be compared against. Operations compare properties against literals. For a successful matching operation, the types must match and the syntax determines the type of the literals. The filter `(age eq '3')` would not work if age is an integer, and `(age eq 3)` would not work if age is a string.
Due to [URL encoding](https://en.wikipedia.org/wiki/URL_encoding), reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` in string literals must be replaced with percent encoded equivalents. Server Ids contain `+` which must be replaced with `%2B`. For example: `id eq P06760-B21+2M212504P8'` becomes `id eq 'P06760-B21%2B2M212504P8'`, if the query must be fully encoded it would become `id%20eq%20%27P06760-B21%2B2M212504P8%27`.

The following examples show typed literals.

- **String**: 'anything in single quotes'
  - Reserved characters in string literals must be URL encoded.
- **Integer**: -100,-1,0,1,100
- **Decimal**: -3.14,-2.71,2.71,3.14
- **Timestamp**: 2019-10-12T07:20:50.52934852Z
  - The timestamp format is [RFC3339](https://datatracker.ietf.org/doc/html/rfc3339)
- **Boolean**: true, false
- **Null**: null.
  - Null is equal to itself and nothing else. Null is not greater or less than anything.


### Composite Filtering on multiple properties

The previous section explained queries for filtering on a single property, the logical operations enable more elaborate filtering using multiple queries.
The complement of any operation can be specified with the 'not' operator before it. Multiple operations can be combined using the operators 'and' & 'or'. The precedence of operations had 'not' bind first, then 'and', and finally 'or'. Operations can be grouped and the order of evaluation changed with parenthesis '()'. The full order of operations is { (), not, and, or }.
In each case if multiple operations apply to a term, they will be applied in order of precedence.

**Examples** with precedence.

- **Require both (and)**: `tolower(name) eq 'robin' and age eq 3`
- **Require either (or)**: `tolower(name) eq 'robin' or age eq 3`
- **Require 1st but (not) 2nd**: `name eq 'robin' and not age eq 3`
- **Precedence**: `name eq 'Robin' or not age in [3,4,5] and (height gt 2 or eyeColor eq 'brown' )`
  1. **()**parentheses are evaluated first. So this is first even though **or** is lowest precedence: **(** `height gt 2` **or** `eyeColor eq 'brown'` **)**
  2. **not** is evaluated next. So this is next: **not** `age in [3,4,5]`
  3. **and** is evaluated next. So this is next: `<result of step2>` **and** `<result of step1>`
  4. **or** is last. So `name eq 'Robin'` **or** `<result of step3>` is last.


### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).

## Data Availability Rules

Data returned by the API is subject to the Compute Ops Management data availability rules. For more information, see the [Compute Ops Management Data availability section](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00004003en_us&docLocale=en_US&page=GUID-B5BD0A50-799E-4600-A45D-34543D93F60E.html) in the Compute Ops Management user guide.