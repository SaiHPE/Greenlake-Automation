---
title: "GET /wellness/v2/events"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/events/getallevents.md"
scraped_at: "2026-06-07T06:16:34.859532+00:00Z"
---

# Get a list of wellness events

Retrieves a list of wellness events, in descending order of creation time so that the most recent events are listed first.
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

Endpoint: GET /wellness/v2/events
Version: v2
Security: Bearer

## Query parameters:

  - `filter` (string)
    The filter query parameter is used to filter a set of resources. The returned set of resources matches the criteria in the filter query parameter. The value of the filter query parameter is a subset of OData V4 filter expressions consisting of simple comparison operations joined by logical operators.

| Class | Supported |
|---|---|
| Types | string, boolean, timestamp |
| Comparison | eq, ne, gt, ge, lt, le, in |
| Logical Expressions | and |
| Functions | contains(), startswith(), endswith() |

The following examples are not an exhaustive list of all possible filtering options.

  - `text-search` (string)
    Searches for wellness events that contain the given search string. A search string can include alphanumeric characters, a space character (Unicode U+0020) or a hyphen (-). Apart from space characters and hyphens, no other special characters are supported. Including an unsupported character might cause inaccurate results. The minimum length of a search string is 2 characters and maximum is 100 characters. When performing a search, it's important to use specific terms. A generic search term may cause the search to timeout.
