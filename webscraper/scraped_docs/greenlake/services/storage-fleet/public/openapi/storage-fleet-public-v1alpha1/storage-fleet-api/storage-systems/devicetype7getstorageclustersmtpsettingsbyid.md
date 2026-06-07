---
title: "GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/smtp-settings"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api/storage-systems/devicetype7getstorageclustersmtpsettingsbyid.md"
scraped_at: "2026-06-07T06:16:14.034003+00:00Z"
---

# Get SMTP settings of HPE Alletra Storage MP X10000 system identified by {systemId}

Get SMTP settings of HPE Alletra Storage MP X10000 system identified by {systemId}

Endpoint: GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/smtp-settings
Version: 1.2.0
Security: bearer

## Path parameters:

  - `systemId` (string, required)
    ID of the Storage system
    Example: "USE603C8P1"

## Query parameters:

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
    Unique identifier for the Storage system.
    Example: "ASHBFY6567YGHJ"

  - `items.type` (string, required)
    type
    Example: "string"

  - `items.apiVersion` (string,null)
    API version Details.
    Example: "sc.hpe.com/v1"

  - `items.associatedLinks` (array,null)
    Associated Links Details

  - `items.associatedLinks.resourceUri` (string,null)
    Resource Uri

  - `items.associatedLinks.type` (string)
    Resource Name

  - `items.commonResourceAttributes` (object,null)

  - `items.commonResourceAttributes.cloudState` (string,null)
    Cloud connectivity status of the system where the resource belongs
    Example: "CONNECTED"

  - `items.commonResourceAttributes.errCode` (string,null)
    Error code of the blocked status of the system where the resource belongs
    Example: "E01"

  - `items.commonResourceAttributes.errMessage` (string,null)
    Reason of the blocked status of the system where the resource belongs
    Example: "This storage system is not actively monitored in the cloud portal. Data Services Cloud Console proactively disabled monitoring and management of storage system with serial number {systemId} for sending excessive cloud events or for not responding to requests."

  - `items.customerId` (string,null)
    CustomerID for the Storage system.
    Example: "ASHBFDJHFB6567YGHJ"

  - `items.generation` (integer,null)
    The most recent specification that has been observed by the controller.
    Example: 1690045300

  - `items.kind` (string,null)
    Kind of the resource
    Example: "smtpSettings"

  - `items.resourceUri` (string,null)
    Link to the object URI

  - `items.status` (object,null)

  - `items.status.smtpConfigurationStatus` (object,null)

  - `items.status.smtpConfigurationStatus.credentials` (object,null)

  - `items.status.smtpConfigurationStatus.credentials.username` (string,null)
    Username
    Example: "India"

  - `items.status.smtpConfigurationStatus.encryption` (string,null)
    The encryption to use for sending mail to the SMTP server. Accepted values:{"None", "StartTLS", "SSL/TLS" }
    Example: "StartTLS"

  - `items.status.smtpConfigurationStatus.recipientEmailAddresses` (array,null)
    The email addresses to use for the recipients of SMTP messages from the system.
    Example: ["sender@email.com"]

  - `items.status.smtpConfigurationStatus.senderEmailAddress` (string,null)
    The address from which email from the system should should be sent. (The "From" Address)
    Example: "sender@email.com"

  - `items.status.smtpConfigurationStatus.smtpPort` (integer,null)
    The port to which SMTP messages should be sent on the server.
    Example: 586

  - `items.status.smtpConfigurationStatus.smtpServer` (string,null)
    SMTP server for sending email notifications.
    Example: "10.11.200.1"

  - `items.systemId` (string,null)
    Identifier of the Storage system.
    Example: "USE603C8P1"

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


