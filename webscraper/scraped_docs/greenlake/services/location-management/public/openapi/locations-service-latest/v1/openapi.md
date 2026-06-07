---
title: "Locations API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi.md"
scraped_at: "2026-06-07T06:13:37.463606+00:00Z"
---

# Locations API

Service to manage location information for HPE GreenLake platform.

Version: v1
License: HPE License

## Servers

```
https://global.api.greenlake.hpe.com
```

## Security

### Bearer

Personal access token issued by the HPE GreenLake platform.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Locations API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/location-management/public/openapi/locations-service-latest/@v1/openApi.yaml)

## Locations

### Lists all locations

 - [GET /locations/v1/locations](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/listalllocations.md): Retrieve location information for all locations.

### Create a Location

 - [POST /locations/v1/locations](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/createlocation.md): Create a location and store its associated information.

### Retrieve a location

 - [GET /locations/v1/locations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/getlocationby.md): Return information for a location specified by a location ID.

### Delete a location

 - [DELETE /locations/v1/locations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/deletelocation.md): Delete a location by providing a specific location ID.

### Update a location

 - [PATCH /locations/v1/locations/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/updatelocation.md): Update a location's information by specifying its location ID. Only include the fields that need to be updated in the request body. Fields that are not included in the request body will remain unchanged.
Note: The name and locationType fields are mandatory and cannot be set to empty or invalid values.

### Manage a location

 - [PATCH /locations/v1/locations/update/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/managelocation.md): Manage the location information for a location specified by its location ID. Provide information in the request body schema to create, update, or delete the location's address, contact, or location details. Only include the fields that need to be modified in the request body. Fields that are not included will remain unchanged.

### Get tags for a workspace

 - [GET /locations/v1/locations/tags](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/listalltags.md): Retrieve tag information for your workspace.

### Create or delete a tag

 - [PATCH /locations/v1/locations/tags](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/updatetags.md): Use this API to create or delete a tag. In the request body, provide: The tag name and tag value in the appropriate array to create (createTags) or delete (deleteTags) tags as needed.The location ID.

### Retrieves tags for given a location

 - [GET /locations/v1/locations/tags/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/listtagsbyid.md): Return a listing of all tag names and tag values for a given location. If a location has no tags, only the location ID and location name are returned.

### Retrieve location from latitude and longitude.

 - [GET /locations/v1/locations/address/revgeocode](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/reversegeocode.md): Geolocate a location by providing the longitude and latitude. Optionally, provide an ISO language code to return the information in a language different from the default (English).

### Create locations using CSV file

 - [POST /locations/v1/locations/locations-csv-upload](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/createlocationcsv.md): Create locations using a CSV file and store the associated information.

### Retrieve a CSV upload status

 - [GET /locations/v1/locations/async-operation/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/getcsvuploadstatus.md): Return status information for a CSV location upload by using the async location ID as a parameter.

### Locations Management service status

 - [GET /locations/v1/locations/status](https://developer.greenlake.hpe.com/docs/greenlake/services/location-management/public/openapi/locations-service-latest/v1/openapi/locations/getlocationservicestatusv1.md): Get Locations Management service status