* title
* condition.category
* condition.name
* condition.severity
* asset.name
* asset.product
* asset.serialNumber
* status.currentStatus
* supportCase.casenumber
* supportCase.casestatus
* serviceName
* productName
__Note:__ You can use both the filter and text-search parameters in the same query. If both are provided, the filter is applied first, and then text-search is performed on the filtered results.

  - `select` (string)
    The select query parameter is used to limit the properties returned for support cases. The value of the select query parameter is a comma separated list of properties. All properties are returned if the select parameter is omitted. __Note:__ Only the total property is supported.

  - `limit` (integer)
    Specifies the number of resources (wellness events) to fetch.

  - `next` (string)
    The next parameter represents the ID of an event used as a pagination cursor to retrieve the next set of wellness events. The parameter must be a valid UUID and be a part of the response of the previous request.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Primary identifier for the wellness event given by the system.

  - `items.type` (string, required)
    The type of the resource.

  - `items.generation` (integer, required)
    Monotonically increasing update counter.

  - `items.createdAt` (string, required)
    Time of wellness event creation.

  - `items.updatedAt` (string, required)
    The last date and time the wellness event was updated.

  - `items.resourceUri` (string)
    URI to the wellness event itself (a self link).

  - `items.title` (string)
    Short description of the wellness event.

  - `items.description` (object)
    Explanation of the wellness event.

  - `items.description.mediaType` (string)
    Specifies the media type of the content.
    Enum: "text/plain", "html"

  - `items.description.content` (string)
    A descriptive explanation of the wellness event.

  - `items.asset` (object)
    The device the wellness event belongs to.

  - `items.asset.name` (string)
    The serial number or name of the asset.

  - `items.asset.serialNumber` (string)
    The serial number of the asset.

  - `items.condition` (object)
    Specifies details about the nature of the wellness event.

  - `items.condition.urn` (string)
    Unique identifier of the condition.

  - `items.condition.severity` (string)
    The severity level of the wellness event.
    Enum: "critical", "warning", "notice"

  - `items.condition.name` (string)
    Human-readable name given to the condition.

  - `items.condition.category` (string)
    The category the condition belongs to.

  - `items.status` (object)
    Current status of the wellness event.

  - `items.status.currentState` (string)
    The current status. It is the most recent computed state for the event.
    Enum: "open", "resolved", "timeoutCaseCreation", "pendingCaseCreation", "pendingEscalation", "escalated", "correlated", "acknowledged", "expired", "error"

  - `items.status.correlatedTo` (array)
    List of wellness events correlated to this wellness event.

  - `items.causes` (array)
    A list of possible root causes for the event condition.

  - `items.causes.title` (string)
    One sentence summary of potential cause.

  - `items.causes.confidence` (integer)
    Confidence score for this cause.

  - `items.causes.visibility` (string)
    A visibility filter. Null or absent implies universally visible.

  - `items.causes.recommendation` (string)
    A recommended action to resolve the wellness condition.

  - `items.supportCase` (object)
    Support case object.

  - `items.supportCase.id` (string, required)
    Unique identifier of the case.

  - `items.supportCase.generation` (integer, required)
    Monotonically increasing update counter to track the support case version.

  - `items.supportCase.createdAt` (string, required)
    The date and time of support case creation.

  - `items.supportCase.updatedAt` (string, required)
    The last date and time the support case was updated.

  - `items.supportCase.resourceUri` (string)
    URI to the support case.

  - `items.supportCase.caseNumber` (string)
    The case number assigned to the support case.

  - `items.supportCase.event` (object)
    Reference to the wellness event.

  - `items.supportCase.event.resourceUri` (string, required)
    URI to the wellness event

  - `items.supportCase.event.id` (string, required)
    Unique ID of the the wellness event

  - `items.supportCase.user` (string)
    The first and last name of the user that escalated the wellness event. Only relevant to manually escalated cases.

  - `items.supportCase.crm` (string)
    The customer relationship management (CRM) system used to create the support case.

  - `items.supportCase.status` (string)
    The current status of the support case.
    Enum: "open", "closed", "escalated", "correlated", "acknowledged", "resolved", "expired", "error"

  - `items.supportCase.caseHistory` (array)
    Case update history.

  - `items.supportCase.caseHistory.action` (string)
    The type of case update, for example, Case Opened and Updated.

  - `items.supportCase.caseHistory.timeStamp` (string)
    Date and time representing when the support case update occurred.

  - `items.supportCase.source` (string)
    Indicates how the support case was created.
    Enum: "manual", "auto"

  - `items.supportCase.details` (object)
    Curated details for manually created support cases. Only present when source is manual.

  - `items.supportCase.details.category` (string)
    The primary help category, for example, "Backup and Recovery".

  - `items.supportCase.details.subcategory` (string)
    The sub-category selection, displayed as a breadcrumb when multiple sub-categories apply. For example, "Disaster Recovery > Data Protection".

  - `items.supportCase.details.description` (string)
    The user-provided issue description.

  - `items.supportCase.details.priority` (object)
    Case priority.

  - `items.supportCase.details.priority.label` (string)
    The human-readable priority label, for example, "Critical".

  - `items.supportCase.details.priority.value` (string)
    The priority code, for example, "P1".

  - `items.supportCase.details.outage` (boolean)
    A boolean that declares whether an outage has occurred.

  - `items.supportCase.details.primaryContact` (object)
    Primary contact for the case.

  - `items.supportCase.details.primaryContact.name` (string)
    The full name of the contact person.

  - `items.supportCase.details.primaryContact.email` (string)
    Contact email address.

  - `items.supportCase.details.primaryContact.phone` (string)
    The phone number of the contact.

  - `items.supportCase.details.primaryContact.preferredContactMethod` (object)
    Specifies how the contact prefers to be reached. Contains the label and type.

  - `items.supportCase.details.primaryContact.preferredContactMethod.label` (string)
    The human-readable label, for example, "Email".

  - `items.supportCase.details.primaryContact.preferredContactMethod.type` (string)
    The contact method type, for example, "email" or "phone".

  - `items.supportCase.details.alternateContact` (object)
    Alternate contact for the case. Only present when an alternate contact was provided during case creation.

  - `items.supportCase.details.accountName` (string)
    Account name associated with the case.

  - `items.supportCase.details.serialNumber` (string)
    Serial number of the device associated with the case.

  - `items.supportCase.details.subscriptionKey` (string)
    License key that activates the device subscription.

  - `items.supportCase.details.orderNumber` (string)
    Purchase order number associated with the device or subscription.

  - `items.supportCase.details.hasAttachments` (boolean)
    Indicates whether the case includes file attachments. Set to true if one or more files are attached.

  - `items.correlated` (boolean)
    Specifies if this wellness event is related to another wellness event or not.

  - `items.serviceName` (string)
    The name of the service to which this event belongs.

  - `items.productName` (string)
    The name of the product to which this event belongs.

  - `items.flag` (boolean)
    Specifies if the wellness event has been flagged or not.

  - `items.read` (boolean)
    Specifies if the wellness event has been read or not.

  - `items.archive` (boolean)
    Specifies if the wellness event has been archived or not.

  - `items.supportCaseCreationOpUri` (string)
    URI to get details of the support case creation operation.

  - `items.serviceManager` (object)
    Reference to the service manager (application) of the device that generated this wellness event.

  - `items.serviceManager.resourceUri` (string, required)
    URI to the service manager (application) of the device that generated this wellness event.

  - `items.serviceManager.id` (string, required)
    Unique ID of the service manager (application) of the device that generated this wellness event.

  - `items.region` (string)
    The region of the device to which the wellness event belongs.

  - `count` (integer, required)
    Number of items (wellness events) returned.

  - `next` (string, required)
    The event ID acts as the pagination cursor for the next page of resources.

  - `total` (integer, required)
    Total number of items (wellness events) for the current filter criteria.

## Response 400 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 401 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 422 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code

## Response 500 fields (application/json):

  - `errorCode` (string, required)
    A unique machine-friendly, but human-readable identifier for the error

  - `message` (string, required)
    User-friendly error message

  - `debugId` (string, required)
    Unique identifier for the instance of this error

  - `httpStatusCode` (integer, required)
    HTTP equivalent status code


## Response 429 fields
