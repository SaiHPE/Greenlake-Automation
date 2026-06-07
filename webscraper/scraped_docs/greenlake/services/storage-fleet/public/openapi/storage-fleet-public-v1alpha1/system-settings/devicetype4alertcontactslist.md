---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/system-settings/devicetype4alertcontactslist.md"
scraped_at: "2026-06-07T06:16:01.848623+00:00Z"
---

# Get alert-contact details for an HPE Alletra Storage MP B10000 storage system

Get alert-contact details for an HPE Alletra Storage MP B10000 storage system

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

## Query parameters:

  - `limit` (integer)
    Number of items to return at a time
    Example: 10

  - `offset` (integer)
    The offset of the first item in the collection to return
    Example: 5

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `count` (integer, required)
    Number of items in this response.

  - `offset` (integer, required)
    The offset query parameter from the request.

  - `items` (array, required)

  - `items.id` (string, required)
    Unique Identifier of the contact
    Example: "67d09515-8526-9b02-c0c4-c1f443a39402"

  - `items.type` (string, required)
    The type of resource
    Example: "alert-contacts"

  - `items.company` (string,null)
    Company
    Example: "HPE"

  - `items.companyCode` (string,null)
    Company code
    Example: "HPE"

  - `items.country` (string,null)
    Country
    Example: "US"

  - `items.customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1sd"

  - `items.fax` (string,null)
    Fax number
    Example: "+1 323 555 1234"

  - `items.firstName` (string,null)
    First name
    Example: "john"

  - `items.generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627540907421

  - `items.includeSvcAlerts` (boolean,null)
    Email sent to contact shall include service alert

  - `items.lastName` (string,null)
    Last name
    Example: "kevin"

  - `items.notificationSeverities` (array,null)
    Severities of notifications the contact will be notificated. An array of number: 0 - Fatal, 1 - Critical, 2 - Major, 3 - Minor, 4 - Degraded, 5 - Info, 6 - Debug
    Example: [0,1,2,3,4,5]

  - `items.preferredLanguage` (string,null)
    Preferred language when being contacted or emailed
    Example: "en"

  - `items.primaryEmail` (string,null)
    Primary email address
    Example: "kevin.john@hpe.com"

  - `items.primaryPhone` (string,null)
    Primary phone
    Example: "98783456"

  - `items.receiveGrouped` (boolean,null)
    Contact will receive grouped low urgency email notifications
    Example: true

  - `items.secondaryEmail` (string,null)
    Secondary email address
    Example: "winny.pooh@hpe.com"

  - `items.secondaryPhone` (string,null)
    Secondary phone
    Example: "23456789"

  - `items.systemId` (string,null)
    SystemId/serialNumber of the array.
    Example: "7CE751P312"

  - `items.systemSupportContact` (boolean,null)
    Contact will be called for any system issues

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

## Response default fields (application/json):

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


