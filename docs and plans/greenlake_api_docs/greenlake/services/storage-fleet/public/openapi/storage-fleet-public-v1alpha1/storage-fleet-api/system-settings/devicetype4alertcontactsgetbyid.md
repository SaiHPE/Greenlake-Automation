---
title: "GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/system-settings/devicetype4alertcontactsgetbyid.md"
scraped_at: "2026-06-07T06:16:15.575301+00:00Z"
---

# Get alert-contact details for an HPE Alletra Storage MP B10000 storage system identified by {id}

Get alert-contact details for an HPE Alletra Storage MP B10000 storage system identified by {id}

Endpoint: GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    systemId of the storage system
    Example: "7CE751P312"

  - `id` (string, required)
    Unique Identifier of the alert contact
    Example: "a4c78226-69cd-b9e7-af3e-445ca8f8a655"

## Query parameters:

  - `select` (string)
    Query to select only the required parameters, separated by . if nested
    Example: "id"

## Response 200 fields (application/json):

  - `id` (string, required)
    Unique Identifier of the contact
    Example: "67d09515-8526-9b02-c0c4-c1f443a39402"

  - `type` (string, required)
    The type of resource
    Example: "alert-contacts"

  - `company` (string,null)
    Company
    Example: "HPE"

  - `companyCode` (string,null)
    Company code
    Example: "HPE"

  - `country` (string,null)
    Country
    Example: "US"

  - `customerId` (string)
    The customer application identifier
    Example: "fc5f41652a53497e88cdcebc715cc1sd"

  - `fax` (string,null)
    Fax number
    Example: "+1 323 555 1234"

  - `firstName` (string,null)
    First name
    Example: "john"

  - `generation` (integer)
    A monotonically increasing value. This value updates when the resource is updated and can be used as a short way to determine if a resource has changed or which of two different copies of a resource is more up to date.
    Example: 1627540907421

  - `includeSvcAlerts` (boolean,null)
    Email sent to contact shall include service alert

  - `lastName` (string,null)
    Last name
    Example: "kevin"

  - `notificationSeverities` (array,null)
    Severities of notifications the contact will be notificated. An array of number: 0 - Fatal, 1 - Critical, 2 - Major, 3 - Minor, 4 - Degraded, 5 - Info, 6 - Debug
    Example: [0,1,2,3,4,5]

  - `preferredLanguage` (string,null)
    Preferred language when being contacted or emailed
    Example: "en"

  - `primaryEmail` (string,null)
    Primary email address
    Example: "kevin.john@hpe.com"

  - `primaryPhone` (string,null)
    Primary phone
    Example: "98783456"

  - `receiveGrouped` (boolean,null)
    Contact will receive grouped low urgency email notifications
    Example: true

  - `secondaryEmail` (string,null)
    Secondary email address
    Example: "winny.pooh@hpe.com"

  - `secondaryPhone` (string,null)
    Secondary phone
    Example: "23456789"

  - `systemId` (string,null)
    SystemId/serialNumber of the array.
    Example: "7CE751P312"

  - `systemSupportContact` (boolean,null)
    Contact will be called for any system issues

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


