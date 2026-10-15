---
title: "GET /wellness/v2/support-cases/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/wellness/public/openapi/wellness-service/openapi-v2/support-cases/getsupportcase.md"
scraped_at: "2026-06-07T06:16:34.157444+00:00Z"
---

# Get support case with specific ID

Retrieves a support case identified by the given ID.

Endpoint: GET /wellness/v2/support-cases/{id}
Version: v2
Security: Bearer

## Path parameters:

  - `id` (string, required)
    The support case ID.

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique identifier of the case.

  - `type` (string, required)
    The type of the resource.

  - `generation` (integer, required)
    Monotonically increasing update counter to track the support case version.

  - `createdAt` (string, required)
    The date and time of support case creation.

  - `updatedAt` (string, required)
    The last date and time the support case was updated.

  - `resourceUri` (string)
    URI to the support case.

  - `caseNumber` (string)
    The case number assigned to the support case.

  - `event` (object)
    Reference to the wellness event.

  - `event.resourceUri` (string, required)
    URI to the wellness event

  - `event.id` (string, required)
    Unique ID of the the wellness event

  - `user` (string)
    The first and last name of the user that escalated the wellness event. Only relevant to manually escalated cases.

  - `crm` (string)
    The customer relationship management (CRM) system used to create the support case.

  - `status` (string)
    The current status of the support case.
    Enum: "open", "closed", "escalated", "correlated", "acknowledged", "resolved", "expired", "error"

  - `caseHistory` (array)
    Case update history.

  - `caseHistory.action` (string)
    The type of case update, for example, Case Opened and Updated.

  - `caseHistory.timeStamp` (string)
    Date and time representing when the support case update occurred.

  - `source` (string)
    Indicates how the support case was created.
    Enum: "manual", "auto"

  - `details` (object)
    Curated details for manually created support cases. Only present when source is manual.

  - `details.category` (string)
    The primary help category, for example, "Backup and Recovery".

  - `details.subcategory` (string)
    The sub-category selection, displayed as a breadcrumb when multiple sub-categories apply. For example, "Disaster Recovery > Data Protection".

  - `details.description` (string)
    The user-provided issue description.

  - `details.priority` (object)
    Case priority.

  - `details.priority.label` (string)
    The human-readable priority label, for example, "Critical".

  - `details.priority.value` (string)
    The priority code, for example, "P1".

  - `details.outage` (boolean)
    A boolean that declares whether an outage has occurred.

  - `details.primaryContact` (object)
    Primary contact for the case.

  - `details.primaryContact.name` (string)
    The full name of the contact person.

  - `details.primaryContact.email` (string)
    Contact email address.

  - `details.primaryContact.phone` (string)
    The phone number of the contact.

  - `details.primaryContact.preferredContactMethod` (object)
    Specifies how the contact prefers to be reached. Contains the label and type.

  - `details.primaryContact.preferredContactMethod.label` (string)
    The human-readable label, for example, "Email".

  - `details.primaryContact.preferredContactMethod.type` (string)
    The contact method type, for example, "email" or "phone".

  - `details.alternateContact` (object)
    Alternate contact for the case. Only present when an alternate contact was provided during case creation.

  - `details.accountName` (string)
    Account name associated with the case.

  - `details.serialNumber` (string)
    Serial number of the device associated with the case.

  - `details.subscriptionKey` (string)
    License key that activates the device subscription.

  - `details.orderNumber` (string)
    Purchase order number associated with the device or subscription.

  - `details.hasAttachments` (boolean)
    Indicates whether the case includes file attachments. Set to true if one or more files are attached.

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
