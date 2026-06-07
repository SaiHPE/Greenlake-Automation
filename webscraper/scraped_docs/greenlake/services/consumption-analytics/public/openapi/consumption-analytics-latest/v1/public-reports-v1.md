---
title: "HPE GreenLake Consumption Analytics Reports API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v1/public-reports-v1.md"
scraped_at: "2026-06-07T05:46:30.284732+00:00Z"
---

# HPE GreenLake Consumption Analytics Reports API

API reference documentation for the HPE GreenLake Consumption Analytics Reports API

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

[HPE GreenLake Consumption Analytics Reports API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/@v1/public-reports-v1.yaml)

## Reports

Reference documentation for reporting operations.

### List available report definitions

 - [GET /consumption-analytics/v1/reports](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v1/public-reports-v1/reports/reports-v1-list.md): List the report definitions that are available to the caller.

### Retrieve a report definition

 - [GET /consumption-analytics/v1/reports/{id}](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v1/public-reports-v1/reports/reports-v1-get-by-id.md): Fetches the details of a specific report definition by its ID. Use the id returned by List available report definitions as the path parameter.

### Download report table

 - [GET /consumption-analytics/v1/reports/{id}/contents](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v1/public-reports-v1/reports/reports-v1-export-csv.md): Executes a saved report definition and retrieves it as a CSV file. Use the id returned by List available report definitions as the path parameter. Indicate whether to include the currency symbols or units of measure in the exported CSV for currency fields using the boolean include-currency-symbol and include-units-of-measure query parameters. Both query parameters default to false.

