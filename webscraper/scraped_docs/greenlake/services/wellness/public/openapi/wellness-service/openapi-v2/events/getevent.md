---
title: "GET /wellness/v2/events/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/events/getevent.md"
scraped_at: "2026-06-07T06:16:33.938574+00:00Z"
---

# Get wellness event with specific ID

Retrieves a wellness event identified by the given ID.

Endpoint: GET /wellness/v2/events/{id}
Version: v2
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The wellness event ID.

## Response 200 fields (application/json):

  - `id` (string, required)
    Primary identifier for the wellness event given by the system.

  - `type` (string, required)
    The type of the resource.

  - `generation` (integer, required)
    Monotonically increasing update counter.

  - `createdAt` (string, required)
    Time of wellness event creation.

  - `updatedAt` (string, required)
    The last date and time the wellness event was updated.

  - `resourceUri` (string)
    URI to the wellness event itself (a self link).

  - `title` (string)
    Short description of the wellness event.

  - `description` (object)
    Explanation of the wellness event.

  - `description.mediaType` (string)
    Specifies the media type of the content.
    Enum: "text/plain", "html"

  - `description.content` (string)
    A descriptive explanation of the wellness event.

  - `asset` (object)
    The device the wellness event belongs to.

  - `asset.name` (string)
    The serial number or name of the asset.

  - `asset.serialNumber` (string)
    The serial number of the asset.

  - `condition` (object)
    Specifies details about the nature of the wellness event.

  - `condition.urn` (string)
    Unique identifier of the condition.

  - `condition.severity` (string)
    The severity level of the wellness event.
    Enum: "critical", "warning", "notice"

  - `condition.name` (string)
    Human-readable name given to the condition.

  - `condition.category` (string)
    The category the condition belongs to.

  - `status` (object)
    Current status of the wellness event.

  - `status.currentState` (string)
    The current status. It is the most recent computed state for the event.
    Enum: "open", "resolved", "timeoutCaseCreation", "pendingCaseCreation", "pendingEscalation", "escalated", "correlated", "acknowledged", "expired", "error"

  - `status.correlatedTo` (array)
    List of wellness events correlated to this wellness event.

  - `causes` (array)
    A list of possible root causes for the event condition.

  - `causes.title` (string)
    One sentence summary of potential cause.

  - `causes.confidence` (integer)
    Confidence score for this cause.

  - `causes.visibility` (string)
    A visibility filter. Null or absent implies universally visible.

  - `causes.recommendation` (string)
    A recommended action to resolve the wellness condition.

  - `supportCase` (object)
    Support case object.

  - `supportCase.id` (string, required)
    Unique identifier of the case.

  - `supportCase.generation` (integer, required)
    Monotonically increasing update counter to track the support case version.

  - `supportCase.createdAt` (string, required)
    The date and time of support case creation.

  - `supportCase.updatedAt` (string, required)
    The last date and time the support case was updated.

  - `supportCase.resourceUri` (string)
    URI to the support case.

  - `supportCase.caseNumber` (string)
    The case number assigned to the support case.

  - `supportCase.event` (object)
    Reference to the wellness event.

  - `supportCase.event.resourceUri` (string, required)
    URI to the wellness event

  - `supportCase.event.id` (string, required)
    Unique ID of the the wellness event

  - `supportCase.user` (string)
    The first and last name of the user that escalated the wellness event. Only relevant to manually escalated cases.

  - `supportCase.crm` (string)
    The customer relationship management (CRM) system used to create the support case.

  - `supportCase.status` (string)
    The current status of the support case.
    Enum: "open", "closed", "escalated", "correlated", "acknowledged", "resolved", "expired", "error"

  - `supportCase.caseHistory` (array)
    Case update history.

  - `supportCase.caseHistory.action` (string)
    The type of case update, for example, Case Opened and Updated.

  - `supportCase.caseHistory.timeStamp` (string)
    Date and time representing when the support case update occurred.

  - `supportCase.source` (string)
    Indicates how the support case was created.
    Enum: "manual", "auto"

  - `supportCase.details` (object)
    Curated details for manually created support cases. Only present when source is manual.

  - `supportCase.details.category` (string)
    The primary help category, for example, "Backup and Recovery".

  - `supportCase.details.subcategory` (string)
    The sub-category selection, displayed as a breadcrumb when multiple sub-categories apply. For example, "Disaster Recovery > Data Protection".

  - `supportCase.details.description` (string)
    The user-provided issue description.

  - `supportCase.details.priority` (object)
    Case priority.

  - `supportCase.details.priority.label` (string)
    The human-readable priority label, for example, "Critical".

  - `supportCase.details.priority.value` (string)
    The priority code, for example, "P1".

  - `supportCase.details.outage` (boolean)
    A boolean that declares whether an outage has occurred.

  - `supportCase.details.primaryContact` (object)
    Primary contact for the case.

  - `supportCase.details.primaryContact.name` (string)
    The full name of the contact person.

  - `supportCase.details.primaryContact.email` (string)
    Contact email address.

  - `supportCase.details.primaryContact.phone` (string)
    The phone number of the contact.

  - `supportCase.details.primaryContact.preferredContactMethod` (object)
    Specifies how the contact prefers to be reached. Contains the label and type.

  - `supportCase.details.primaryContact.preferredContactMethod.label` (string)
    The human-readable label, for example, "Email".

  - `supportCase.details.primaryContact.preferredContactMethod.type` (string)
    The contact method type, for example, "email" or "phone".

  - `supportCase.details.alternateContact` (object)
    Alternate contact for the case. Only present when an alternate contact was provided during case creation.

  - `supportCase.details.accountName` (string)
    Account name associated with the case.

  - `supportCase.details.serialNumber` (string)
    Serial number of the device associated with the case.

  - `supportCase.details.subscriptionKey` (string)
    License key that activates the device subscription.

  - `supportCase.details.orderNumber` (string)
    Purchase order number associated with the device or subscription.

  - `supportCase.details.hasAttachments` (boolean)
    Indicates whether the case includes file attachments. Set to true if one or more files are attached.

  - `correlated` (boolean)
    Specifies if this wellness event is related to another wellness event or not.

  - `serviceName` (string)
    The name of the service to which this event belongs.

  - `productName` (string)
    The name of the product to which this event belongs.

  - `flag` (boolean)
    Specifies if the wellness event has been flagged or not.

  - `read` (boolean)
    Specifies if the wellness event has been read or not.

  - `archive` (boolean)
    Specifies if the wellness event has been archived or not.

  - `supportCaseCreationOpUri` (string)
    URI to get details of the support case creation operation.

  - `serviceManager` (object)
    Reference to the service manager (application) of the device that generated this wellness event.

  - `serviceManager.resourceUri` (string, required)
    URI to the service manager (application) of the device that generated this wellness event.

  - `serviceManager.id` (string, required)
    Unique ID of the service manager (application) of the device that generated this wellness event.

  - `region` (string)
    The region of the device to which the wellness event belongs.

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

## Response 404 fields (application/json):

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
