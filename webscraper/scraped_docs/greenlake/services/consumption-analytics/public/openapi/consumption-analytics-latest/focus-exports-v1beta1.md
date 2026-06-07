---
title: "HPE GreenLake Consumption Analytics FOCUS Exports API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/focus-exports-v1beta1.md"
scraped_at: "2026-06-07T05:46:29.444906+00:00Z"
---

# HPE GreenLake Consumption Analytics FOCUS Exports API

API reference documentation for the HPE GreenLake Consumption Analytics FOCUS Exports API

Version: 1.0.0
License: HPE

## Servers

Production - US West
```
https://us-west.api.greenlake.hpe.com
```

## Security

### glcUserBearerAuth

JWT token used for authentication and authorization.

Type: http
Scheme: bearer
Bearer Format: JWT

## Download OpenAPI description

[HPE GreenLake Consumption Analytics FOCUS Exports API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/focus-exports-v1beta1.yaml)

## FOCUS Exports

Reference documentation for FOCUS export configuration operations.

### List available FOCUS export configurations

 - [GET /consumption-analytics/v1beta1/focus-exports](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/focus-exports-v1beta1/focus-exports/focus-v1beta1-list.md): List the FOCUS export configurations that are available to the caller.

### Get a FOCUS export configuration

 - [GET /consumption-analytics/v1beta1/focus-exports/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/focus-exports-v1beta1/focus-exports/focus-v1beta1-get.md): Fetches the details of a specific FOCUS export configuration by its ID. Use the id returned by List available FOCUS export configurations as the path parameter.

### Download FOCUS export CSV data

 - [GET /consumption-analytics/v1beta1/focus-exports/{id}/contents](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/focus-exports-v1beta1/focus-exports/focus-v1beta1-export.md): Executes the given FOCUS export configuration and retrieves it as a CSV file. Use the id returned by List available FOCUS export configurations as the path parameter.

