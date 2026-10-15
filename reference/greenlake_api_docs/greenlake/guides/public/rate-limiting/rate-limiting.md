---
title: "Rate limiting"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/guides/public/rate-limiting/rate-limiting.md"
scraped_at: "2026-06-07T06:13:20.878803+00:00Z"
---

# Rate limiting

GreenLake cloud applies rate limits on API requests to ensure system stability, prevent abuse, and maintain service performance for all users.

Unless otherwise noted, rate limits are applied per personal API client. Exceeding these limits may result in your requests being temporarily rejected with a `429 (Too Many Requests)` HTTP status code.

## Best practices

- Implement retry logic with exponential backoff in your applications to handle rate limit errors gracefully
- Cache frequently accessed data to reduce the number of API calls
- Batch operations when possible instead of making multiple individual requests


## Rate limit headers

GreenLake APIs include rate limit information in response headers to help you manage request rates effectively. These headers provide visibility into your current rate limit status:

| Response Header | Description |
|  --- | --- |
| `ratelimit-limit` | The maximum number of requests allowed in the current time window. |
| `ratelimit-remaining` | The number of requests remaining before hitting the rate limit. |
| `rateLimit-reset` | The time in seconds until the rate limit window resets. |


### Example response headers


```bash
HTTP/1.1 200 Ok
Content-Type: application/json
ratelimit-limit: 100
ratelimit-remaining: 0
rateLimit-reset: 48
```

In this example, the client has reached their rate limit (0 remaining requests) and will need to wait 48 seconds before the quota resets.