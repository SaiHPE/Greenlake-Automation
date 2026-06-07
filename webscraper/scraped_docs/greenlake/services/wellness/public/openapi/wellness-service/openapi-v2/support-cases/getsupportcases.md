---
title: "GET /wellness/v2/support-cases"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/support-cases/getsupportcases.md"
scraped_at: "2026-06-07T06:16:34.010143+00:00Z"
---

# Get a list of support cases

Retrieves a list of support cases associated with wellness events. The results are in descending order of creation time, so that the most recent support cases are listed first.
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

Endpoint: GET /wellness/v2/support-cases
Version: v2
Security: Bearer

## Query parameters:

  - `filter` (string)
    The filter query parameter is used to filter a set of resources. The returned set of resources matches the criteria in the filter query parameter. The value of the filter query parameter is a subset of OData V4 filter expressions consisting of simple comparison operations joined by logical operators.

| Class | Supported |
|---|---|
| Types | string, timestamp, guid |
| Comparison | eq, ne, gt, ge, lt, le, in |
| Logical Expressions | and |
| Functions | contains(), startswith(), endswith() |

The following examples are not an exhaustive list of all possible filtering options.

  - `select` (string)
    The select query parameter is used to limit the properties returned for support cases. The value of the select query parameter is a comma separated list of properties. All properties are returned if the select parameter is omitted. __Note:__ Only the total property is supported.

  - `limit` (integer)
    Specifies the number of support cases to be returned.

  - `next` (string)
    Specifies the event ID, which acts as the pagination cursor for the next page of support cases.

## Response 200 fields (application/json):

  - `items` (array, required)

  - `items.id` (string, required)
    Unique identifier of the case.

  - `items.type` (string, required)
    The type of the resource.

  - `items.generation` (integer, required)
    Monotonically increasing update counter to track the support case version.

  - `items.createdAt` (string, required)
    The date and time of support case creation.

  - `items.updatedAt` (string, required)
    The last date and time the support case was updated.

  - `items.resourceUri` (string)
    URI to the support case.

  - `items.caseNumber` (string)
    The case number assigned to the support case.

  - `items.event` (object)
    Reference to the wellness event.

  - `items.event.resourceUri` (string, required)
    URI to the wellness event

  - `items.event.id` (string, required)
    Unique ID of the the wellness event

  - `items.user` (string)
    The first and last name of the user that escalated the wellness event. Only relevant to manually escalated cases.

  - `items.crm` (string)
    The customer relationship management (CRM) system used to create the support case.

  - `items.status` (string)
    The current status of the support case.
    Enum: "open", "closed", "escalated", "correlated", "acknowledged", "resolved", "expired", "error"

  - `items.caseHistory` (array)
    Case update history.

  - `items.caseHistory.action` (string)
    The type of case update, for example, Case Opened and Updated.

  - `items.caseHistory.timeStamp` (string)
    Date and time representing when the support case update occurred.

  - `items.source` (string)
    Indicates how the support case was created.
    Enum: "manual", "auto"

  - `items.details` (object)
    Curated details for manually created support cases. Only present when source is manual.

  - `items.details.category` (string)
    The primary help category, for example, "Backup and Recovery".

  - `items.details.subcategory` (string)
    The sub-category selection, displayed as a breadcrumb when multiple sub-categories apply. For example, "Disaster Recovery > Data Protection".

  - `items.details.description` (string)
    The user-provided issue description.

  - `items.details.priority` (object)
    Case priority.

  - `items.details.priority.label` (string)
    The human-readable priority label, for example, "Critical".

  - `items.details.priority.value` (string)
    The priority code, for example, "P1".

  - `items.details.outage` (boolean)
    A boolean that declares whether an outage has occurred.

  - `items.details.primaryContact` (object)
    Primary contact for the case.

  - `items.details.primaryContact.name` (string)
    The full name of the contact person.

  - `items.details.primaryContact.email` (string)
    Contact email address.

  - `items.details.primaryContact.phone` (string)
    The phone number of the contact.

  - `items.details.primaryContact.preferredContactMethod` (object)
    Specifies how the contact prefers to be reached. Contains the label and type.

  - `items.details.primaryContact.preferredContactMethod.label` (string)
    The human-readable label, for example, "Email".

  - `items.details.primaryContact.preferredContactMethod.type` (string)
    The contact method type, for example, "email" or "phone".

  - `items.details.alternateContact` (object)
    Alternate contact for the case. Only present when an alternate contact was provided during case creation.

  - `items.details.accountName` (string)
    Account name associated with the case.

  - `items.details.serialNumber` (string)
    Serial number of the device associated with the case.

  - `items.details.subscriptionKey` (string)
    License key that activates the device subscription.

  - `items.details.orderNumber` (string)
    Purchase order number associated with the device or subscription.

  - `items.details.hasAttachments` (boolean)
    Indicates whether the case includes file attachments. Set to true if one or more files are attached.

  - `count` (integer, required)
    Number of items (support cases) returned.

  - `next` (string, required)
    Support case ID, which acts as the pagination cursor for the next page of support cases.

  - `total` (integer, required)
    Total number of items (support cases) for the current filter criteria.

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
