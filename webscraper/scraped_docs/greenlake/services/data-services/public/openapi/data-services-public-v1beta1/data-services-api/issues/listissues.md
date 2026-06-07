---
title: "GET /data-services/v1beta1/issues"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/issues/listissues.md"
scraped_at: "2026-06-07T06:15:16.456659+00:00Z"
---

# List active issues

Returns the list of active issues for the account and user obtained from the request header. The list includes
issues only for the resource-types that the user has permissions to view. Active issues are issues in the CREATED 
state. Clients using this API must process the returned issues for any desired groupings.

Endpoint: GET /data-services/v1beta1/issues
Version: 1.3.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    Use offset in conjunction with limit for paging. The offset is the number of items from the beginning
of the result set to the first item included in the response.

  - `limit` (integer)
    Use limit in conjunction with offset for paging. The limit is the maximum number of items to include in the response.

  - `filter` (string)
    The expression used to filter responses. You can filter on the following properties: issueType, severity, category, state, createdAt, services, 
sourceResourceId, sourceResourceType. You can combine multiple comparison operators using “and”.
The returned set of resources must match the criteria in the filter query parameter
A comparison compares a property name to a literal. The comparisons supported are the following:
“eq” : Is a property equal to value. Valid for number, boolean and string properties.
“gt” : Is a property greater than a value. Valid for number or string timestamp properties.
“lt” : Is a property less than a value. Valid for number or string timestamp properties
“in” : Is a value in a property. The property is an array of number, boolean or string properties.
"contains": Is a substring value that is equal to a portion of the property value. Valid for strings.
Syntax: 
“eq” : filter=\ eq \ {host:port}/data-services/v1beta1/issues?filter=\ eq \
“gt” : filter=\ gt \ {host:port}/data-services/v1beta1/issues?filter=\ gt \
“lt” : filter=\ lt \ {host:port}/data-services/v1beta1/issues?filter=\ lt \
“in” : filter=\ in \ {host:port}/data-services/v1beta1/issues?filter=\ in \
“contains” : filter=contains(property,value) {host:port}/data-services/v1beta1/issues?filter=contains(property,value)
* Can use and to add more filter inputs {host:port}/data-services/v1beta1/issues?filter=\ eq \ and \ lt \ 
* To filter multiple values on one property e.g. filter=severity in ('CRITICAL','WARNING') {host:port}/data-services/v1beta1/issues?filter=severity%20in%20CRITICAL%2CWARNING
Examples:
GET /data-services/v1beta1/issues?filter=issueType eq 'ISSUE'
GET /data-services/v1beta1/issues?filter=issueType eq 'ISSUE' & state eq 'CREATED'
GET /data-services/v1beta1/issues?filter=contains(sourceResourceType,'orchestrator')
GET /data-services/v1beta1/issues?filter='data-ops-manager' in services
Filters are supported on following attributes:
issueType,
severity,
category,
state,
createdAt,
services,
sourceResourceId,
sourceResourceType

  - `sort` (string)
    resource property to sort, with an order appended
Order may only be either “asc” (ascending) or “desc” (descending)
    Example: "/issues?sort=id desc"

  - `select` (string)
    The select query parameter is used to limit the properties returned with a resource or collection-level GET.
Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client.
The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)
    The issues returned by the query.

  - `items.id` (string, required)
    An identifier for the resource, usually a UUID.

  - `items.type` (string, required)
    The type of resource.

  - `items.generation` (integer, required)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.

  - `items.createdAt` (string, required)

  - `items.updatedAt` (string, required)

  - `items.resourceUri` (string, required)
    The self reference for this resource.

  - `items.customerId` (string, required)
    The customer application identifier

  - `items.name` (string)
    A system specified name for the resource.

  - `items.body` (string)
    Long description with more details including possible remediations.

  - `items.category` (string)
    Category of the issue. PERFORMANCE, CAPACITY, etc

  - `items.clearedAt` (string)
    Time when the issue was cleared. RFC 3339 timestamp

  - `items.groups` (array)
    Groups this issue is associated with.

  - `items.groups.id` (string, required)
    ID of the associated group

  - `items.groups.name` (string, required)
    Name of the associated group

  - `items.issueType` (string)
    The type of the issue. Eg: ISSUE

  - `items.lastOccurredAt` (string)
    Time when the issue last occurred. RFC 3339 timestamp

  - `items.occurrenceCount` (integer)
    Indicates the number of occurrences of the issue

  - `items.recommendation` (string)
    Recommendation to address the underlying issue.

  - `items.relatedResources` (array)
    Details of the resources related to the issue

  - `items.relatedResources.type` (string, required)

  - `items.relatedResources.resourceUri` (string, required)

  - `items.relatedResources.id` (string, required)

  - `items.relatedResources.name` (string)

  - `items.relatedResources.consoleUri` (string)
    console URI of the related object resource that is the source of the issue

  - `items.services` (array)
    Details of the services this issue belongs to

  - `items.severity` (string)
    Severity of the issue. For issue: CRITICAL, WARNING, INFO. For reco: HIGH, MEDIUM, LOW

  - `items.snoozed` (boolean)
    An auxiliary calculated attribute to help the end-user filter snoozed and un-snoozed issues

  - `items.snoozedBy` (string)
    The email id of the last user who snoozed this issue.

  - `items.snoozedFor` (string)
    Enum: "NONE", "DAY", "WEEK", "MONTH", "INFINITE"

  - `items.snoozedUntil` (string)
    Date-time until this issue will be considered snoozed/inactive until this time. RFC 3339

  - `items.sourceResourceId` (string)
    Identifier for the source resource that is contained in relatedResources

  - `items.sourceResourceType` (string)
    Type of the source resource that is contained in the relatedResources

  - `items.state` (string)
    State of the issue. Eg: CREATED, ASSIGNED, CLOSED, SNOOZED, DELETED, etc

  - `total` (integer)
    Total number of items matching the filter parameter in the request.

## Response 400 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 401 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 403 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 404 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 405 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 422 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 500 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"

## Response 503 fields (application/json):

  - `httpStatusCode` (integer, required)
    The HTTP status code of the response

  - `message` (string, required)
    A user-friendly error message
    Example: "An example error message"

  - `errorCode` (string, required)
    A machine friendly identifier for the error response

  - `debugId` (string, required)
    A unique identifier for the request
    Example: "f57dcca3345820eb579c9317ce36dd92"


