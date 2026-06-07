---
title: "HPE GreenLake for Locations"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public.md"
scraped_at: "2026-06-07T06:13:28.086876+00:00Z"
---

# HPE GreenLake for Locations

This page provides an introduction and quick start guide for the Locations API:

- [Overview](#overview)—See a high-level description of the API.
- [Developer guide](#developer-guide)—Review a quick start guide that helps you get started with the API.


## Overview

The HPE GreenLake Locations service allows you to assign and manage device service delivery information. Service delivery information includes device location and support contact information:

- Device location—A physical address associated with each device instance on the HPE GreenLake cloud.
- Support contact information—A name, email address, and optionally a phone number associated with each device instance.


HPE GreenLake for Locations is a RESTful API for creating and managing location services. The API enables any locations service operation or task available through the HPE GreenLake cloud UI. The platform uses the collected information to automate service delivery and to create automated support cases.

### Features

- Create locations with addresses and service delivery contact information.
- Assign a primary contact for a device.
- Access audit logs for the locations service.
- Location validation to ensure that the location and related details are still correct.
- Manage tags for a specific location or workspace.
- Retrieve a location using latitude and longitude.
- Create locations in bulk using CSV upload.


### What's new

May 2026

API documentation is aligned with the latest request and response payload behavior for location update operations, including partial update guidance, expanded schema fields, and corrected error responses.

November 2025

The previously deprecated `/v1beta1/` endpoints have been removed and are no longer available to use. Use the `v1` versions instead.

[For more information, see the Changelog.](/docs/greenlake/services/location-management/public/openapi/changelog)

### Related documentation

- [HPE GreenLake Cloud User Guide](https://support.hpe.com/hpesc/public/docDisplay?docId=a00120892en_us&page=GUID-D357866E-BF13-4F71-A745-F2139545DEF1.html)


## Developer guide

The Locations service enables creating and managing locations with service delivery contact and address information. The examples in this guide help you use the Locations APIs to add, update, and delete locations.

### Prerequisites

Ensure that you meet the following prerequisites:

- Locations and service delivery contact information that you want to map to existing devices.
- Access to devices that you want to assign locations to.
- HPE GreenLake cloud administrator permissions. Contact the administrator in your organization if you do not already have access.


#### Endpoints

Endpoints are the host URLs that you will submit your API requests to.

- [https://global.api.greenlake.hpe.com/](https://global.api.greenlake.hpe.com/)


#### URIs

Unique Resource Identifiers (URIs) identify a server or resource used in the Locations API. A URI is a full API path ending with a specific endpoint. For example:

- `/locations/v1/locations`
- `/locations/v1/locations/{id}`
- `/locations/v1/locations/update/{id}`
- `/locations/v1/locations/tags`
- `/locations/v1/locations/tags/{id}`
- `/locations/v1/locations/address/revgeocode`
- `/locations/v1/locations/status`


#### Access and permissions

A user with view permissions for Locations (`ccs.location-management.view`) is sufficient to make the following API calls:

- `GET /locations/v1/locations`
- `GET /locations/v1/locations/{id}`
- `GET /locations/v1/locations/tags`
- `GET /locations/v1/locations/tags/{id}`
- `GET /locations/v1/locations/address/revgeocode`
- `GET /locations/v1/locations/status`


A user with edit permissions for Locations (`ccs.location-management.edit`) is required to make the following API calls:

- `POST /locations/v1/locations`
- `PATCH /locations/v1/locations/{id}`
- `DELETE /locations/v1/locations/{id}`
- `PATCH /locations/v1/locations/update/{id}`
- `PATCH /locations/v1/locations/tags`


#### Generating token

You must create a personal API client and generate an access token to make API calls. HPE GreenLake APIs use OAuth-based access tokens used as an authorization bearer token. To do this:

1. [Create a personal API client.](/docs/greenlake/guides/public/authentication/authentication#creating-a-personal-api-client)
  - Select the **HPE GreenLake Cloud Platform** service.
2. [Generate an access token.](/docs/greenlake/guides/public/authentication/authentication#generating-an-access-token)
  - [View code samples for generating an access token.](/docs/greenlake/guides/public/authentication/authentication#viewing-code-samples-for-generating-an-access-token)
3. Use the access token as an authorization bearer token to make secure REST API calls.


### Making it all work

The examples in this section provide a high-level overview of the functionality of HPE GreenLake for Locations APIs. For more details and code samples, view the **API reference**.

#### Obtain a list of all locations

Locations capture addresses, contacts, and service delivery information for operations, management, and commerce. The information is used for service delivery and support, and operations. Use a `GET` request to retrieve a list of locations.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/locations
```

The information included in a valid response:

- `id` (location ID)
- `name`
- `city`
- `country`
- `expiredAt`


A valid response will also return pagination with page information and total count of locations.

The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Obtain specific location information

Locations capture addresses, contacts, and service delivery information for operations, management, and commerce. The information is used for service delivery and support, and operations.

Make a `GET` request and provide the location Id to retrieve information for the specified location.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/locations/{id}
```

The information included in a valid response:

- `id`
- `name`
- `locationType`
- `description`
- `expiredAt`
- `contacts` (array):
  - `id`
  - `name`
  - `type`
  - `email`
  - `phoneNumber`
- `addresses` (array):
  - `id`
  - `type`
  - `country`
  - `streetAddress`
  - `streetAddress2`
  - `city`
  - `state`
  - `postalCode`


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Create a location

You can create a location to assign to your devices using the Locations service by making a `POST` request and providing a name, description, address, and contact information.

- **Name**—Give the location a name that makes it easy to identify.
- **Description** (optional)—Add a description of the location to help identify it.
- **Address**—Provide a physical address of the location. The initial address type will be `"street"`. You can later add additional addresses of type `"shipping_receiving"` using the update operations.
- **Contacts**—Provide the name, email, and phone number of the location contacts. You must provide only one primary contact. You can provide multiple security, shipping and receiving, and operations contacts.


The endpoint:


```bash
POST https://global.api.greenlake.hpe.com/locations/v1/locations
```

Payload:


```json
{
    "name": "Test Location",
    "description": "This is a test location",
    "type": "building",
    "validated": true,
    "validationCycle": "6",
    "addresses": [
        {
            "type": "street",
            "country": "US",
            "street_address": "1701 E Mossy Oaks Rd ",
            "street_address2": "This is a test location",
            "city": "Spring",
            "state": "TX",
            "postal_code": "77389"
        }
    ],
    "contacts": [
        {
            "type": "primary",
            "name": "John Doe",
            "phoneNumber": "+1800-123-4567",
            "email": "john.doe@hpe.com"
        }
    ]
}
```

The information included in a valid response:

- `id`
- `name`
- `locationType`
- `description`
- `addresses` (array):
  - `id`
  - `type`
  - `country`
  - `streetAddress`
  - `streetAddress2`
  - `city`
  - `state`
  - `postalCode`
- `contacts` (array):
  - `name`
  - `type`
  - `email`
  - `phoneNumber`
- `validated`
- `validatedByName`
- `validatedByEmail`
- `validationCycle`
- `validationExpired`
- `generation`
- `createdAt`
- `updatedAt`


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Delete a location

To delete a particular location, use a `DELETE` request and provide a specific location Id.


```sh
DELETE https://global.api.greenlake.hpe.com/locations/v1/locations/{id}
```

The information included in a valid response:

- 204 No content response.


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Update location

Update location information like address, contact, name, and description for a specified location by making a `PATCH` request and providing a location id.

The endpoint:


```sh
PATCH https://global.api.greenlake.hpe.com/locations/v1/locations/{id}
```

Payload:


```json
{
  "name": "Test Location",
  "description": "This is a test location.",
  "type": "Building"
}
```

The payload can also consist of contact or address objects to be updated.

The information included in a valid response:

- Empty response
- `id`
- `type`
- `name`
- `locationType`
- `description`
- `addresses` (array of objects):
  - `id`
  - `type`
  - `country`
  - `streetAddress`
  - `streetAddress2`
  - `city`
  - `state`
  - `postalCode`
- `contacts` (array of objects):
  - `id`
  - `name`
  - `type`
  - `email`
  - `phoneNumber`
- `validated`
- `validatedByName`
- `validatedByEmail`
- `validatedAt`
- `validationCycle`
- `validationExpired`
- `generation`
- `createdAt`
- `updatedAt`


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Manage location information

Update location information with an array of address and contact objects for a specified location by making a `PATCH` request and providing a location id.

The endpoint:


```sh
PATCH https://global.api.greenlake.hpe.com/locations/v1/locations/update/{id}
```

Payload:


```json
{
  "addresses": {
    "add": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "city": "string",
        "country": "string",
        "locationId": "string",
        "postalCode": "string",
        "state": "string",
        "streetAddress": "string",
        "streetAddress2": "string",
        "type": "shipping_receiving"
      }
    ],
    "delete": [
      "string"
    ],
    "update": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "city": "string",
        "country": "string",
        "locationId": "string",
        "postalCode": "string",
        "state": "string",
        "streetAddress": "string",
        "streetAddress2": "string",
        "type": "shipping_receiving"
      }
    ]
  },
  "contacts": {
    "add": [
      {
        "email": "string",
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "locationId": "string",
        "name": "string",
        "phoneNumber": "string",
        "type": "primary"
      }
    ],
    "delete": [
      "string"
    ]
  }
}
```

The payload can also consist of contact or address objects to be updated.

The information included in a valid response:

- Empty response
- `id`
- `type`
- `name`
- `locationType`
- `description`
- `addresses` (array of objects):
  - `id`
  - `type`
  - `country`
  - `streetAddress`
  - `streetAddress2`
  - `city`
  - `state`
  - `postalCode`
- `contacts` (array of objects):
  - `id`
  - `name`
  - `type`
  - `email`
  - `phoneNumber`
- `validated`
- `validatedByName`
- `validatedByEmail`
- `validatedAt`
- `validationCycle`
- `validationExpired`
- `generation`
- `createdAt`
- `updatedAt`


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Obtain a list of all tags for all locations in a workspace

Tags consist of name and value pairs and are associated with locations.

Use this `GET` request to retrieve a list of tags for a workspace.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/locations/tags
```

The information included in a valid response:

- An array of objects with the tag name, tag value, and the created at timestamp.
- Pagination with page information
- Total count of tags for a workspace.


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Obtain tag information for a specific location

Tags consist of name and value and are associated with locations.

Use this `GET` request and provide the location ID to retrieve all the tag information for the specified location.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/locations/tags/{id}
```

The information included in a valid response:

- `locationId`
- `locationName`
- `tags` (array of objects):
  - `name`
  - `value`


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Manage tags for a location

Update tag information by providing create and delete tag objects for a specified location.

Make a `PATCH` request and provide a location ID in the request.

The endpoint:


```sh
PATCH https://global.api.greenlake.hpe.com/locations/v1/locations/tags
```

Payload:


```json
{
    "createTags": [

        {
            "name": "test-2001",
            "value": ""
        },
        {
            "name": "test-2002",
            "value": ""
        },
        {
            "name": "test-2003",
            "value": ""
        },
        {
            "name": "test-2004",
            "value": ""
        },
        {
            "name": "test-2005",
            "value": ""
        }
    ],
    "deleteTags": [
          {
            "name": "test-2046",
            "value": ""
        }
    ],
    "locationId": "4f94d3fa-cbcc-463d-a13d-d3e32c2d722d"
}
```

The payload can also include contact or address objects to update.

The information included in a valid response:

- Empty response
- `createTag` (an object with tag name and value pairs)
- `deleteTag` (an object with tag name and value pairs)
- `Id`
- `Type`
- `Generation`
- `CreatedAt`
- `UpdatedAt`


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Obtain location address using latitude and longitude

Use this endpoint to reverse geocode a location. In reverse geocoding, a location described by geographic coordinates (longitude and latitude) is converted to a human-readable address.

Make a `GET` request and provide the longitude and latitude as query parameters to retrieve a location's address information. Locations capture addresses, contacts, and service delivery information for operations, management, and commerce. The information is used for service delivery, support, and operations.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/address/revgeocode
```

The information included in a valid response:

- `label` (full label address)
- `countryCode`
- `countryName`
- `stateCode`
- `state`
- `county`
- `city`
- `street`
- `postalCode`
- `lat` (latitude)
- `lng` (longitude)


The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


For example:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/address/revgeocode?latitude=48.924549&longitude=2.359627
```

Payload:


```json
{
    "label": "STADE DE FRANCE, Avenue Jules Rimet, 93210 Saint-Denis, France",
    "countryCode": "FRA",
    "countryName": "France",
    "stateCode": "IDF",
    "state": "Ile-de-France",
    "county": "Seine-Saint-Denis",
    "city": "Saint-Denis",
    "street": "Avenue Jules Rimet",
    "postalCode": "93210",
    "lat": 48.9242,
    "lng": 2.35862
}
```

#### Create a location using CSV upload

Using this API endpoint, you create locations in bulk. When calling the endpoint, include a CSV with the location details. You can upload up to 100 locations at once using a CSV file, and the file size of the CSV must be under 100KB. The location is automatically assigned the default validation period of six months.

The details you can include in the CSV are:

- Location Name(Required)
- Description(Optional)
- Street Address(Required)
- City(Required)
- State/Province(Required)
- Country(Required)
- Zip/Postal Code(Required)
- Primary Contact Email(Required)
- First Name(Required)
- Last Name(Required)
- Tag 1 Name (optional)
- Tag 1 Value (optional)
- Tag 2 Name (optional)
- Tag 2 Value (optional)


This endpoint is an asynchronous operation, meaning:

- The operation may take some time to complete but does so in the background.
- You do not have to wait for the operation to finish. Therefore, you can make simultaneous calls to the endpoint or carry on with other tasks.
- The endpoint initially responds with a `202 Accepted`, a URI to the async-operation resource, and a unique `id` to track the status of the operation.


Use the `id` returned by this endpoint when calling the [**Get the status of the asynchronous CSV upload operation**](/docs/greenlake/services/location-management/public#get-the-status-of-the-asynchronous-csv-upload-operation) to check the status of the operation.

The endpoint:


```sh
POST https://global.api.greenlake.hpe.com/locations/v1/locations/locations-csv-upload
```

- Attach the CSV in the request as a file.


Payload:


```sh
Content-Type: multipart/form-data
Form Data: file (the CSV file to be uploaded)

file: example.csv
```

The information included in a valid response:


```json
  {
    "status": "INITIALIZED",
    "startedAt": "2025-03-06T01:18:43Z",
    "endedAt": "",
    "progressPercent": 0,
    "suggestedPollingIntervalSeconds": 10,
    "timeoutMinutes": 0,
    "result": {
        "totalCount": 0,
        "succeededCount": 0,
        "failedCount": 0,
        "failedRecords": null,
        "succeededRecords": null
    },
    "id": "525c4816-4415-4301-a4dc-514de61e1704",
    "type": "locations/asyncOperation"
}
```

The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Get the status of the asynchronous CSV upload operation

An asynchronous resource tracks the status of a CSV upload using the asynchronous location ID received from [**Create a location using CSV upload**](/docs/greenlake/services/location-management/public#create-a-location-using-csv-upload). It has four states `INITIALIZED`, `IN_PROGRESS`, `SUCCEEDED`, and `FAILED`. An asynchronous resource will not be available 24 hours after reaching a terminal state (`SUCCEEDED`, `FAILED`).

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/locations/async-operation/{id}
```

The information included in a valid response:


```json
{
    "status": "SUCCEEDED",
    "startedAt": "2025-03-06T01:18:43Z",
    "endedAt": "2025-03-06T01:18:44Z",
    "progressPercent": 100,
    "suggestedPollingIntervalSeconds": 10,
    "timeoutMinutes": 0,
    "result": {
        "totalCount": 1,
        "succeededCount": 1,
        "failedCount": 0,
        "failedRecords": null,
        "succeededRecords": [
            {
                "name": "test-csv",
                "id": "12a0ad99-d915-49cb-8dab-c830f182f327"
            }
        ]
    },
    "id": "525c4816-4415-4301-a4dc-514de61e1704",
    "type": "locations/asyncOperation"
}
```

The information included in an invalid response:

- `httpStatusCode`
- `message`
- `debugId`
- `errorCode`


#### Check service status

You can check the health and availability of the Locations service using the status endpoint. This is useful for monitoring the service or troubleshooting connectivity issues.

The endpoint:


```sh
GET https://global.api.greenlake.hpe.com/locations/v1/locations/status
```

A successful response returns an HTTP 200 OK status, indicating that the service is operational.

### Filtering

Filters allow you to limit the resources that take part in the action of a REST call. When a REST call includes a filter, the GET or PUT action is restricted to a response that meets the filter requirements. Specify filters using the query parameter `filter`.

A generic example of filtering syntax:


```sh
filter = <property> <operation> <literal>
```

- **Property** is the name of an attribute in the requested resource type. The property name is always to the left of the operation.
- **Operation** is the parameter used to evaluate the comparison. Operations compare properties against literals. The Locations API supports the equality operation (`eq`) and the special case operation, `contains`. Examples:
  - Equality—`?filter=<property> eq <literal>`—The equality operator can be used with the city and country properties.
  - Contains—`?filter=contains(<property>, <literal>)`—The Locations service allows you to filter using the contains function. A function is a block of reusable code that performs a single action.
- **Literal** is what the property is to be compared against. The Locations API supports the data type string, which is anything in 'single quotes'. For a successful matching operation, the data types must match, and the syntax determines the data type of the literals. Due to URL encoding, reserved characters ! # $ & ' ( ) * + , / : ; = ? @ [ ] in string literals must be replaced with percent-encoded equivalents.


Examples of equality operator filters:


```sh cityName
GET <URI>?filter=city eq 'cityName'
```


```sh countryName
GET <URI>?filter=country eq 'countryName'
```

Example of the special case operation contains:


```sh contains
GET <URI>?filter=contains(name,'test')'
```

The contains operator matches strings that contain the literal, "ob". For example, "Rob", "Bob" and so on.

#### OData filtering reference

This filtering is a subset of [OData 4.0 filtering](http://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html#_Toc31358949).