---
title: "Sustainability-Insight-Center"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest.md"
scraped_at: "2026-06-07T05:46:40.165408+00:00Z"
---

# Sustainability-Insight-Center

The HPE Sustainability Insight Center API enables users to manage power consumption data that helps to reduce costs and achieve IT sustainability goals.

Version: v1beta1
License: HPE License

## Servers

```
https://us-west.api.greenlake.hpe.com
```

```
https://eu-central.api.greenlake.hpe.com
```

```
https://ap-northeast.api.greenlake.hpe.com
```

```
https://eu-west.api.greenlake.hpe.com
```

## Security

### bearer

Personal Access Token issued by the GLC platform.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[Sustainability-Insight-Center](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/index.yaml)

## usages

Aggregate usage data

### Aggregated energy use for entities

 - [GET /sustainability-insight-ctr/v1beta1/usage-by-entity](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getusagebyentity.md): Retrieves an aggregated energy usage list grouped by individual entities over a defined time frame and supports filtering, sorting, and offset-based pagination.

### Total aggregated data

 - [GET /sustainability-insight-ctr/v1beta1/usage-totals](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getusagetotals.md): Returns the total aggregated power cost, power consumption, and carbon emissions over a defined time frame and supports filtering by entities.

### Timeseries of energy usage over time

 - [GET /sustainability-insight-ctr/v1beta1/usage-series](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getusagebyseries.md): Retrieves aggregated energy usage statistics grouped by time bucket over a defined time frame and supports filtering by entities. Behavior is non-deterministic if the time range does not divide evenly by your selected interval.

### Aggregated carbon footprint usage for cloud entities

 - [GET /sustainability-insight-ctr/v1beta1/cloud-usage-by-entity](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getcloudusagebyentity.md): Retrieves aggregated carbon footprint usage in a list grouped by individual cloud entities, such as, cloud services, over a
defined time frame and supports filtering, sorting, and offset-based pagination.

### Total aggregated cloud carbon footprint usage

 - [GET /sustainability-insight-ctr/v1beta1/cloud-usage-totals](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getcloudusagetotals.md): Returns the total carbon footprint over a defined time frame and supports filtering by cloud entities.

### Timeseries of cloud carbon footprint usage over time

 - [GET /sustainability-insight-ctr/v1beta1/cloud-usage-series](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/usages/getcloudusagebyseries.md): Retrieves aggregated carbon footprint usage statistics grouped by time bucket over a defined time frame and
supports filtering by entities. Behavior is non-deterministic if the time range does not divide evenly by your selected
interval.

## coefficients

Create and retrieve custom coefficients for locations

### Get all cost and co2 coefficients

 - [GET /sustainability-insight-ctr/v1beta1/coefficients](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/coefficients/getcoefficients.md): Get a list of all costs (amount per kWh) and co2 coefficients of all locations. Supports filtering by locationId.

### Create cost and co2 coefficients for a location

 - [POST /sustainability-insight-ctr/v1beta1/coefficients](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/coefficients/addcoefficients.md): Create cost and co2 coefficients for a specific location's data. If a coefficient is provided, either the value must be provided of one of the use default or use current flags must be set. Takes effect after the returned start time.

### Get a single cost and co2 coefficient for an id

 - [GET /sustainability-insight-ctr/v1beta1/coefficients/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/coefficients/getcoefficient.md): Get a single cost and co2 coefficient for an id

## ingests

Upload and retrieve records of 3rd party ingests

### Get all metadata of uploaded 3rd party device measurements.

 - [GET /sustainability-insight-ctr/v1beta1/ingests](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/ingests/getingests.md): This returns the associated metadata of each uploaded 3rd party device measurement.

### Upload a document with 3rd party device measurement data.

 - [POST /sustainability-insight-ctr/v1beta1/ingests](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/ingests/addingest.md): Allows a user to upload power measurements for 3rd party devices from their own configured ITOM applications.

### Get metadata for a 3rd party device measurement.

 - [GET /sustainability-insight-ctr/v1beta1/ingests/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/ingests/getingest.md): Get metadata for an ingested 3rd party device measurement.

## datasources

Retrieve information about where data comes from

### Get all information for SIC data sources.

 - [GET /sustainability-insight-ctr/v1beta1/datasources](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/datasources/getdatasources.md): This returns information such as name and data collection times for each SIC data source.

### Get information for a SIC data source.

 - [GET /sustainability-insight-ctr/v1beta1/datasources/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/openapi/sustainability-insight-ctr-latest/datasources/getdatasource.md): Get information such as name and data collection times for a SIC data source.

