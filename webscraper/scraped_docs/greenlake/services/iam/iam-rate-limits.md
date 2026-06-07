---
title: "IAM API Rate Limits | HPE GreenLake"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/iam/iam-rate-limits.md"
scraped_at: "2026-06-07T05:45:54.705849+00:00Z"
---

# Rate Limits for IAM APIs

## Overview

HPE GreenLake Cloud Platform's Identity and Access Management (IAM) service enforces rate limits on API requests to ensure system stability, prevent abuse, and maintain service performance for all users. This document outlines the current rate limits for various IAM operations.

Unless otherwise noted, rate limits are applied independently per HPE subject principal (authenticated user or service account). Exceeding these limits may result in your requests being temporarily rejected with a `429 (Too Many Requests)` HTTP status code.

## Best Practices

- Implement retry logic with exponential backoff in your applications to handle rate limit errors gracefully
- Cache frequently accessed data to reduce the number of API calls
- Batch operations when possible instead of making multiple individual requests


## Rate Limit Headers

IAM APIs typically include rate limit information in response headers to help clients manage their request rates effectively. These headers provide visibility into your current rate limit status:

| Response Header | Description |
|  --- | --- |
| `X-RateLimit-Limit` | The maximum number of requests allowed in the current time window |
| `X-RateLimit-Remaining` | The number of requests remaining before hitting the rate limit |
| `X-RateLimit-Reset` | The time in seconds until the rate limit window resets |


### Example Response Headers


```http
HTTP/1.1 200 Ok
Content-Type: application/json
X-RateLimit-Limit: 100
X-Ratelimit-Remaining: 0
X-Ratelimit-Reset: 48
```

In this example, the client has reached their rate limit (0 remaining requests) and will need to wait 48 seconds before the quota resets.

## API-Specific Rate Limits

This section details the specific rate limits for different IAM API endpoints.

### Organization API Rate Limits

| Description | HTTP Method and Path | Limit |
|  --- | --- | --- |
| Add an organization | POST `/organizations/v1alpha1/organizations` | 1 request per second |
| List organizations | GET `/organizations/v1alpha1/organizations` | 5 requests per minute |
| Retrieve organization by ID | GET `/organizations/v1alpha1/organizations/{orgId}` | 100 requests per minute |
| Update an organization | PATCH `/organizations/v1alpha1/organizations/{orgId}` | 1 request per second |


### User Management API Rate Limits

| Description | HTTP Method and Path | Limit |
|  --- | --- | --- |
| Invite user to organization | POST `/organizations/v1alpha1/users/invite-user` | 1 request per second |
| Returns supported methods | OPTIONS `/organizations/v1alpha1/users/invite-user` | 100 requests per minute |


### Workspace API Rate Limits

| Description | HTTP Method and Path | Limit |
|  --- | --- | --- |
| Create a workspace linked to an organization | POST `/organizations/v1alpha1/workspaces` | 1 request per second |
| List workspaces | GET `/organizations/v1alpha1/workspaces` | 5 requests per minute |
| Update a workspace | PATCH `/organizations/v1alpha1/workspaces/{id}` | 1 request per second |
| Get a workspace | GET `/organizations/v1alpha1/workspaces/{id}` | 20 requests per minute |


## Feedback

We continuously improve our documentation and services based on your feedback. If you have suggestions regarding these rate limits or documentation, please submit feedback through the HPE GreenLake portal feedback mechanism.