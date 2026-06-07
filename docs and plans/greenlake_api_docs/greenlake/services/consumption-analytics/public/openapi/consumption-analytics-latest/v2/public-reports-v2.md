---
title: "HPE GreenLake Consumption Analytics Reports API"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v2/public-reports-v2.md"
scraped_at: "2026-06-07T06:13:36.225761+00:00Z"
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

[HPE GreenLake Consumption Analytics Reports API](https://developer.greenlake.hpe.com/_bundle/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/@v2/public-reports-v2.yaml)

## Reports

Reference documentation for reporting operations.

### List report definitions

 - [GET /consumption-analytics/v2/reports](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v2/public-reports-v2/reports/reports-v2-list.md): List the report definitions that are available.

### Generate report from definition

 - [POST /consumption-analytics/v2/reports/execute](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v2/public-reports-v2/reports/reports-v2-gen-by-def.md): Generates the report based on report definition provided in the request body.

### Generate report for saved definition

 - [POST /consumption-analytics/v2/reports/{id}/execute](https://developer.greenlake.hpe.com/docs/greenlake/services/consumption-analytics/public/openapi/consumption-analytics-latest/v2/public-reports-v2/reports/reports-v2-gen-by-id.md): Executes a report for a saved definition; specify the date range in the request body.

