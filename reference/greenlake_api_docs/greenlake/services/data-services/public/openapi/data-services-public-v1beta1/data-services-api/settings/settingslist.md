---
title: "GET /data-services/v1beta1/settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/data-services/public/openapi/data-services-public-v1beta1/data-services-api/settings/settingslist.md"
scraped_at: "2026-06-07T06:15:17.196259+00:00Z"
---

# List settings for the current account.

Returns all settings values for the current account

Endpoint: GET /data-services/v1beta1/settings
Version: 1.3.0
Security: bearer

## Query parameters:

  - `offset` (integer)
    Use offset in conjunction with limit for paging. The offset is the number of items from the beginning of the result set to the first item included in the response.

  - `limit` (integer)
    Use limit in conjunction with offset for paging. The limit is the maximum number of items to include in the response.

  - `filter` (string)
    The expression to use for filtering responses. You can filter on the following properties: customerId, id, name, possibleValues, currentValue, settingDescription, lastUpdatedBy, lastUpdatedAt, externalApplicationName. You can combine multiple comparison operators using AND. The comparisons supported are the following:
“eq” : Valid for number, boolean and string properties.
“gt” : Valid for number or string timestamp properties.
“lt” :  Valid for number or string timestamp properties
“in” : Valid for an array of strings
Syntax:
“eq” : filter=\ eq \ {host:port}/data-services/v1beta1/settings?filter=\ eq \
“gt” : filter=\ gt \ {host:port}/data-services/v1beta1/settings?filter=\ gt \
“lt” : filter=\ lt \ {host:port}/data-services/v1beta1/settings?filter=\ lt \
“in” : filter=\ in \ {host:port}/data-services/v1beta1/settings?filter=\ in \
* Use AND to filter on multiple properties: {host:port}/data-services/v1beta1/settings?filter=\ eq \ and \ lt \
* To filter multiple values on one property e.g. filter=name in ('foo','bar') {host:port}/data-services/v1beta1/settings?filter=foo%bar%20in%20severity
Examples:
GET /data-services/v1beta1/settings?filter=name eq 'SETTINGNAME'
GET /data-services/v1beta1/settings?filter=name eq 'SETTINGNAME' and lastUpdatedBy eq 'CREATED'
GET /data-services/v1beta1/settings?filter=relatedObjectType in ('NIMBLE-VOLUME')
Filters are supported on following attributes:
customerId,
id,
name,
possibleValues,
currentValue,
settingDescription,
lastUpdatedBy,
lastUpdatedAt,
externalApplicationName

  - `sort` (string)
    The property to sort by followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified the default order is ascending.

  - `select` (string)
    A comma-separated list of properties to include in response. If this is omitted, all properties are returned.

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

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

  - `items.consoleUri` (string)
    The URI for console screen that displays this resource

  - `items.currentValue` (string)
    Value of the setting

  - `items.description` (string)
    Description of the setting

  - `items.externalApplicationName` (string)
    Name of the application to be displayed in UI

  - `items.lastUpdatedAt` (string)
    Time when this setting was last updated for this account. RFC 3339

  - `items.lastUpdatedBy` (string)
    UserId of the user who last updated this setting for this account

  - `items.nextValue` (string)
    Next possible value of the setting, which is updated by the workflow

  - `items.possibleValues` (string)
    A JSON array (stored as string) containing possible values of this setting

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


